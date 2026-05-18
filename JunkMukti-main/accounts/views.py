from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import EmailOTP
import random
import os
import requests
from django.utils import timezone
from datetime import timedelta

def send_otp_email_brevo(to_email, username, otp):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": os.getenv("BREVO_API_KEY"),
        "content-type": "application/json"
    }

    payload = {
        "sender": {
            "name": "Waste2Wealth",
            "email": os.getenv("EMAIL_FROM")
        },
        "to": [
            {
                "email": to_email,
                "name": username
            }
        ],
        "subject": "Your Waste2Wealth OTP Verification Code",
        "htmlContent": f"""
            <h2>Waste2Wealth OTP Verification</h2>
            <p>Hello <b>{username}</b>,</p>
            <p>Your OTP is:</p>
            <h1>{otp}</h1>
            <p>This OTP is valid for 10 minutes.</p>
            <p>If you didn’t request this, ignore the email.</p>
            <br>
            <p>♻️ Waste2Wealth Team</p>
        """
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.status_code


EMAIL_ENABLED = os.getenv("EMAIL_ENABLED") == "True"

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        otp = str(random.randint(100000, 999999))

        expires_at = timezone.now() + timedelta(minutes=10)

        EmailOTP.objects.update_or_create(
             email=email,
             defaults={
                'otp': otp,
                'expires_at': expires_at
             }
        )

        if EMAIL_ENABLED:
            status = send_otp_email_brevo(email, username, otp)
            if status not in [200, 201, 202]:
                messages.error(
                    request,
                    "Unable to send OTP email right now. Please try again later."
                )
                return redirect("signup")
        else:
            print("OTP for", email, "is:", otp)

        request.session['signup_username'] = username
        request.session['signup_email'] = email
        request.session['signup_password'] = password

        return redirect('verify_otp')

    return render(request, "accounts/signup.html")


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('home')

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        print("ENTERED OTP:", entered_otp)

        username = request.session.get('signup_username')
        email = request.session.get('signup_email')
        password = request.session.get('signup_password')

        print("SESSION DATA:", username, email, password)

        if not all([username, email, password]):
            print("❌ SESSION LOST")
            messages.error(request, "Session expired. Please sign up again.")
            return redirect('signup')

        try:
            record = EmailOTP.objects.get(email=email)
            print("DB OTP:", record.otp)

            if record.is_expired():
                print("❌ OTP EXPIRED")
                return redirect('signup')

            if record.otp == entered_otp:
                print("✅ OTP MATCHED")

                try:
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )
                    print("✅ USER CREATED:", user.username)

                except Exception as e:
                    print("❌ USER CREATION FAILED:", e)
                    messages.error(request, "User creation failed.")
                    return redirect('signup')

                record.delete()
                request.session.flush()

                return redirect('login')

        except Exception as e:
            print("❌ VERIFY OTP ERROR:", e)

    return render(request, "accounts/verify_otp.html")


