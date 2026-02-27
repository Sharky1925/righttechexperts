from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed initial database records (placeholder).'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('seed_database is scaffolded only. Port app/seed.py logic in Phase 1.'))
