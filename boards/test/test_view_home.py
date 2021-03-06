from django.test import TestCase
from django.urls import resolve
from ..views import BoardListView


class HomeTests(TestCase):
    def test_home_url_resolve_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func.view_class, BoardListView)