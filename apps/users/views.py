"""
Vues de l'application users — Authentification, 2FA, gestion des comptes.
"""

import random
import string
from datetime import timedelta

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings as django_settings

from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Utilisateur, ParametresApplication, Direction, MODULES_DISPONIBLES
from .serializers import ConnexionSerializer


def journaliser(request, type_action, description, objet_type='', objet_id='', issue='SUCCES'):
    try:
        from apps.dashboard.models import JournalAudit
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        JournalAudit.objects.create(
            utilisateur      = request.user if request.user.is_authenticated else None,
            identifiant_user = request.user.identifiant if request.user.is_authenticated else 'anonyme',
            profil_user      = request.user.profil if request.user.is_authenticated else '',
            type_action      = type_action,
            description      = description,
            objet_type       = objet_type,
            objet_id         = str(objet_id),
            adresse_ip       = ip or None,
            terminal         = request.META.get('HTTP_USER_AGENT', '')[:255],
            issue            = issue,
        )
    except Exception:
        pass


class ConnexionView(TokenObtainPairView):
    serializer_class = ConnexionSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            payload = getattr(serializer, '_2fa_payload', None)
            if payload:
                return Response(payload, status=400)
            raise

        return Response(serializer.validated_data)


# ---------------------------------------------------------------
# DOUBLE AUTHENTIFICATION
# ---------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def verifier_2fa(request):
    """
    Étape 2 de la connexion : vérification du code 2FA.
    Reçoit l'identifiant et le code, retourne le token JWT si valide.
    """
    identifiant = request.data.get('identifiant', '')
    code        = request.data.get('code', '')

    try:
        user = Utilisateur.objects.get(identifiant=identifiant)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Code invalide.'}, status=400)

    if not user.code_2fa or not user.code_2fa_expiration:
        return Response({'detail': 'Aucun code en attente.'}, status=400)

    if timezone.now() > user.code_2fa_expiration:
        return Response({'detail': 'Code expiré. Veuillez vous reconnecter.'}, status=400)

    if user.code_2fa != code:
        return Response({'detail': 'Code incorrect.'}, status=400)

    # Effacer le code
    user.code_2fa            = ''
    user.code_2fa_expiration = None
    user.tentatives_connexion = 0
    user.save()

    # Générer le token JWT
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    refresh['nom']    = user.nom
    refresh['prenom'] = user.prenom
    refresh['profil'] = user.profil
    refresh['modules'] = user.get_modules()

    journaliser(request, 'CONNEXION', f"Connexion 2FA réussie : {user.identifiant}")

    return Response({
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
        'mdp_expire': user.mdp_expire,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def renvoyer_code_2fa(request):
    """Renvoie un nouveau code 2FA à l'utilisateur."""
    identifiant = request.data.get('identifiant', '')
    try:
        user = Utilisateur.objects.get(identifiant=identifiant, is_active=True)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    if not user.email:
        return Response({'detail': 'Aucun email configuré pour ce compte.'}, status=400)

    _envoyer_code_2fa(user)
    return Response({'detail': 'Code renvoyé.'})


def _envoyer_code_2fa(user):
    """Génère et envoie un code 2FA par email."""
    code = ''.join(random.choices(string.digits, k=6))
    user.code_2fa            = code
    user.code_2fa_expiration = timezone.now() + timedelta(minutes=10)
    user.save()

    params = ParametresApplication.get()
    texte  = params.texte_email_2fa.replace('{code}', code)
    email_exp = params.email_expediteur or django_settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject  = f'Code de vérification — {params.nom_application}',
            message  = texte,
            from_email = email_exp,
            recipient_list = [user.email],
            fail_silently  = True,
        )
    except Exception:
        import logging
        logging.exception("Erreur lors de l'envoi de l'email 2FA (views._envoyer_code_2fa)")


# ---------------------------------------------------------------
# MOT DE PASSE
# ---------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changer_mot_de_passe(request):
    """L'utilisateur change son propre mot de passe."""
    ancien = request.data.get('ancien_mdp', '')
    nouveau = request.data.get('nouveau_mdp', '')
    confirmation = request.data.get('confirmation', '')

    if not request.user.check_password(ancien):
        return Response({'detail': 'Ancien mot de passe incorrect.'}, status=400)

    if nouveau != confirmation:
        return Response({'detail': 'Les deux mots de passe ne correspondent pas.'}, status=400)

    if len(nouveau) < 12:
        return Response({'detail': 'Le mot de passe doit contenir au moins 12 caractères.'}, status=400)

    request.user.set_password(nouveau)
    request.user.date_derniere_mdp  = timezone.now()
    request.user.alerte_mdp_envoyee = False
    request.user.save()

    journaliser(request, 'MODIF_COMPTE', 'Changement de mot de passe')
    return Response({'detail': 'Mot de passe modifié avec succès.'})


# ---------------------------------------------------------------
# PARAMÈTRES APPLICATION
# ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_parametres_publics(request):
    """Paramètres publics nécessaires avant connexion (logo, couleurs, textes)."""
    p = ParametresApplication.get()
    logo_url = request.build_absolute_uri(p.logo.url) if p.logo else None
    fond_url = request.build_absolute_uri(p.image_fond_login.url) if p.image_fond_login else None
    return Response({
        'nom_application':   p.nom_application,
        'slogan':            p.slogan,
        'texte_pied_page':   p.texte_pied_page,
        'couleur_principale': p.couleur_principale,
        'couleur_accent':    p.couleur_accent,
        'couleur_danger':    p.couleur_danger,
        'logo_url':          logo_url,
        'image_fond_url':    fond_url,
        'timeout_inactivite': p.timeout_inactivite,
        'double_auth_active': p.double_auth_active,
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def parametres_application(request):
    """Lecture et modification des paramètres. ADMIN uniquement pour la modification."""
    p = ParametresApplication.get()

    if request.method == 'GET':
        logo_url = request.build_absolute_uri(p.logo.url) if p.logo else None
        fond_url = request.build_absolute_uri(p.image_fond_login.url) if p.image_fond_login else None
        return Response({
            'nom_application':    p.nom_application,
            'slogan':             p.slogan,
            'texte_pied_page':    p.texte_pied_page,
            'couleur_principale': p.couleur_principale,
            'couleur_accent':     p.couleur_accent,
            'couleur_danger':     p.couleur_danger,
            'logo_url':           logo_url,
            'image_fond_url':     fond_url,
            'timeout_inactivite': p.timeout_inactivite,
            'duree_validite_mdp': p.duree_validite_mdp,
            'tentatives_max':     p.tentatives_max,
            'double_auth_active': p.double_auth_active,
            'email_expediteur':   p.email_expediteur,
            'texte_email_2fa':    p.texte_email_2fa,
        })

    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)

    champs_texte = ['nom_application', 'slogan', 'texte_pied_page',
                    'couleur_principale', 'couleur_accent', 'couleur_danger',
                    'email_expediteur', 'texte_email_2fa']
    for c in champs_texte:
        if c in request.data:
            setattr(p, c, request.data[c])

    champs_int = ['timeout_inactivite', 'duree_validite_mdp', 'tentatives_max']
    for c in champs_int:
        if c in request.data:
            setattr(p, c, int(request.data[c]))

    if 'double_auth_active' in request.data:
        p.double_auth_active = request.data['double_auth_active'] in [True, 'true', '1']

    if 'logo' in request.FILES:
        p.logo = request.FILES['logo']

    if 'image_fond_login' in request.FILES:
        p.image_fond_login = request.FILES['image_fond_login']

    # Supprimer le logo si demandé
    if request.data.get('supprimer_logo') in [True, 'true', '1']:
        if p.logo:
            p.logo.delete(save=False)
        p.logo = None
    # Supprimer l'image de fond si demandée
    if request.data.get('supprimer_fond') in [True, 'true', '1']:
        if p.image_fond_login:
            p.image_fond_login.delete(save=False)
        p.image_fond_login = None
    # Enregistrer les modifications apportées aux paramètres
    p.save()
    journaliser(request, 'MODIF_COMPTE', 'Paramètres de l\'application modifiés', 'parametres', 1)
    return Response({'detail': 'Paramètres enregistrés.'})


# ---------------------------------------------------------------
# GESTION DES DIRECTIONS
# ---------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_directions(request):
    if request.method == 'GET':
        dirs = Direction.objects.filter(active=True).values('id', 'nom', 'sigle', 'description', 'ordre')
        return Response(list(dirs))

    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)

    nom = request.data.get('nom', '').strip()
    if not nom:
        return Response({'detail': 'Le nom est obligatoire.'}, status=400)

    d = Direction.objects.create(
        nom         = nom,
        sigle       = request.data.get('sigle', '').strip(),
        description = request.data.get('description', '').strip(),
        ordre       = request.data.get('ordre', 0),
    )
    return Response({'detail': 'Direction créée.', 'id': d.id}, status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def modifier_direction(request, pk):
    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)

    try:
        d = Direction.objects.get(pk=pk)
    except Direction.DoesNotExist:
        return Response({'detail': 'Direction introuvable.'}, status=404)

    if request.method == 'DELETE':
        d.active = False
        d.save()
        return Response({'detail': 'Direction désactivée.'})

    for c in ['nom', 'sigle', 'description', 'ordre']:
        if c in request.data:
            setattr(d, c, request.data[c])
    d.save()
    return Response({'detail': 'Direction mise à jour.'})


# ---------------------------------------------------------------
# GESTION DES UTILISATEURS
# ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_utilisateurs(request):
    if request.user.profil not in ['DG', 'ADMIN']:
        return Response({'detail': 'Accès refusé.'}, status=403)

    users = Utilisateur.objects.select_related('direction').all().order_by('nom')
    data = [{
        'id':             u.id,
        'identifiant':    u.identifiant,
        'nom':            u.nom,
        'prenom':         u.prenom,
        'profil':         u.profil,
        'email':          u.email,
        'fonction':       u.fonction,
        'direction_id':   u.direction_id,
        'direction_nom':  u.direction.nom if u.direction else '',
        'is_active':      u.is_active,
        'modules_actifs': u.modules_actifs,
        'double_auth_active': u.double_auth_active,
        'double_auth_desactive_admin': u.double_auth_desactive_admin,
        'date_creation':  u.date_creation.strftime('%d/%m/%Y'),
        'mdp_expire':     u.mdp_expire,
        'est_verrouille': u.est_verrouille,
    } for u in users]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_utilisateur(request):
    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)

    data = request.data
    for c in ['identifiant', 'nom', 'prenom', 'profil', 'password']:
        if not data.get(c):
            return Response({'detail': f'Le champ {c} est obligatoire.'}, status=400)

    if Utilisateur.objects.filter(identifiant=data['identifiant']).exists():
        return Response({'detail': 'Cet identifiant existe déjà.'}, status=400)

    # Validation: destinataire doit avoir une direction
    if data['profil'] == 'DEST' and not data.get('direction_id'):
        return Response({'detail': 'La direction est obligatoire pour un Destinataire.'}, status=400)

    direction = None
    if data.get('direction_id'):
        try:
            direction = Direction.objects.get(pk=data['direction_id'])
        except Direction.DoesNotExist:
            return Response({'detail': 'Direction introuvable.'}, status=404)

    user = Utilisateur.objects.create_user(
        identifiant    = data['identifiant'],
        password       = data['password'],
        nom            = data['nom'],
        prenom         = data['prenom'],
        profil         = data['profil'],
        direction      = direction,
        fonction       = data.get('fonction', ''),
        email          = data.get('email', ''),
        modules_actifs = data.get('modules_actifs', []),
        date_derniere_mdp = timezone.now(),
    )

    journaliser(request, 'CREATION_COMPTE', f"Compte créé : {user.identifiant} ({user.profil})", 'compte', user.id)
    return Response({'detail': 'Compte créé.', 'id': user.id}, status=201)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_utilisateur(request, pk):
    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)

    try:
        user = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    data = request.data
    for c in ['nom', 'prenom', 'email', 'fonction']:
        if c in data:
            setattr(user, c, data[c])

    if 'direction_id' in data:
        if data['direction_id']:
            try:
                user.direction = Direction.objects.get(pk=data['direction_id'])
            except Direction.DoesNotExist:
                pass
        else:
            user.direction = None

    if 'modules_actifs' in data:
        user.modules_actifs = data['modules_actifs']

    if 'double_auth_active' in data:
        user.double_auth_active = bool(data['double_auth_active'])

    if 'double_auth_desactive_admin' in data:
        user.double_auth_desactive_admin = bool(data['double_auth_desactive_admin'])

    if 'password' in data and data['password']:
        user.set_password(data['password'])
        user.date_derniere_mdp = timezone.now()

    user.save()
    journaliser(request, 'MODIF_COMPTE', f"Compte modifié : {user.identifiant}", 'compte', user.id)
    return Response({'detail': 'Compte mis à jour.'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def basculer_compte(request, pk):
    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)

    try:
        user = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    if user.pk == request.user.pk:
        return Response({'detail': 'Impossible de désactiver votre propre compte.'}, status=400)

    user.is_active = not user.is_active
    user.save()

    etat = 'activé' if user.is_active else 'désactivé'
    journaliser(request, 'CREATION_COMPTE' if user.is_active else 'DESACT_COMPTE',
                f"Compte {etat} : {user.identifiant}", 'compte', user.id)
    return Response({'detail': f'Compte {etat}.', 'is_active': user.is_active})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def deverrouiller_compte(request, pk):
    """Déverrouille un compte après trop de tentatives."""
    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)
    try:
        user = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    user.tentatives_connexion = 0
    user.verrouille_jusqu     = None
    user.save()
    journaliser(request, 'MODIF_COMPTE', f"Compte déverrouillé : {user.identifiant}", 'compte', user.id)
    return Response({'detail': 'Compte déverrouillé.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supervision(request):
    if request.user.profil != 'ADMIN':
        return Response({'detail': 'Réservé à l\'Administrateur.'}, status=403)

    from apps.courriers.models import Courrier
    from apps.archives.models import ArchiveHistorique
    from django.db.models import Count

    total_users  = Utilisateur.objects.count()
    actifs       = Utilisateur.objects.filter(is_active=True).count()
    inactifs     = Utilisateur.objects.filter(is_active=False).count()
    verrouilles  = sum(1 for u in Utilisateur.objects.all() if u.est_verrouille)
    par_profil   = list(Utilisateur.objects.values('profil').annotate(total=Count('id')))

    try:
        from apps.dashboard.models import JournalAudit
        total_audit   = JournalAudit.objects.count()
        acces_refuses = JournalAudit.objects.filter(issue='REFUS').count()
        derniere      = JournalAudit.objects.order_by('-horodatage_utc').first()
        derniere_str  = derniere.horodatage_utc.strftime('%d/%m/%Y %H:%M') if derniere else 'Aucune'
    except Exception:
        total_audit = acces_refuses = 0
        derniere_str = 'N/A'

    import django
    return Response({
        'utilisateurs': {
            'total': total_users, 'actifs': actifs,
            'inactifs': inactifs, 'verrouilles': verrouilles,
            'par_profil': par_profil,
        },
        'volumetrie': {
            'total_courriers': Courrier.objects.count(),
            'total_archives':  ArchiveHistorique.objects.count(),
        },
        'audit': {
            'total_entrees':   total_audit,
            'acces_refuses':   acces_refuses,
            'derniere_action': derniere_str,
        },
        'systeme': {
            'django_version': django.get_version(),
            'heure_serveur':  timezone.now().strftime('%d/%m/%Y %H:%M:%S'),
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mon_profil(request):
    """Retourne le profil complet avec les modules actifs de l'utilisateur connecté."""
    user = request.user
    return Response({
        'identifiant': user.identifiant,
        'nom':         user.nom,
        'prenom':      user.prenom,
        'profil':      user.profil,
        'modules':     user.get_modules(),
        'direction':   user.direction.nom if user.direction else '',
        'mdp_expire':  user.mdp_expire,
    })
