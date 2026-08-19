"""Delete stored contact submissions past the retention limit (privacy, D11).

Run on a schedule (e.g. daily) so personal data is not retained indefinitely.
The retention window is ``settings.CONTACT_SUBMISSION_RETENTION_DAYS``.
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.contrib.forms.models import FormSubmission


class Command(BaseCommand):
    """Prune contact form submissions older than the configured retention."""

    help = "Delete stored contact submissions older than the retention limit."

    def add_arguments(self, parser) -> None:
        """Add an optional ``--days`` override and a ``--dry-run`` flag."""
        parser.add_argument(
            "--days",
            type=int,
            default=None,
            help="Override the retention window (defaults to the settings value).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report how many rows would be deleted without deleting them.",
        )

    def handle(self, *args, **options) -> None:
        """Delete (or count, when dry-run) submissions older than the cutoff."""
        days = options["days"]
        if days is None:
            days = getattr(settings, "CONTACT_SUBMISSION_RETENTION_DAYS", 365)
        cutoff = timezone.now() - timedelta(days=days)

        stale = FormSubmission.objects.filter(submit_time__lt=cutoff)
        count = stale.count()
        if options["dry_run"]:
            self.stdout.write(f"[dry-run] {count} submission(s) older than {days} days.")
            return

        stale.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {count} submission(s) older than {days} days.")
        )
