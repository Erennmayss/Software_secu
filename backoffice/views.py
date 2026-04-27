from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from accounts.models import FoodProduct, HealthConstraint
from .forms import FoodProductForm, HealthConstraintForm, SubstitutionRuleForm
from .models import SubstitutionRule

User = get_user_model()

staff_required = user_passes_test(lambda u: u.is_authenticated and u.is_staff)


def _base_context(active_page):
    return {'active_page': active_page}


@staff_required
def admin_dashboard(request):
    total_users = User.objects.count()
    total_recipes = FoodProduct.objects.count()
    top_recipes = FoodProduct.objects.annotate(favorites_count=Count('favorites')).order_by('-favorites_count', '-id')[:5]
    recent_recipes = FoodProduct.objects.order_by('-id')[:5]

    rules_with_user_counts = SubstitutionRule.objects.select_related('target_constraint').annotate(
        affected_users=Count('target_constraint__user', distinct=True)
    )
    daily_subs = sum(rule.affected_users for rule in rules_with_user_counts)

    constraint_counts = HealthConstraint.objects.annotate(user_count=Count('user', distinct=True)).order_by('-user_count', 'name')
    constraint_distribution = []
    for constraint in constraint_counts:
        percentage = round((constraint.user_count / total_users) * 100, 1) if total_users else 0
        constraint_distribution.append({
            'name': constraint.name,
            'percentage': percentage,
            'user_count': constraint.user_count,
            'color': constraint.color,
            'icon': constraint.icon,
        })

    context = {
        **_base_context('dashboard'),
        'total_users': total_users,
        'total_recipes': total_recipes,
        'daily_subs': daily_subs,
        'active_users': User.objects.filter(last_login__isnull=False).count(),
        'favorite_recipes': FoodProduct.objects.aggregate(total=Count('favorites'))['total'] or 0,
        'recent_recipes': recent_recipes,
        'top_recipes': top_recipes,
        'constraint_distribution': constraint_distribution,
    }
    return render(request, 'admin/dashboard.html', context)


@staff_required
def recipe_list(request):
    if request.method == 'POST':
        delete_recipe_id = request.POST.get('delete_recipe_id')
        if delete_recipe_id:
            recipe = get_object_or_404(FoodProduct, pk=delete_recipe_id)
            recipe.delete()
            messages.success(request, 'Recette supprimee avec succes.')
            query_string = request.META.get('QUERY_STRING')
            redirect_url = reverse('backoffice:recipe_list')
            if query_string:
                redirect_url = f'{redirect_url}?{query_string}'
            return redirect(redirect_url)

    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    products = FoodProduct.objects.all().order_by('-id')

    if search_query:
        products = products.filter(name__icontains=search_query)
    if category_filter:
        products = products.filter(category=category_filter)

    context = {
        **_base_context('recipes'),
        'products': products,
        'search_query': search_query,
        'category_filter': category_filter,
        'category_choices': FoodProduct.CATEGORY_CHOICES,
    }
    return render(request, 'admin/recipes_list.html', context)


@staff_required
def recipe_create(request):
    form = FoodProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Recette creee avec succes.')
        return redirect('backoffice:recipe_list')

    return render(request, 'admin/recipe_form.html', {
        **_base_context('recipe_form'),
        'form': form,
        'page_mode': 'create',
    })


@staff_required
def recipe_update(request, pk):
    recipe = get_object_or_404(FoodProduct, pk=pk)
    form = FoodProductForm(request.POST or None, request.FILES or None, instance=recipe)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Recette mise a jour avec succes.')
        return redirect('backoffice:recipe_list')

    return render(request, 'admin/recipe_form.html', {
        **_base_context('recipe_form'),
        'form': form,
        'recipe': recipe,
        'page_mode': 'edit',
    })


@staff_required
def user_list(request):
    if request.method == 'POST':
        target_id = request.POST.get('toggle_staff_user_id')
        if target_id:
            user = get_object_or_404(User, pk=target_id)
            if user.pk == request.user.pk:
                messages.error(request, 'Vous ne pouvez pas modifier votre propre role depuis cette page.')
            else:
                user.is_staff = not user.is_staff
                user.save(update_fields=['is_staff'])
                messages.success(request, 'Role utilisateur mis a jour.')
            return redirect('backoffice:user_list')

    search_query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()
    activity_filter = request.GET.get('activity', '').strip()

    users = User.objects.prefetch_related('health_constraints').all().order_by('-date_joined')
    if search_query:
        users = users.filter(email__icontains=search_query)
    if role_filter == 'admin':
        users = users.filter(is_staff=True)
    elif role_filter == 'member':
        users = users.filter(is_staff=False)

    if activity_filter == 'active':
        users = users.filter(is_active=True)
    elif activity_filter == 'inactive':
        users = users.filter(is_active=False)

    total_users = User.objects.count()
    active_count = User.objects.filter(is_active=True).count()
    active_percentage = round((active_count / total_users) * 100, 1) if total_users else 0
    common_constraint = (
        HealthConstraint.objects.annotate(user_count=Count('user'))
        .filter(user_count__gt=0)
        .order_by('-user_count', 'name')
        .first()
    )

    context = {
        **_base_context('users'),
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'activity_filter': activity_filter,
        'total_users': total_users,
        'active_percentage': active_percentage,
        'most_common_constraint': common_constraint.name if common_constraint else 'Aucune',
    }
    return render(request, 'admin/users_list.html', context)


@staff_required
def health_settings(request):
    constraint_form = HealthConstraintForm(prefix='constraint')
    rule_form = SubstitutionRuleForm(prefix='rule')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_constraint':
            constraint_form = HealthConstraintForm(request.POST, prefix='constraint')
            if constraint_form.is_valid():
                constraint_form.save()
                messages.success(request, 'Contrainte de sante ajoutee.')
                return redirect('backoffice:health_settings')

        elif action == 'delete_constraint':
            constraint = get_object_or_404(HealthConstraint, pk=request.POST.get('constraint_id'))
            constraint.delete()
            messages.success(request, 'Contrainte de sante supprimee.')
            return redirect('backoffice:health_settings')

        elif action == 'add_rule':
            rule_form = SubstitutionRuleForm(request.POST, prefix='rule')
            if rule_form.is_valid():
                rule_form.save()
                messages.success(request, 'Regle de substitution ajoutee.')
                return redirect('backoffice:health_settings')

        elif action == 'delete_rule':
            rule = get_object_or_404(SubstitutionRule, pk=request.POST.get('rule_id'))
            rule.delete()
            messages.success(request, 'Regle de substitution supprimee.')
            return redirect('backoffice:health_settings')

    diseases = HealthConstraint.objects.filter(constraint_type=HealthConstraint.TYPE_DISEASE).order_by('name')
    allergens = HealthConstraint.objects.filter(constraint_type=HealthConstraint.TYPE_ALLERGEN).order_by('name')
    rules = SubstitutionRule.objects.select_related('target_constraint').order_by('target_constraint__name', 'forbidden_ingredient')

    return render(request, 'admin/health_settings.html', {
        **_base_context('health'),
        'constraint_form': constraint_form,
        'rule_form': rule_form,
        'diseases': diseases,
        'allergens': allergens,
        'rules': rules,
    })
