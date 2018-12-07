# Generated by Django 2.1.4 on 2018-12-07 05:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Annotation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('object_id', models.CharField(max_length=255)),
                ('field_id', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('lastmod', models.DateTimeField(auto_now=True)),
                ('content', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
            ],
        ),
    ]
