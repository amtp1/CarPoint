# Generated by Django 4.0.6 on 2022-07-16 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_set_image_alter_set_model_settransmission_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='car',
            old_name='city_id',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='car',
            old_name='engine_id',
            new_name='engine',
        ),
        migrations.RenameField(
            model_name='car',
            old_name='mark_id',
            new_name='mark',
        ),
        migrations.RenameField(
            model_name='car',
            old_name='set_id',
            new_name='set',
        ),
        migrations.RenameField(
            model_name='car',
            old_name='transmission_id',
            new_name='transmission',
        ),
        migrations.RenameField(
            model_name='car',
            old_name='wd_id',
            new_name='wd',
        ),
        migrations.AlterField(
            model_name='set',
            name='special',
            field=models.TextField(verbose_name='Конфигурации'),
        ),
    ]