# Generated by Django 4.1.7 on 2024-07-14 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MindMap',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(default='')),
                ('doc_id', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'mind_map',
            },
        ),
    ]
