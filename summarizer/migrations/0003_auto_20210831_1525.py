# Generated by Django 3.2.6 on 2021-08-31 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('summarizer', '0002_auto_20210831_1448'),
    ]

    operations = [
        migrations.AddField(
            model_name='summarizer',
            name='file_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='summarizer',
            name='source_data',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
