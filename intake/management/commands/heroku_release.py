from django.core import management
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = str(
        "Sets up seeds based on what environment it runs in.")

    def handle(self, *args, **kwargs):
        management.call_command('migrate')
        management.call_command('load_essential_data')
        if settings.GENERATE_DUMMY_DATA:
            management.call_command('load_mock_data')
