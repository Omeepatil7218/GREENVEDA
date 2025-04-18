# Generated by Django 5.1.4 on 2025-01-16 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vedaapp', '0005_alter_purchasemaster_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='features/')),
            ],
        ),
    ]
