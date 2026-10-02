from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, FoodProduct, HealthConstraint, PasswordResetCode


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'sexe', 'culinary_level', 'activity_level')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations complémentaires', {
            'fields': (
                'avatar', 'bio', 'health_constraints', 'age', 'weight', 'height',
                'sexe', 'restrictions', 'aliments_a_eviter', 'activity_level', 'culinary_level'
            )
        }),
    )


@admin.register(HealthConstraint)
class HealthConstraintAdmin(admin.ModelAdmin):
    list_display = ('name', 'constraint_type', 'color', 'icon')
    list_filter = ('constraint_type',)
    search_fields = ('name',)


@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)


@admin.register(FoodProduct)
class FoodProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'calories', 'difficulty')
    list_filter = ('category', 'difficulty')
    search_fields = ('name', 'ingredients_text')
    list_per_page = 25