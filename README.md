# 🚀 TweetHQ — Social Microblogging Platform

TweetHQ is a full-stack Django-based microblogging web application that allows users to share thoughts, interact with posts, and receive real-time notifications.

Built with a focus on clean backend architecture, scalable integrations, and production deployment.

---

## ✨ Features

### 📝 Core Functionality

* Create, edit, and delete tweets
* Upload images with tweets (Cloudinary integration)
* User authentication (register, login, logout)

### ❤️ Engagement System

* Like / Unlike tweets (toggle system)
* Comment on tweets
* Edit & delete comments with proper permissions

### 🔔 Notification System

* Real-time database notifications for:

  * Likes
  * Comments
* Notification model with sender, receiver, and type tracking

### 📧 Email Notifications

* Integrated with **Resend API**
* Sends email alerts when:

  * Someone likes your tweet
  * Someone comments on your tweet
* Styled HTML emails with contextual data

### 🔍 Search

* Dynamic user search (AJAX-based)
* Case-insensitive username filtering

---

## 🛠️ Tech Stack

### Backend

* Django (Python)
* PostgreSQL (Supabase)

### Media & Storage

* Cloudinary (image hosting)

### Email Service

* Resend API (production-ready email delivery)

### Deployment

* Vercel (serverless deployment)

---

## 🧠 Key Highlights

* Designed relational models for Tweets, Likes, Comments, and Notifications
* Implemented optimized queries using `select_related` and `prefetch_related`
* Built crash-safe external integrations (Resend API with fallback handling)
* Environment-based configuration using `.env` and secure key management
* Production-ready structure with scalable architecture

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/tweethq.git
cd tweethq
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env` File

```env
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True

DATABASE_URL=your_database_url

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

RESEND_API_KEY=your_resend_key
```

---

### 5. Run Migrations

```bash
python manage.py migrate
```

---

### 6. Run Server

```bash
python manage.py runserver
```

---

## 🌐 Deployment

* Deployed on **Vercel**
* Environment variables configured via Vercel dashboard
* Uses serverless Django setup

---

## 🔐 Security Practices

* Sensitive data stored in environment variables
* `.env` excluded using `.gitignore`
* API keys and credentials rotated when exposed
* No hardcoded secrets in codebase

---

## 🚧 Future Improvements

* 🔔 Notification dropdown UI with unread badge
* Real-time updates using WebSockets
* Follow / Unfollow system
* User profile customization
* Pagination & infinite scroll

---

## 🤝 Contribution

Open to improvements and suggestions. Feel free to fork and enhance.

---

## 📌 Author

**Nikhil Kumar Mishra**

* Aspiring data-driven builder & product-focused developer
* Passionate about scalable systems and real-world problem solving

---

## ⭐ If you like this project

Give it a star ⭐ and support the journey!
