# Generated by Django 3.2.7 on 2021-09-07 14:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('django_celery_results', '0010_remove_duplicate_indices'),
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskManualRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('app', models.CharField(max_length=64)),
                ('arg', models.CharField(blank=True, max_length=64)),
                ('remark', models.TextField(blank=True)),
                ('create_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='TaskDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('remark', models.CharField(blank=True, max_length=255)),
                ('arg', models.CharField(blank=True, max_length=64)),
                ('create_date', models.DateTimeField()),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.periodictask')),
                ('taskid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='django_celery_results.taskresult')),
            ],
        ),
    ]
