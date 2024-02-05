from django.contrib.auth.hashers import make_password
from django.db import migrations
from django.utils import timezone
import os


def create_superuser(apps, schema_editor):
    model_user = apps.get_model('auth', 'User')
    superuser = model_user(
        is_active=True,
        is_superuser=True,
        is_staff=True,
        username=os.environ.get("SUPERUSER", "admin"),
        password=make_password(os.environ.get("SUPERUSER_PASSWORD", "admin")),
        email='dev@dev.ru',
        last_login=timezone.now(),
    )
    superuser.save()


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]