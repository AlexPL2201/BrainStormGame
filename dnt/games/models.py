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

    @property
    def players_count(self):
        return sum([lobby.players_count for lobby in self.lobbies.all()])


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
        # return len(self.players)
        players = self.players
        total_players = 0
        for _ in players.all():
            total_players += 1

        return total_players

    @property
    def get_average_level(self):
        players = self.players
        total_level = 0
        total_players = 0
        for player in players.all():
            total_level += player.level
            total_players += 1

        return int(total_level / total_players)


class Game(models.Model):

    types = TYPES

    type = models.CharField(max_length=16, choices=types, default=types[0])

    @property
    def players(self):
        return self.players.select_related()