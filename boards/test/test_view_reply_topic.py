from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Board, Post, Topic
from ..views import reply_topic


class ReplyTopicTestCase(TestCase):
    """
    Base test case to be used in all `reply_topic` views tests
    """
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.username = 'john'
        self.password = '123'

        user = User.objects.create_user(username=self.username, email='john@deo.com', password=self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    pass


class ReplyTopicTests(ReplyTopicTestCase):
    pass


class SuccessfulRplyTopicTests(ReplyTopicTestCase):
    def test_redirection(self):
        url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        topic_posts_url = '{url}?page=1#2'.format(url=url)
        self.assertRedirects(self.response, topic_posts_url)


class InvalidRplyTopicTests(ReplyTopicTestCase):
    pass