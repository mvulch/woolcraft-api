from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.utils import timezone

from orders.models import Cart


class Command(BaseCommand):
    help = "Deletes anonymous carts whose session has expired or no longer exists."

    def handle(self, *args, **options):
        valid_session_keys = set(
            Session.objects.filter(expire_date__gt=timezone.now()).values_list('session_key', flat=True)
        )
        abandoned_carts = Cart.objects.filter(user__isnull=True).exclude(
            session_key__isnull=True
        ).exclude(session_key='').exclude(session_key__in=valid_session_keys)

        count = abandoned_carts.count()
        abandoned_carts.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted {count} abandoned anonymous cart(s)."))
