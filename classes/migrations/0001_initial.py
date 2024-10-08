# Generated by Django 5.0.6 on 2024-08-18 10:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('teachers', '0001_initial'),
        ('years', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('short_name', models.CharField(max_length=50)),
                ('prefect_id', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('master', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='teachers.teacher')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='years.year')),
            ],
            options={
                'verbose_name_plural': 'school classes',
            },
        ),
    ]
