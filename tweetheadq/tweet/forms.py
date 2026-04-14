from django import forms
from .models import Tweet, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# ===============================
# 📝 TWEET FORM
# ===============================
class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ['photo', 'text']


# ===============================
# 👤 USER REGISTRATION FORM
# ===============================
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    # ✅ Username validation
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        return username

    # 🔥 ADD THIS (important)
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")

        return email


# ===============================
# 💬 COMMENT FORM
# ===============================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']