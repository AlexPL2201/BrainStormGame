# Generated by Django 4.1.7 on 2023-03-25 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0005_game_categories_game_highest_level_game_lowest_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='type',
            field=models.CharField(choices=[('normal', 'Обычная'), ('ranked', 'Ранговая'), ('theme', 'Тематическая'), ('friend', 'Дружеская')], default=('normal', 'Обычная'), max_length=16),
        ),
        migrations.AlterField(
            model_name='lobby',
            name='type',
            field=models.CharField(choices=[('normal', 'Обычная'), ('ranked', 'Ранговая'), ('theme', 'Тематическая'), ('friend', 'Дружеская')], default=('normal', 'Обычная'), max_length=16),
        ),
        migrations.AlterField(
            model_name='queue',
            name='type',
            field=models.CharField(choices=[('normal', 'Обычная'), ('ranked', 'Ранговая'), ('theme', 'Тематическая'), ('friend', 'Дружеская')], default=('normal', 'Обычная'), max_length=16),
        ),
    ]
