from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,TemplateView
from .models import Post
from .forms import EmailPostForm,CommentForm,SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy,reverse
from django.contrib.postgres.search import TrigramSimilarity


class HomeView(TemplateView):
    template_name="blog/base.html"

def post_list(request, tag_slug=None,date=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        print(request.POST.get('tag_slug'))
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    
    if date :
        post_list = post_list.filter(publish__date=date)
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer get the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results
        posts = paginator.page(paginator.num_pages)
    return render(
    request,
    'blog/post/list.html',
    {
    'posts': posts,
    'tag': tag,
    }
    )

def post_detail(request, year,month,day,post):
    post = get_object_or_404(
    Post,
    publish__year=year,
    publish__month=month,
    publish__day=day,
    slug=post,
    status=Post.Status.PUBLISHED
    )

    # Form for users to comment
    form = CommentForm()
    if request.method == "POST":
        form =post_comment(request.POST,post)
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    

    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
    tags__in=post_tags_ids
    ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
    same_tags=Count('tags')
    ).order_by('-same_tags', '-publish')[:4]


    return render(
    request,
    'blog/post/detail.html',
    {'post': post,
     'comments': comments,
    'form': form,
    'similar_posts': similar_posts
    }
    )


def post_comment(data, post):
    
    # A comment was posted
    form = CommentForm(data=data)
    if form.is_valid():
        # Create a Comment object without saving it to the database

        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
        form = CommentForm()
    return form
    

def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(
    Post,
    id=post_id,
    status=Post.Status.PUBLISHED
    )
    sent = False
    if request.method == "POST":
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
            post.get_absolute_url()
            )
            subject = (
            f"{cd['name']} ({cd['email']}) "
            f"recommends you read {post.title}"
            )
            message = (
            f"Read {post.title} at {post_url}\n\n"
            f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
            subject=subject,
            message=message,
            from_email=cd['email'],
            recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()
    return render(
    request,
    'blog/post/share.html',
    {
    'post': post,
    'form': form,
    'sent': sent
    }
    )


def post_search(request):
    query = request.GET.get('query').strip()

    if not query:
        return post_list(request)
    
    results = (
        Post.published.annotate(
            similarity=TrigramSimilarity('title', query),
        )
        .filter(similarity__gt=0.1)
        .order_by('-similarity')
    )
            
    return render(
        request,
        'blog/post/search.html',
        {
        'query': query,
        'results': results
        }
    )
