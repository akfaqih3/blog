from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(
    required=False,
    widget=forms.Textarea
    )

class CommentForm(forms.ModelForm):
    name = forms.CharField(max_length=255,required=True)
    email = forms.EmailField(widget=forms.EmailInput,required=True)
    body = forms.CharField(widget=forms.Textarea,required=True)
    name.widget.attrs={"class":"form-control"}
    email.widget.attrs={"class":"form-control"}
    body.widget.attrs={"class":"form-control","cols":30,"rows":10}
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']

class SearchForm(forms.Form):
    query = forms.CharField()