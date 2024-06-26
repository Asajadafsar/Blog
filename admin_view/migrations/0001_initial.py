# Generated by Django 5.0.4 on 2024-05-10 23:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminLogs',
            fields=[
                ('log_id', models.AutoField(primary_key=True, serialize=False)),
                ('action', models.CharField(max_length=100)),
                ('action_date', models.DateTimeField()),
                ('ip_address', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
