from django.shortcuts import render, get_object_or_404, redirect
from .models import Tweet, Like, Comment, Notification
from .forms import TweetForm, UserRegistrationForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings

# ✅ NEW IMPORTS
import resend
import os

# ✅ INIT RESEND
resend.api_key = os.environ.get("RESEND_API_KEY")


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


# ===============================
# ❤️ LIKE SYSTEM
# ===============================
@login_required
@require_POST
def toggle_like(request, tweet_id):
    tweet = Tweet.objects.get(id=tweet_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        tweet=tweet
    )

    if created:
        if tweet.user != request.user:

            Notification.objects.get_or_create(
                sender=request.user,
                receiver=tweet.user,
                tweet=tweet,
                notification_type='like'
            )

            try:
                resend.Emails.send({
    "from": "TweetHQ <onboarding@resend.dev>",
    "to": tweet.user.email,
    "subject": "❤️ Someone liked your tweet",
    "html": f"""
    <div style="font-family: Arial, sans-serif; background:#f9f9f9; padding:30px;">

        <div style="max-width:500px; margin:auto; background:white; padding:20px; border-radius:10px;">

            <h2 style="margin-top:0; color:#222;">
                ❤️ New Like on TweetHQ
            </h2>

            <p style="font-size:15px; color:#555;">
                <strong>{request.user.username}</strong> liked your tweet.
            </p>

            <div style="
                background:#f1f3f5;
                padding:12px;
                border-radius:8px;
                margin:20px 0;
                font-style:italic;
                color:#333;
            ">
                "{tweet.text}"
            </div>

            <div style="text-align:center; margin:25px 0;">
                <a href="https://tweet-app-teal.vercel.app/"
                   style="
                       display:inline-block;
                       padding:12px 20px;
                       background:#007bff;
                       color:white;
                       text-decoration:none;
                       border-radius:6px;
                       font-weight:bold;
                   ">
                   View Tweet
                </a>
            </div>

            <hr style="border:none; border-top:1px solid #eee;">

            <p style="font-size:12px; color:#888; text-align:center; margin-top:15px;">
                You’re receiving this because someone interacted with your tweet.
                <br><br>
                — <strong>TweetHQ</strong>
            </p>

        </div>

    </div>
    """
})
            except Exception as e:
                print("Resend Like Error:", e)

    else:
        like.delete()

    return redirect('tweet_list')


# ===============================
# 💬 COMMENT SYSTEM
# ===============================
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

        if tweet.user != request.user:

            Notification.objects.get_or_create(
                sender=request.user,
                receiver=tweet.user,
                tweet=tweet,
                notification_type='comment'
            )

            try:
                resend.Emails.send({
        "from": "TweetHQ <onboarding@resend.dev>",
        "to": tweet.user.email,
        "subject": "💬 New comment on your tweet",
        "html": f"""
            <div style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color:#333;">New Comment 💬</h2>

                <p>
                    <strong>{request.user.username}</strong> commented on your tweet.
                </p>

                <div style="
                    background:#f5f5f5;
                    padding:10px;
                    border-radius:8px;
                    margin:15px 0;
                ">
                    <p><b>Your Tweet:</b> "{tweet.text}"</p>
                </div>

                <a href="https://tweet-app-teal.vercel.app/"
                style="
                    display:inline-block;
                    padding:10px 15px;
                    background:#28a745;
                    color:white;
                    text-decoration:none;
                    border-radius:5px;
                ">
                View Conversation
                </a>

                <p style="margin-top:20px; font-size:12px; color:gray;">
                    — TweetHQ Team
                </p>
            </div>
        """
})
            except Exception as e:
                print("Resend Comment Error:", e)

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user and request.user != comment.tweet.user:
        return redirect('tweet_list')

    comment.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user:
        return redirect('tweet_list')

    new_text = request.POST.get('text', '').strip()

    if new_text:
        comment.text = new_text
        comment.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


# ===============================
# 🔍 SEARCH USERS
# ===============================
def search_users(request):
    query = request.GET.get('q', '')

    users = User.objects.filter(username__icontains=query)[:10]

    results = list(users.values('id', 'username'))

    return JsonResponse({'results': results})