# Generated by Django 3.0.4 on 2020-03-10 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ClothesSearchApp', '0002_adding_img_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='clothes',
            name='type',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]