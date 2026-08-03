
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organisations', '0001_initial'),  # Adapter au nom de ta dernière migration
    ]

    operations = [
        migrations.AddField(
            model_name='organisation',
            name='police',
            field=models.CharField(
                max_length=200,
                default="'Segoe UI', sans-serif",
                help_text='Police de caractères CSS'
            ),
        ),
        migrations.AddField(
            model_name='organisation',
            name='taille_texte_base',
            field=models.CharField(
                max_length=10,
                default='14px',
                help_text='Taille de base des textes (ex: 14px)'
            ),
        ),
        migrations.AddField(
            model_name='organisation',
            name='couleur_texte',
            field=models.CharField(
                max_length=7,
                default='#222222',
                help_text='Couleur du texte principal'
            ),
        ),
        migrations.AddField(
            model_name='organisation',
            name='couleur_texte_secondaire',
            field=models.CharField(
                max_length=7,
                default='#666666',
                help_text='Couleur du texte secondaire'
            ),
        ),
        migrations.AddField(
            model_name='organisation',
            name='graisse_titres',
            field=models.CharField(
                max_length=10,
                default='700',
                help_text='Graisse des titres (ex: 600, 700, 800)'
            ),
        ),
        migrations.AddField(
            model_name='organisation',
            name='rayon_bord',
            field=models.CharField(
                max_length=10,
                default='6px',
                help_text='Rayon des coins (ex: 6px, 10px)'
            ),
        ),
    ]
