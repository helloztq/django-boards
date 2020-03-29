from django.contrib.auth.models import User
from .models import Board, Topic, Post

user = User.objects.first()
board = Board.objects.get(name='Python')

for i in range(10000):
    subject = 'Topic test #{}'.format(i)
    topic = Topic.objects.create(subject=subject, board=board, starter=user)
    Post.objects.create(message='Lorem ipsum...', topic=topic, created_by=user)



