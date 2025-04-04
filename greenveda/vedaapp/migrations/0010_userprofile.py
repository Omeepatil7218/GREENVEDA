# Generated by Django 5.1.1 on 2025-03-26 11:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vedaapp', '0009_alter_categorymaster_options_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='profile_images/')),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('language', models.CharField(blank=True, choices=[('Hindi', 'Hindi'), ('English', 'English'), ('Punjabi', 'Punjabi'), ('Bengali', 'Bengali'), ('Tamil', 'Tamil'), ('Telugu', 'Telugu'), ('Marathi', 'Marathi'), ('Gujarati', 'Gujarati')], max_length=20, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=100, null=True)),
                ('pincode', models.CharField(blank=True, max_length=10, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
