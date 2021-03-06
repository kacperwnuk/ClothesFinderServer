# Generated by Django 3.0.4 on 2020-03-17 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ClothesSearchApp', '0004_change_of_structure'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeColors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cloth_type', models.CharField(choices=[('T-SHIRT', 'T-Shirty'), ('SHIRT', 'Koszule'), ('PANTS', 'Spodnie'), ('SHORTS', 'Szorty'), ('JACKET', 'Marynarki'), ('SWEATER', 'Swetry')], max_length=10)),
                ('colors', models.ManyToManyField(to='ClothesSearchApp.Color')),
            ],
        ),
    ]
