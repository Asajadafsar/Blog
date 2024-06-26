# Generated by Django 5.0.4 on 2024-05-08 06:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0007_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='post_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sign.blogpost'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tag',
            name='user_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='sign.user'),
            preserve_default=False,
        ),
    ]
