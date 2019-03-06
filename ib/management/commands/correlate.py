from django.core.management.base import BaseCommand
from ib.IB import check_correlate


class Command(BaseCommand):
    help = 'ib data correlate'

    def handle(self, *args, **options):
        check_correlate()