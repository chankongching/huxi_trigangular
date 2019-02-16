from django.core.management.base import BaseCommand
from ib.IB import IBClient

class Command(BaseCommand):
    help = 'ib data collector'
    def handle(self, *args, **options):
        client = IBClient()
