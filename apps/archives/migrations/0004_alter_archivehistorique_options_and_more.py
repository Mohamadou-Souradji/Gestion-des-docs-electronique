# apps/archives/migrations/0004_saas_migration.py
# Copier ce fichier dans apps/archives/migrations/

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def convertir_fonds(apps, schema_editor):
    """
    L'ancien champ fonds est un texte (ex: 'EST', 'ADMIN').
    On crée un FondsArchive pour chaque valeur unique,
    puis on relie chaque archive au bon FondsArchive.
    """
    ArchiveHistorique = apps.get_model('archives', 'ArchiveHistorique')
    FondsArchive = apps.get_model('archives', 'FondsArchive')

    # Collecter les valeurs uniques de l'ancien champ fonds (texte)
    valeurs_fonds = set()
    for archive in ArchiveHistorique.objects.all():
        valeurs_fonds.add(str(archive.fonds_ancien or 'GENERAL'))

    # Créer un FondsArchive par valeur unique
    fonds_map = {}
    for valeur in valeurs_fonds:
        fonds_obj, _ = FondsArchive.objects.get_or_create(
            code=valeur[:20],
            defaults={
                'intitule': f"Fonds {valeur}",
                'description': f"Fonds migré automatiquement depuis la valeur '{valeur}'",
            }
        )
        fonds_map[valeur] = fonds_obj

    # Lier chaque archive au bon FondsArchive
    for archive in ArchiveHistorique.objects.all():
        valeur = str(archive.fonds_ancien or 'GENERAL')
        archive.fonds = fonds_map.get(valeur)
        archive.save(update_fields=['fonds'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('archives', '0003_initial'),
        ('organisations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [

        # ─── 1. Renommer le champ fonds en fonds_ancien (pour préserver les données texte)
        migrations.RenameField(
            model_name='archivehistorique',
            old_name='fonds',
            new_name='fonds_ancien',
        ),

        # ─── 2. Renommer resume → description
        migrations.RenameField(
            model_name='archivehistorique',
            old_name='resume',
            new_name='description',
        ),

        # ─── 3. Créer le modèle FondsArchive
        migrations.CreateModel(
            name='FondsArchive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('intitule', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('organisation', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='fonds_archives',
                    to='organisations.organisation',
                )),
            ],
            options={'ordering': ['code']},
        ),

        # ─── 4. Ajouter le nouveau champ fonds (FK nullable d'abord)
        migrations.AddField(
            model_name='archivehistorique',
            name='fonds',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='documents',
                to='archives.fondsarchive',
            ),
        ),

        # ─── 5. Ajouter organisation à ArchiveHistorique
        migrations.AddField(
            model_name='archivehistorique',
            name='organisation',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='archives',
                to='organisations.organisation',
            ),
        ),

        # ─── 6. Ajouter fichier_pdf
        migrations.AddField(
            model_name='archivehistorique',
            name='fichier_pdf',
            field=models.FileField(blank=True, null=True, upload_to='archives/%Y/%m/'),
        ),

        # ─── 7. Supprimer les anciens champs inutiles
        migrations.RemoveField(model_name='archivehistorique', name='categorie'),
        migrations.RemoveField(model_name='archivehistorique', name='contenu_ocr'),
        migrations.RemoveField(model_name='archivehistorique', name='est_historique'),
        migrations.RemoveField(model_name='archivehistorique', name='expediteur'),
        migrations.RemoveField(model_name='archivehistorique', name='fichier'),
        migrations.RemoveField(model_name='archivehistorique', name='lot'),
        migrations.RemoveField(model_name='archivehistorique', name='reference_origine'),
        migrations.RemoveField(model_name='archivehistorique', name='type_document'),

        # ─── 8. Migrer les données fonds (texte → FK)
        migrations.RunPython(convertir_fonds, noop),

        # ─── 9. Maintenant rendre fonds obligatoire (non nullable)
        migrations.AlterField(
            model_name='archivehistorique',
            name='fonds',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='documents',
                to='archives.fondsarchive',
                null=True,  # garder null=True pour les archives sans fonds
            ),
        ),

        # ─── 10. Supprimer fonds_ancien maintenant qu'on a migré les données
        migrations.RemoveField(
            model_name='archivehistorique',
            name='fonds_ancien',
        ),

        # ─── 11. Modifier les autres champs pour correspondre au nouveau modèle
        migrations.AlterField(
            model_name='archivehistorique',
            name='date_document',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='archivehistorique',
            name='intitule',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='archivehistorique',
            name='mots_cles',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='archivehistorique',
            name='reference_systeme',
            field=models.CharField(blank=True, max_length=50, unique=True),
        ),

        # ─── 12. Modifier options Meta
        migrations.AlterModelOptions(
            name='archivehistorique',
            options={'ordering': ['-date_versement']},
        ),
    ]