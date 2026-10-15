import os
from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_initial_admin(apps, schema_editor):
    CustomUser = apps.get_model('homepage', 'CustomUser')
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@makitest.local')
    password = os.environ.get('ADMIN_PASSWORD', 'MakitestAdmin2026!')

    if not CustomUser.objects.filter(username=username).exists():
        admin_user = CustomUser(
            username=username,
            email=email,
            password=make_password(password),
            role='admin',
            authorized=True,
            is_staff=True,
            is_superuser=True,
        )
        admin_user.save()


def remove_initial_admin(apps, schema_editor):
    CustomUser = apps.get_model('homepage', 'CustomUser')
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    CustomUser.objects.filter(username=username).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0004_customuser_authorized'),
    ]

    operations = [
        migrations.RunPython(create_initial_admin, reverse_code=remove_initial_admin),
    ]
