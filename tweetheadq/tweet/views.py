from django.shortcuts import render, get_object_or_404, redirect
from .models import Tweet, Like, Comment
from .forms import TweetForm, UserRegistrationForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse


def index(request):
    return render(request, 'tweet/index.html')


def tweet_list(request):
    tweets = Tweet.objects.all().order_by("-created_at")

    liked_tweet_ids = []
    if request.user.is_authenticated:
        liked_tweet_ids = Like.objects.filter(user=request.user)\
                                      .values_list('tweet_id', flat=True)

    return render(request, 'tweet/tweet_list.html', {
        'tweets': tweets,
        'liked_tweet_ids': liked_tweet_ids
    })


@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()

    return render(request, 'tweet/tweet_form.html', {'form': form})


@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)

    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)

    return render(request, 'tweet/tweet_form.html', {'form': form})


@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)

    if request.method == 'POST':
        tweet.delete()
        return redirect('tweet_list')

    return render(request, 'tweet/tweet_confirm_delete.html', {'tweet': tweet})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def user_tweets(request, username):
    user_obj = get_object_or_404(User, username=username)
    tweets = Tweet.objects.filter(user=user_obj).order_by("-created_at")

    liked_tweet_ids = []
    if request.user.is_authenticated:
        liked_tweet_ids = Like.objects.filter(user=request.user)\
                                      .values_list('tweet_id', flat=True)

    return render(request, 'tweet/tweet_list.html', {
        'tweets': tweets,
        'profile_user': user_obj,
        'liked_tweet_ids': liked_tweet_ids
    })


@login_required
@require_POST
def toggle_like(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        tweet=tweet
    )

    if not created:
        like.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def add_comment(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.tweet = tweet
        comment.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user and request.user != comment.tweet.user:
        return redirect('tweet_list')  # block unauthorized

    comment.delete()

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        return redirect('tweet_list')  # block unauthorized

    new_text = request.POST.get('text', '').strip()

    if new_text:
        comment.text = new_text
        comment.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))

def search_users(request):
    query = request.GET.get('q', '')
    
    users = User.objects.filter(username__icontains=query)[:10]
    
    results = list(users.values('id', 'username'))
    
    return JsonResponse({'results': results})