from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse  # ADD THIS IMPORT!
try:
    from ratelimit.decorators import ratelimit
except ImportError:
    def ratelimit(*args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

from .forms import SignupForm


@ratelimit(key="ip", rate="5/m", block=True)
def signup(request):
    """Enhanced signup view with email verification option"""
    
    if request.user.is_authenticated:
        messages.info(request, "You're already logged in!")
        return redirect("/")

    if request.method == "POST":
        form = SignupForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = True  # Set to False if using email verification
                user.save()
                
                # Auto-login (if not using email verification)
                login(request, user)
                
                # Send welcome email (optional)
                send_welcome_email(user)
                
                messages.success(
                    request,
                    f"ðŸŽ‰ Welcome to Scholarify, {user.first_name}! Your account is ready."
                )
                
                # Redirect to home
                next_url = request.GET.get("next") or "/"
                if not url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    next_url = "/"
                return redirect(next_url)
                
            except Exception as e:
                messages.error(
                    request,
                    f"Registration failed: {str(e)}. Please try again."
                )
                # Keep form data for correction
                return render(request, "accounts/signup.html", {"form": form})
        else:
            # Collect all form errors
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{field.title()}: {error}")
            
            if error_messages:
                messages.error(request, " ".join(error_messages[:3]))  # Show first 3 errors
            else:
                messages.error(request, "Please correct the errors below.")
    
    else:
        form = SignupForm()
    
    return render(request, "accounts/signup.html", {
        "form": form,
        "title": "Join Scholarify - Scholarships & Opportunities"
    })


def send_welcome_email(user):
    """Send welcome email to new user"""
    try:
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            return
        subject = "Welcome to Scholarify! ðŸŽ“"
        message = f"""
Hello {user.first_name},

Welcome to Scholarify! We're excited to have you join our community.

With your account, you can:
â€¢ Browse thousands of scholarships
â€¢ Apply for opportunities worldwide
â€¢ Save your favorite listings
â€¢ Get personalized recommendations

Start exploring: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}

Best regards,
The Scholarify Team
        """
        
        send_mail(
            subject,
            message.strip(),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )
    except Exception as e:
        # Log but don't crash if email fails
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to send welcome email to {user.email}: {e}")


def send_verification_email(request, user):
    """Send email verification link (optional feature)"""
    try:
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_url = request.build_absolute_uri(
            reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        
        subject = "Verify your Scholarify account"
        html_message = render_to_string('accounts/verification_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        
        send_mail(
            subject,
            'Please verify your email address.',  # Plain text version
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to send verification email: {e}")

