from django.shortcuts import render, get_object_or_404, redirect
from .models import Tweet, Like, Comment, Notification
from .forms import TweetForm, UserRegistrationForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
import os

# ===============================
# ✅ SAFE RESEND SETUP
# ===============================
try:
    import resend
except ImportError:
    resend = None

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")

if resend and RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
else:
    print("⚠️ Resend not configured")


# ===============================
# 🏠 HOME
# ===============================
def index(request):
    return render(request, 'tweet/index.html')


# ===============================
# 📰 TWEET LIST
# ===============================
def tweet_list(request):
    tweets = Tweet.objects.select_related('user')\
                          .prefetch_related('likes', 'comments')\
                          .order_by("-created_at")

    liked_tweet_ids = []
    if request.user.is_authenticated:
        liked_tweet_ids = Like.objects.filter(user=request.user)\
                                      .values_list('tweet_id', flat=True)

    return render(request, 'tweet/tweet_list.html', {
        'tweets': tweets,
        'liked_tweet_ids': liked_tweet_ids
    })


# ===============================
# ➕ CREATE TWEET
# ===============================
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


# ===============================
# ✏️ EDIT TWEET
# ===============================
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


# ===============================
# ❌ DELETE TWEET
# ===============================
@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)

    if request.method == 'POST':
        tweet.delete()
        return redirect('tweet_list')

    return render(request, 'tweet/tweet_confirm_delete.html', {'tweet': tweet})


# ===============================
# 👤 REGISTER
# ===============================
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


# ===============================
# 👤 USER TWEETS
# ===============================
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
# 📧 EMAIL HELPER (NEW)
# ===============================
def send_notification_email(subject, html, to_email):
    try:
        if resend and RESEND_API_KEY:
            resend.Emails.send({
                "from": "TweetHQ <onboarding@resend.dev>",
                "to": to_email,
                "subject": subject,
                "html": html
            })
        else:
            print("⚠️ Email skipped (Resend not configured)")
    except Exception as e:
        print("Email Error:", e)


# ===============================
# ❤️ LIKE SYSTEM
# ===============================
@login_required
@require_POST
def toggle_like(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)

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

            to_email = tweet.user.email or "tweet.nikhilporject@gmail.com"

            send_notification_email(
                subject="❤️ Someone liked your tweet",
                to_email=to_email,
                html=f"""
                <div style="font-family: Arial; padding: 20px;">
                    <h2>❤️ New Like</h2>
                    <p><b>{request.user.username}</b> liked your tweet.</p>
                    <p>"{tweet.text}"</p>
                </div>
                """
            )

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

            to_email = tweet.user.email or "tweet.nikhilporject@gmail.com"

            send_notification_email(
                subject="💬 New comment on your tweet",
                to_email=to_email,
                html=f"""
                <div style="font-family: Arial; padding: 20px;">
                    <h2>💬 New Comment</h2>
                    <p><b>{request.user.username}</b> commented:</p>
                    <p>"{comment.text}"</p>
                    <hr>
                    <p><b>Your Tweet:</b> "{tweet.text}"</p>
                </div>
                """
            )

    return redirect(request.META.get('HTTP_REFERER', '/'))


# ===============================
# ❌ DELETE COMMENT
# ===============================
@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.user and request.user != comment.tweet.user:
        return redirect('tweet_list')

    comment.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ===============================
# ✏️ EDIT COMMENT
# ===============================
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
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'results': []})

    users = User.objects.filter(username__icontains=query)[:10]

    results = list(users.values('id', 'username'))

    return JsonResponse({'results': results})