# Generated by Django 4.1 on 2022-11-24 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_alter_setentry_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='setentry',
            name='is_shipped',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='setentry',
            name='status',
            field=models.CharField(choices=[('new', 'Ожидает'), ('road', 'В пути'), ('client', 'Передан клиенту'), ('payment', 'Ожидает оплаты'), ('complete', 'Закрыто')], default='new', max_length=32, verbose_name='Статус заявки'),
        ),
    ]
