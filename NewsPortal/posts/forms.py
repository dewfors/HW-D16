from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'article_text',
            'author',
            'category',
        ]

    def clean(self):
        cleaned_data = super().clean()
        article_text = cleaned_data.get("article_text")
        if article_text is not None and len(article_text) < 40:
            raise ValidationError({
                "article_text": "Описание слишком короткое."
            })

        title = cleaned_data.get("title")
        if title == article_text:
            raise ValidationError(
                "Описание не должно быть идентичным названию."
            )
        return cleaned_data
