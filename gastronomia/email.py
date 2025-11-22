# Create this file: gastronomia/email.py

from django.contrib.auth.tokens import default_token_generator
from templated_mail.mail import BaseEmailMessage
from djoser import utils
from djoser.conf import settings as djoser_settings
from django.conf import settings
from django.template.loader import render_to_string


class ActivationEmail(BaseEmailMessage):
    template_name = "email/activation_email_body.html"
    
    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        
        # Generate the activation URL components
        uid = utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        
        # Build the complete context
        context.update({
            "user": user,
            "uid": uid,
            "token": token,
            "url": djoser_settings.ACTIVATION_URL.format(uid=uid, token=token),
            "domain": djoser_settings.DOMAIN,
            "site_name": djoser_settings.SITE_NAME,
            "protocol": "https" if getattr(settings, 'USE_HTTPS', False) else "http"
        })
        
        return context

    def get_subject(self):
        return f"Activate your {djoser_settings.SITE_NAME} account"

    def send(self, to, *args, **kwargs):
        # Get the context
        context = self.get_context_data()
        
        # Render both HTML and text versions
        html_content = render_to_string(self.template_name, context)
        text_content = f"""
Welcome to {context['site_name']}!

Hi {context['user'].get_full_name() or context['user'].username},

Thank you for joining our community! We're excited to have you on board.

To complete your registration and start exploring all our features, please activate your account by visiting this link:

{context['protocol']}://{context['domain']}/{context['url']}

This activation link will expire in 24 hours for your security. If you didn't create an account with us, please ignore this email.

Welcome aboard!
The {context['site_name']} Team
"""
        
        # Send the email with both versions
        from django.core.mail import EmailMultiAlternatives
        
        subject = self.get_subject()
        from_email = settings.DEFAULT_FROM_EMAIL
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to if isinstance(to, list) else [to]
        )
        email.attach_alternative(html_content, "text/html")
        
        return email.send()


class PasswordResetEmail(BaseEmailMessage):
    template_name = "email/password_reset_email_body.html"
    
    def get_context_data(self):
        context = super().get_context_data()
        user = context.get("user")
        
        # Generate the password reset URL components
        uid = utils.encode_uid(user.pk)
        token = default_token_generator.make_token(user)
        
        # Build the complete context
        context.update({
            "user": user,
            "uid": uid,
            "token": token,
            "url": djoser_settings.PASSWORD_RESET_CONFIRM_URL.format(uid=uid, token=token),
            "domain": djoser_settings.DOMAIN,
            "site_name": djoser_settings.SITE_NAME,
            "protocol": "https" if getattr(settings, 'USE_HTTPS', False) else "http"
        })
        
        return context

    def get_subject(self):
        return f"Reset your {djoser_settings.SITE_NAME} password"

    def send(self, to, *args, **kwargs):
        # Get the context
        context = self.get_context_data()
        
        # Render both HTML and text versions
        html_content = render_to_string(self.template_name, context)
        text_content = f"""
Password Reset for {context['site_name']}

Hi {context['user'].get_full_name() or context['user'].username},

We received a request to reset your password for your {context['site_name']} account.

If you made this request, visit this link to reset your password:

{context['protocol']}://{context['domain']}/{context['url']}

This password reset link will expire in 1 hour for your security. If you didn't request this reset, please ignore this email and your password will remain unchanged.

Best regards,
The {context['site_name']} Team
"""
        
        # Send the email with both versions
        from django.core.mail import EmailMultiAlternatives
        
        subject = self.get_subject()
        from_email = settings.DEFAULT_FROM_EMAIL
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to if isinstance(to, list) else [to]
        )
        email.attach_alternative(html_content, "text/html")
        
        return email.send()