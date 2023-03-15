from django.db import models

TYPES = (
        ('normal', 'Обычная'),
    )


class Queue(models.Model):

    types = TYPES

    type = models.CharField(max_length=16, choices=types, default=types[0])
    lowest_level = models.SmallIntegerField()
    highest_level = models.SmallIntegerField()

    @property
    def lobbies(self):
        return self.lobbies.select_related()


class Lobby(models.Model):

    objects = None
    types = TYPES

    type = models.CharField(max_length=16, choices=types, default=types[0])
    queue = models.ForeignKey(Queue, on_delete=models.SET_NULL, related_name='lobbies', null=True, blank=True)

    @property
    def players(self):
        return self.players.select_related()

    @property
    def players_count(self):
        return len(self.players)

    def get_average_level(self):
        players = self.players
        total_level = 0
        for player in players:
            total_level += player.level

        return int(total_level / len(players))


class Game(models.Model):

    types = TYPES

    type = models.CharField(max_length=16, choices=types, default=types[0])

    @property
    def players(self):
        return self.players.select_related()