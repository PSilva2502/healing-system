from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consultas', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='atendimento',
            name='sintomas',
            field=models.TextField(blank=True, default='', verbose_name='Sintomas relatados'),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='locais_dor',
            field=models.JSONField(blank=True, default=list, verbose_name='Locais de dor'),
        ),
        migrations.AddField(
            model_name='atendimento',
            name='resultado_exame',
            field=models.TextField(blank=True, default='', verbose_name='Resultado de exames'),
        ),
    ]
