"""
Vues de l'application users — GED ESCEP-Niger SaaS.
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

from .models import Utilisateur, Direction, MODULES_DISPONIBLES
from .serializers import ConnexionSerializer


def journaliser(request, type_action, description, objet_type='', objet_id='', issue='SUCCES'):
    try:
        from apps.dashboard.models import JournalAudit
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        JournalAudit.objects.create(
            organisation     = getattr(request, 'tenant', None),
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
                # Journaliser tentative 2FA
                return Response(payload, status=400)
            # Journaliser échec connexion
            try:
                from apps.dashboard.models import journaliser, TypeAction
                identifiant = request.data.get('identifiant', 'inconnu')
                journaliser(request, TypeAction.CONNEXION,
                           f"Échec connexion : {identifiant}",
                           issue='ECHEC')
            except Exception:
                pass
            raise

        # Connexion réussie — journaliser
        try:
            from apps.dashboard.models import journaliser, TypeAction
            identifiant = request.data.get('identifiant', '')
            from apps.users.models import Utilisateur
            user = Utilisateur.objects.get(identifiant=identifiant)
            # Simuler request.user pour journaliser
            request.user = user
            request.tenant = user.organisation  # ← AJOUTER

            journaliser(request, TypeAction.CONNEXION,
                       f"Connexion réussie : {identifiant}")
        except Exception:
            pass

        return Response(serializer.validated_data)
@api_view(['POST'])
@permission_classes([AllowAny])
def verifier_2fa(request):
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

    user.code_2fa            = ''
    user.code_2fa_expiration = None
    user.tentatives_connexion = 0
    user.save()

    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    if user.organisation:
        refresh['tenant_id']   = user.organisation.id
        refresh['tenant_code'] = user.organisation.code_tenant
    refresh['nom']     = user.nom
    refresh['prenom']  = user.prenom
    refresh['profil']  = user.profil
    refresh['modules'] = user.get_modules()

    journaliser(request, 'CONNEXION', f"Connexion 2FA : {user.identifiant}")

    return Response({
        'access':     str(refresh.access_token),
        'refresh':    str(refresh),
        'mdp_expire': user.mdp_expire,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def renvoyer_code_2fa(request):
    identifiant = request.data.get('identifiant', '')
    try:
        user = Utilisateur.objects.get(identifiant=identifiant, is_active=True)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    if not user.email:
        return Response({'detail': 'Aucun email configuré.'}, status=400)

    code = ''.join(random.choices(string.digits, k=6))
    user.code_2fa            = code
    user.code_2fa_expiration = timezone.now() + timedelta(minutes=10)
    user.save()

    org = user.organisation
    from_email = (org.email_expediteur if org else '') or django_settings.DEFAULT_FROM_EMAIL
    texte = (org.texte_email_2fa if org else 'Code: {code}').replace('{code}', code)

    try:
        send_mail(
            subject        = f"Code — {org.nom if org else 'GED'}",
            message        = texte,
            from_email     = from_email,
            recipient_list = [user.email],
            fail_silently  = True,
        )
    except Exception:
        pass

    return Response({'detail': 'Code renvoyé.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changer_mot_de_passe(request):
    ancien       = request.data.get('ancien_mdp', '')
    nouveau      = request.data.get('nouveau_mdp', '')
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
# PARAMÈTRES APPLICATION — maintenant délégué à l'organisation
# ---------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def get_parametres_publics(request):
    """Redirigé vers l'endpoint organisation (rétrocompatibilité)."""
    from apps.organisations.views import parametres_publics_organisation
    return parametres_publics_organisation(request)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def parametres_application(request):
    """Délégué à l'organisation courante."""
    from apps.organisations.views import mes_parametres_organisation
    return mes_parametres_organisation(request)


# ---------------------------------------------------------------
# DIRECTIONS
# ---------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def liste_directions(request):
    org = request.tenant
    if request.method == 'GET':
        qs = Direction.objects.filter(active=True)
        if org:
            qs = qs.filter(organisation=org)
        return Response(list(qs.values('id', 'nom', 'sigle', 'description', 'ordre')))

    if request.user.profil != 'ADMIN':
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)

    nom = request.data.get('nom', '').strip()
    if not nom:
        return Response({'detail': 'Le nom est obligatoire.'}, status=400)

    d = Direction.objects.create(
        organisation = org,
        nom          = nom,
        sigle        = request.data.get('sigle', '').strip(),
        description  = request.data.get('description', '').strip(),
        ordre        = request.data.get('ordre', 0),
    )
    return Response({'detail': 'Direction créée.', 'id': d.id}, status=201)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def modifier_direction(request, pk):
    if request.user.profil != 'ADMIN':
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)

    try:
        d = Direction.objects.get(pk=pk)
    except Direction.DoesNotExist:
        return Response({'detail': 'Direction introuvable.'}, status=404)

    # Vérifier que la direction appartient à la même organisation
    if request.tenant and d.organisation_id != request.tenant.id:
        return Response({'detail': 'Accès refusé.'}, status=403)

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
# UTILISATEURS
# ---------------------------------------------------------------
import re

def valider_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_utilisateurs(request):
    if request.user.profil not in ['DG', 'ADMIN']:
        return Response({'detail': 'Accès refusé.'}, status=403)

    org = request.tenant
    qs  = Utilisateur.objects.select_related('direction').all().order_by('nom')
    if org:
        qs = qs.filter(organisation=org)

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
        'double_auth_active':          u.double_auth_active,
        'double_auth_desactive_admin': u.double_auth_desactive_admin,
        'date_creation':  u.date_creation.strftime('%d/%m/%Y'),
        'mdp_expire':     u.mdp_expire,
        'est_verrouille': u.est_verrouille,
    } for u in qs]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_utilisateur(request):
    if request.user.profil != 'ADMIN':
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)

    data = request.data
    for c in ['identifiant', 'nom', 'prenom', 'profil', 'password']:
        if not data.get(c):
            return Response({'detail': f'Le champ {c} est obligatoire.'}, status=400)

    # Validation email obligatoire
    email = data.get('email', '').strip()
    if not email:
        return Response({'detail': 'L\'email est obligatoire.'}, status=400)
    if not valider_email(email):
        return Response({'detail': 'Email invalide. Format attendu : exemple@domaine.com'}, status=400)

    org = request.tenant

    if Utilisateur.objects.filter(identifiant=data['identifiant'], organisation=org).exists():
        return Response({'detail': 'Cet identifiant existe déjà dans votre organisation.'}, status=400)

    if data['profil'] == 'DEST' and not data.get('direction_id'):
        return Response({'detail': 'La direction est obligatoire pour un Destinataire.'}, status=400)

    direction = None
    if data.get('direction_id'):
        try:
            direction = Direction.objects.get(pk=data['direction_id'])
        except Direction.DoesNotExist:
            return Response({'detail': 'Direction introuvable.'}, status=404)

    user = Utilisateur.objects.create_user(
        identifiant       = data['identifiant'],
        password          = data['password'],
        organisation      = org,
        nom               = data['nom'],
        prenom            = data['prenom'],
        profil            = data['profil'],
        direction         = direction,
        fonction          = data.get('fonction', ''),
        email             = email,
        modules_actifs    = data.get('modules_actifs', []),
        date_derniere_mdp = timezone.now(),
    )

    journaliser(request, 'CREATION_COMPTE', f"Compte créé : {user.identifiant} ({user.profil})", 'compte', user.id)
    return Response({'detail': 'Compte créé.', 'id': user.id}, status=201)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def modifier_utilisateur(request, pk):
    if request.user.profil != 'ADMIN':
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)

    try:
        user = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    if request.tenant and user.organisation_id != request.tenant.id:
        return Response({'detail': 'Accès refusé.'}, status=403)

    data = request.data

    # Validation email si fourni
    if 'email' in data:
        email = data['email'].strip()
        if not email:
            return Response({'detail': 'L\'email est obligatoire.'}, status=400)
        if not valider_email(email):
            return Response({'detail': 'Email invalide. Format attendu : exemple@domaine.com'}, status=400)
        user.email = email

    for c in ['nom', 'prenom', 'fonction']:
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
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)
    try:
        user = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    if request.tenant and user.organisation_id != request.tenant.id:
        return Response({'detail': 'Accès refusé.'}, status=403)
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
    if request.user.profil != 'ADMIN':
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)
    try:
        user = Utilisateur.objects.get(pk=pk)
    except Utilisateur.DoesNotExist:
        return Response({'detail': 'Utilisateur introuvable.'}, status=404)

    if request.tenant and user.organisation_id != request.tenant.id:
        return Response({'detail': 'Accès refusé.'}, status=403)

    user.tentatives_connexion = 0
    user.verrouille_jusqu     = None
    user.save()
    journaliser(request, 'MODIF_COMPTE', f"Compte déverrouillé : {user.identifiant}", 'compte', user.id)
    return Response({'detail': 'Compte déverrouillé.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def supervision(request):
    if request.user.profil != 'ADMIN':
        return Response({'detail': "Réservé à l'Administrateur."}, status=403)

    from apps.courriers.models import Courrier
    from apps.archives.models import ArchiveHistorique
    from django.db.models import Count

    org = request.tenant

    qs_users = Utilisateur.objects.filter(organisation=org) if org else Utilisateur.objects.all()
    total_users = qs_users.count()
    actifs      = qs_users.filter(is_active=True).count()
    inactifs    = qs_users.filter(is_active=False).count()
    verrouilles = sum(1 for u in qs_users if u.est_verrouille)
    par_profil  = list(qs_users.values('profil').annotate(total=Count('id')))

    qs_courriers = Courrier.objects.filter(organisation=org) if org else Courrier.objects.all()
    qs_archives  = ArchiveHistorique.objects.filter(organisation=org) if org else ArchiveHistorique.objects.all()

    try:
        from apps.dashboard.models import JournalAudit
        qs_audit = JournalAudit.objects.filter(organisation=org) if org else JournalAudit.objects.all()
        total_audit   = qs_audit.count()
        acces_refuses = qs_audit.filter(issue='REFUS').count()
        derniere      = qs_audit.order_by('-horodatage_utc').first()
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
            'total_courriers': qs_courriers.count(),
            'total_archives':  qs_archives.count(),
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
    user = request.user

    # L'ADMIN a accès à tous les modules automatiquement
    if user.profil == 'ADMIN' or user.is_superuser:
        from .models import MODULES_DISPONIBLES
        modules = [code for code, _ in MODULES_DISPONIBLES]
    else:
        modules = user.get_modules()

    return Response({
        'identifiant': user.identifiant,
        'nom':         user.nom,
        'prenom':      user.prenom,
        'profil':      user.profil,
        'modules':     modules,
        'direction':   user.direction.nom if user.direction else '',
        'mdp_expire':  user.mdp_expire,
        'workflow_type': request.user.organisation.workflow_type if request.user.organisation else 'CLASSIQUE',
    })



@api_view(['POST'])
@permission_classes([AllowAny])
def verifier_identifiant(request):
    """
    Vérifie qu'un identifiant existe dans une organisation donnée.
    Utilisé par LoginView pour confirmer le changement d'organisation.
    NE retourne pas d'informations sensibles — juste existe/n'existe pas.
    """
    identifiant = request.data.get('identifiant', '').strip()
    tenant_code = request.data.get('tenant_code', '').strip()

    if not identifiant or not tenant_code:
        return Response({'existe': False})

    try:
        Utilisateur.objects.get(
            identifiant=identifiant,
            organisation__code_tenant=tenant_code,
            is_active=True
        )
        return Response({'existe': True})
    except Utilisateur.DoesNotExist:
        return Response({'existe': False})
