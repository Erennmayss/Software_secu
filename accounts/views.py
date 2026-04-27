import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail

from .forms import SignupForm, LoginForm, ProfileForm, PasswordChangeForm
from .models import User, PasswordResetCode, HealthConstraint


# ── Inscription ──────────────────────────────────────────
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('recipes:index')

    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé.')
        return redirect('accounts:onboarding')

    return render(request, 'accounts/signup.html', {'form': form})


# ── Connexion ────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('recipes:index')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        next_url = request.GET.get('next', 'recipes:index')
        return redirect(next_url)

    return render(request, 'accounts/login.html', {'form': form})


# ── Déconnexion ──────────────────────────────────────────
@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ── Modifier le profil (API JSON pour le frontend) ───────
@login_required
def update_profile(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    data = json.loads(request.body)
    action = data.get('action')

    if action == 'profile':
        form = ProfileForm(data, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'full_name': request.user.full_name,
                'email': request.user.email,
            })
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    if action == 'password':
        form = PasswordChangeForm(request.user, data)
        if form.is_valid():
            user = request.user
            if not user.check_password(form.cleaned_data['old_password']):
                return JsonResponse({'success': False, 'error': 'old_password'}, status=400)
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)   # garde la session active
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'error': 'Action inconnue'}, status=400)


# ── Infos profil (GET) ───────────────────────────────────
@login_required
def profile_data(request):
    u = request.user
    return JsonResponse({
        'first_name': u.first_name,
        'last_name':  u.last_name,
        'email':      u.email,
        'full_name':  u.full_name,
    })


# ── Page Mot de passe oublié (HTML) ──────────────────────
def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('recipes:index')
    return render(request, 'accounts/forgot_password.html')


# ── API : Demander un code de réinitialisation (Envoi Email)
def request_reset_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Données invalides'}, status=400)

        user = User.objects.filter(email=email).first()
        if user:
            # Supprimer les anciens codes et en générer un nouveau
            PasswordResetCode.objects.filter(user=user).delete()
            reset_entry = PasswordResetCode(user=user)
            reset_entry.generate_code()
            
            # Envoi du vrai e-mail via SMTP
            send_mail(
                'Code de réinitialisation Biodelice',
                f'Bonjour {user.first_name},\n\nVoici votre code à 6 chiffres pour réinitialiser votre mot de passe : {reset_entry.code}\n\nSi vous n\'avez pas demandé cette réinitialisation, ignorez ce message.',
                'noreply@biodelice.com',
                [email],
                fail_silently=False,
            )
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# ── API : Valider le code et changer le mot de passe ─────
def confirm_reset_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            reset_entry = PasswordResetCode.objects.filter(user=user, code=data.get('code')).first()
            if reset_entry:
                user.set_password(data.get('new_password'))
                user.save()
                reset_entry.delete()
                return JsonResponse({'success': True})
                
        return JsonResponse({'success': False, 'error': 'Code invalide ou expiré.'}, status=400)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


# ── Onboarding (Choix des maladies/allergies) ────────────
@login_required
def onboarding_view(request):
    if request.method == 'POST':
        raw_constraints = request.POST.get('constraints_list', '')
        constraints_list = [c.strip().lower() for c in raw_constraints.split(',') if c.strip()]
        
        request.user.health_constraints.clear()
        for name in constraints_list:
            obj, created = HealthConstraint.objects.get_or_create(name=name)
            request.user.health_constraints.add(obj)
            
        return redirect('recipes:index')
    return render(request, 'accounts/onboarding.html')

@login_required
def settings_view(request):
    return render(request, 'settings.html')

 # accounts/views.py - Ajoute cette fonction

@login_required
def save_onboarding(request):
    if request.method == 'POST':
        user = request.user
        
        # Étape 1
        user.age = request.POST.get('age')
        user.weight = request.POST.get('weight')
        user.height = request.POST.get('height')
        user.sexe = request.POST.get('sexe')
        
        # Étape 2
        user.restrictions = request.POST.get('restrictions', '')
        
        # Étape 3
        user.aliments_a_eviter = request.POST.get('aliments_a_eviter', '')
        
        # Étape 4 - Maladies (liaison avec HealthConstraint)
        maladies = request.POST.get('maladies', '').split(',')
        user.health_constraints.clear()
        for maladie in maladies:
            if maladie:
                obj, _ = HealthConstraint.objects.get_or_create(name=maladie)
                user.health_constraints.add(obj)
        
        # Étape 5
        user.culinary_level = request.POST.get('culinary_level', '')
        
        user.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)
