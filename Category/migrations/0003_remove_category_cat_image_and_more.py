# Generated by Django 5.2.3 on 2025-06-22 11:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Category', '0002_alter_category_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='cat_image',
        ),
        migrations.RemoveField(
            model_name='category',
            name='description',
        ),
    ]
