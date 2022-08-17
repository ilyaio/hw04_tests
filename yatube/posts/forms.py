from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {'group': 'Группа', 'text': 'Сообщение'}
        help_texts = {'group': 'Выберите группу', 'text': 'Введите сообщение'}
        fields = ["group", "text"]
        # fields = ["group", "text", "image"]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        labels = {'text': 'Комментарий'}
        help_texts = {'text': 'Оставьте комментарий'}
        fields = ("text",)
