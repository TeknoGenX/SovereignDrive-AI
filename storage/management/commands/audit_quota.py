from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Sum
from storage.models import File, UserProfile

class Command(BaseCommand):
    help = 'Audit and synchronize storage quota for all users.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Audit specific user by username')
        parser.add_argument('--fix', action='store_true', help='Actually update the storage_used values')

    def handle(self, *args, **options):
        username = options['user']
        fix = options['fix']

        if username:
            users = User.objects.filter(username=username)
        else:
            users = User.objects.all()

        self.stdout.write(self.style.MIGRATE_HEADING(f"Starting Storage Audit... (Fix Mode: {fix})"))

        for user in users:
            # 1. Calculate actual size from non-trashed files
            actual_usage = File.objects.filter(owner=user, is_trashed=False).aggregate(total=Sum('size'))['total'] or 0
            
            # 2. Get current profile usage
            profile, created = UserProfile.objects.get_or_create(user=user)
            current_usage = profile.storage_used

            if actual_usage != current_usage:
                diff = actual_usage - current_usage
                status = self.style.WARNING("MISMATCH")
                
                self.stdout.write(
                    f"User: {user.username} | DB: {current_usage} | Actual: {actual_usage} | Diff: {diff} | {status}"
                )

                if fix:
                    profile.storage_used = actual_usage
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(f"  Fixed storage_used for {user.username}"))
            else:
                self.stdout.write(f"User: {user.username} | Usage: {actual_usage} | {self.style.SUCCESS('OK')}")

        self.stdout.write(self.style.SUCCESS("Audit complete."))
