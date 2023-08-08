from django.core.management.base import BaseCommand
from packing.models import PalleteType


class Command(BaseCommand):
    help = "Creates pallete types"

    def handle(self, *args, **kwargs):
        PalleteType.objects.get_or_create(name='return')
        PalleteType.objects.get_or_create(name='warehouse')
        PalleteType.objects.get_or_create(name='chpu')
