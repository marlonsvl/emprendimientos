# Generated manually to fix migration ancestry

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gastronomia', '0001_initial'), # This establishes the missing ancestor link!
    ]

    operations = [
        migrations.AddField(
            model_name='establecimiento',
            name='medio_pago',
            field=models.CharField(default='No especificado', max_length=200),
        ),
    ]