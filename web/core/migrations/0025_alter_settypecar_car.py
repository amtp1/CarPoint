# Generated by Django 4.1 on 2022-10-10 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_alter_setcolor_car'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settypecar',
            name='car',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.car', verbose_name='Автомобиль'),
        ),
    ]
