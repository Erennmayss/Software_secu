from django.contrib import admin
from .models import SubstitutionRule


@admin.register(SubstitutionRule)
class SubstitutionRuleAdmin(admin.ModelAdmin):
    list_display = ('target_constraint', 'forbidden_ingredient', 'substitute', 'difficulty')
    list_filter = ('difficulty', 'target_constraint')
    search_fields = ('forbidden_ingredient', 'substitute', 'target_constraint__name')
    ordering = ('target_constraint__name', 'forbidden_ingredient')
