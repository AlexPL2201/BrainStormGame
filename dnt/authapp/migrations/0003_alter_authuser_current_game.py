# Generated by Django 4.0.4 on 2023-03-17 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0004_alter_game_results'),
        ('authapp', '0002_alter_authuser_birthdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authuser',
            name='current_game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='games.game'),
        ),
    ]