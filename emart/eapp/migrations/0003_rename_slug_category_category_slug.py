# Generated by Django 3.2.5 on 2021-08-13 15:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eapp', '0002_alter_category_slug'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='slug',
            new_name='category_slug',
        ),
    ]
