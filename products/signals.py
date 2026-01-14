from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from .models import Product

User = get_user_model()


@receiver(post_save, sender=Product)
def send_new_product_email(sender, instance, created, **kwargs):
    if not created:
        return  # Only send on NEW product

    try:
        # Get recipients (exclude owner)
        print(instance.thumbnail)
        recipients = (
            User.objects
            .filter(is_active=True)
            .exclude(id=instance.user.id)
            .values_list("email", flat=True)
        )

        if not recipients:
            return

        subject = f"🔥 New Product Added: {instance.title}"

        
        current_site = Site.objects.get_current()
        domain = current_site.domain  # e.g., mynexmarket.com

        context = {
            "product": instance,
            "site_name": "My Next Market",
            "product_url": f"https://{domain}/products/{instance.slug}",
            "image_url": f"https://{domain}{instance.thumbnail.url}" if instance.thumbnail else "",
        }

        html_content = render_to_string(
            "emails/new_product.html",
            context
        )

        text_content = f"""
New product added: {instance.title}

Price: {instance.currency} {instance.price}
Location: {instance.location}

View product:
https://mynextmarket.com/products/{instance.slug}
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[],                 # empty (use BCC)
            bcc=list(recipients),  # BCC protects privacy
        )

        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

    except Exception as e:
        # NEVER break product creation
        print("❌ Failed to send new product email:", str(e))
