# Generated by Django 4.1 on 2022-11-24 19:01

import core.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_alter_setentry_status_agreements'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agreements',
            options={'verbose_name': 'Соглашение', 'verbose_name_plural': 'Соглашения'},
        ),
        migrations.AddField(
            model_name='agreements',
            name='distributor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='core.distributor', verbose_name='Дистрибьютор'),
        ),
        migrations.AlterField(
            model_name='adminentryfiles',
            name='act',
            field=models.FileField(blank=True, default=None, storage=core.models.AdminFileStorage(), upload_to='files/admin', verbose_name='Акт'),
        ),
        migrations.AlterField(
            model_name='adminentryfiles',
            name='agreement',
            field=models.FileField(blank=True, default=None, storage=core.models.AdminFileStorage(), upload_to='files/admin', verbose_name='Соглашение'),
        ),
        migrations.AlterField(
            model_name='adminentryfiles',
            name='bill',
            field=models.FileField(blank=True, default=None, storage=core.models.AdminFileStorage(), upload_to='files/admin', verbose_name='Счёт'),
        ),
        migrations.AlterField(
            model_name='distributorentryfiles',
            name='act',
            field=models.FileField(blank=True, default=None, storage=core.models.DistributorFileStorage(), upload_to='files/distributor', verbose_name='Акт'),
        ),
        migrations.AlterField(
            model_name='distributorentryfiles',
            name='agreement',
            field=models.FileField(blank=True, default=None, storage=core.models.DistributorFileStorage(), upload_to='files/distributor', verbose_name='Соглашение'),
        ),
        migrations.AlterField(
            model_name='distributorentryfiles',
            name='bill',
            field=models.FileField(blank=True, default=None, storage=core.models.DistributorFileStorage(), upload_to='files/distributor', verbose_name='Счёт'),
        ),
    ]