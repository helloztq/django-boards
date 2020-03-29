from django.test import TestCase
from ..forms import SignUpForm


class SignUpFormTest(TestCase):

    def test_from_has_fields(self):
        form = SignUpForm()
        expected = ['username', 'email', 'password1', 'passowrd2',]
        actual = list(form.fields)
        self.assertSequenceEqual(actual, expected)