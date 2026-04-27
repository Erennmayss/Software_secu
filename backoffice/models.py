from django.db import models

from accounts.models import HealthConstraint


class SubstitutionRule(models.Model):
    DIFFICULTY_EASY = 'easy'
    DIFFICULTY_MODERATE = 'moderate'
    DIFFICULTY_COMPLEX = 'complex'
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, 'Facile'),
        (DIFFICULTY_MODERATE, 'Modere'),
        (DIFFICULTY_COMPLEX, 'Complexe'),
    ]

    target_constraint = models.ForeignKey(
        HealthConstraint,
        on_delete=models.CASCADE,
        related_name='substitution_rules',
    )
    forbidden_ingredient = models.CharField(max_length=255)
    substitute = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_EASY)

    class Meta:
        ordering = ['target_constraint__name', 'forbidden_ingredient']
        unique_together = ('target_constraint', 'forbidden_ingredient', 'substitute')

    def __str__(self):
        return f'{self.target_constraint.name}: {self.forbidden_ingredient} -> {self.substitute}'
