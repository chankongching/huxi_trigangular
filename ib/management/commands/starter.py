from django.core.management.base import BaseCommand
from ib.IB import IBClient, subscribe_all_contracts_lob


class Command(BaseCommand):
    help = 'ib data collector'

    def handle(self, *args, **options):
        client = IBClient(1234)
        client.ready = subscribe_all_contracts_lob
        client.start()
