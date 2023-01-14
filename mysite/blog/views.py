from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_detail(request,year,month,day,post):
    post = get_object_or_404(Post,slug=post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    comments = post.comments.filter(active=True)
    new_comment = None

    comment_form = CommentForm(request.POST or None)
    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.post = post
        new_comment.save()

    return render(
        request,
        'blog/post/detail.html', 
        {
            'post' : post,
            'comments' : comments,
            'new_comment' : new_comment,
            'comment_form' : comment_form})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    
    form = EmailPostForm(request.POST or None)
    if form.is_valid():
        cd = form.cleaned_data
        post_url = request.build_absolute_uri(post.get_absolute_url())
        subject = f'{cd["name"]} recomend you read {post.title}'
        message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
        send_mail(subject,message,'admin@myblig.com',[cd['to']])
        sent = True
    return render(request,
                  'blog/post/share.html',
                  {'post':post,'form':form,'sent':sent})