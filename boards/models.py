from django.db import models
from django.contrib.auth.models import User
from django.utils.text import Truncator
from django.db import models
from django.utils.html import mark_safe
from markdown import markdown
import math

# Create your models here.


class Board(models.Model):
    name = models.CharField(max_length=10, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_post_count(self):
        print('==================Board===============')
        count = Post.objects.filter(topic__board=self).count()
        print('get_post_count', count)
        return count

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()


class Topic(models.Model):
    subject = models.CharField(max_length=255)
    last_update = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, models.deletion.SET_NULL, null=True, related_name='topics')
    starter = models.ForeignKey(User, models.deletion.SET_NULL, null=True, related_name='topics')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 5
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()

        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, models.deletion.DO_NOTHING, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, models.deletion.DO_NOTHING, related_name='posts')
    updated_by = models.ForeignKey(User, models.deletion.SET_NULL, null=True, related_name='+')

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))

