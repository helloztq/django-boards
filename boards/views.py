from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.views.generic import View, CreateView, UpdateView, ListView
from django.urls.base import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm


# Create your views here.


def home(request):
    boards = Board.objects.all()
    names = list()
    #
    # for board in boards:
    #     names.append(board.name)
    #     print("get_last_post", board.get_last_post(), board.get_post_count())
    #
    # print(names)

    return render(request, 'home.html', {'boards': boards})


class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 20)
    try:
        topics = paginator.page(page)

    except PageNotAnInteger:
        topics = paginator.page(1)
    except EmptyPage:
        topics = paginator.page(paginator.num_pages)

    # topics = board.topics.order_by('-last_update').annotate(replies=Count('posts'))

    return render(request, 'topic.html', {'board': board, 'topics': topics})


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topic.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('last_update').annotate(replies=Count('posts') - 1)
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()

    if request.method == 'POST':
        form = NewTopicForm(request.POST)

        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()

            Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )

            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()

    return render(request, 'new_topic.html', {'board': board, 'form': form})


def about(request):
    # print('pk', pk)
    return 'about'


# def post(request, username):
#     print('slug', username)
#     return HttpResponse('Hello')
def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    print("request.method", request.method)
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_update = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )
            return redirect(topic_post_url)
    else:
        form = PostForm()

    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


# class NewPostView(View):
#
#     def render(self, request):
#         return render(request, 'new_post.html', {'form': self.form})
#
#     def post(self, request):
#         self.form = PostForm(request.POST)
#         if self.form.is_valid():
#             self.form.save()
#             return redirect('post_list')
#         return self.render(request)
#
#     def get(self, request):
#         self.form = PostForm()
#         return self.render(request)

class NewPostView(CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('post_list')
    template_name = 'new_post.html'


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)


class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email')
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self, queryset=None):
        return self.request.user
