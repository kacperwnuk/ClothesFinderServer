# Generated by Django 3.0.4 on 2020-04-06 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ClothesSearchApp', '0014_add_occasion_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='occasion',
            name='key',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
