# Generated by Django 3.1.7 on 2021-10-17 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Name')),
                ('value', models.TextField(verbose_name='Value')),
                ('category', models.CharField(default='default', max_length=128)),
                ('encrypted', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=True, verbose_name='Enabled')),
                ('comment', models.TextField(verbose_name='Comment')),
            ],
            options={
                'verbose_name': 'Setting',
                'db_table': 'settings_setting',
            },
        ),
    ]
