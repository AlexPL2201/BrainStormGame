from django.core.management.base import BaseCommand
from games.models import Lobby, Queue, Game


class Command(BaseCommand):

    def handle(self, *args, **options):
        Lobby.objects.all().delete()
        Queue.objects.all().delete()
        Game.objects.all().delete()
