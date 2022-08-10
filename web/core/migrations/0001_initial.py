# Generated by Django 4.0.6 on 2022-07-11 20:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='Engine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Двигатель',
                'verbose_name_plural': 'Двигатели',
            },
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('is_visible', models.BooleanField()),
            ],
            options={
                'verbose_name': 'Марка',
                'verbose_name_plural': 'Марки',
            },
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('price', models.FloatField()),
                ('body', models.CharField(max_length=255)),
                ('is_visible', models.BooleanField()),
                ('mark', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.mark')),
            ],
            options={
                'verbose_name': 'Марка автомобиля',
                'verbose_name_plural': 'Марки автомобиля',
            },
        ),
        migrations.CreateModel(
            name='Transmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Трансмиссия',
                'verbose_name_plural': 'Трансмиссии',
            },
        ),
        migrations.CreateModel(
            name='Wd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'Привод',
                'verbose_name_plural': 'Приводы',
            },
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('image', models.URLField()),
                ('special', models.TextField()),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.model')),
            ],
            options={
                'verbose_name': 'Набор',
                'verbose_name_plural': 'Наборы',
            },
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('set_id', models.IntegerField()),
                ('image', models.URLField()),
                ('price', models.FloatField()),
                ('expenditure', models.CharField(max_length=255)),
                ('city_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.city')),
                ('engine_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.engine')),
                ('mark_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.mark')),
                ('transmission_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.transmission')),
                ('wd_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.wd')),
            ],
            options={
                'verbose_name': 'Автомобиль',
                'verbose_name_plural': 'Автомобили',
            },
        ),
        migrations.CreateModel(
            name='BotUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(unique=True)),
                ('first_name', models.CharField(max_length=255)),
                ('phone', models.BigIntegerField()),
                ('username', models.CharField(max_length=255)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.city')),
            ],
            options={
                'verbose_name': 'Пользователь бота',
                'verbose_name_plural': 'Пользователи бота',
            },
        ),
    ]