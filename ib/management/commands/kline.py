from django.core.management.base import BaseCommand
from ib.IB import IBClient, subscribe_and_save_kline


class Command(BaseCommand):
    help = 'ib data kline'

    def handle(self, *args, **options):
        client = IBClient(1235)
        client.ready = subscribe_and_save_kline
        client.start()
