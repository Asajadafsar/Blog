# Generated by Django 5.0.4 on 2024-05-08 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sign', '0008_tag_post_id_tag_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=150),
        ),
    ]
