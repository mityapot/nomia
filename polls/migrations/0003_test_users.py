from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone
import json


def create_users(apps, schema_editor):
    with open('./utils/users.json') as json_file:
        data_raw = json.load(json_file)
        users = data_raw['data']

    model_user = apps.get_model('auth', 'User')
    for user in users:
        user = model_user(
            is_active=True,
            is_superuser=False,
            is_staff=False,
            username=user['username'],
            password=make_password(user['password']),
            first_name=user['first_name'],
            last_name=user['last_name'],
            email=user['email'],
            last_login=timezone.now(),
        )
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0002_superuser'),
    ]

    operations = [
        migrations.RunPython(create_users),
    ]