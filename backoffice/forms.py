from django import forms

from accounts.models import FoodProduct, HealthConstraint
from .models import SubstitutionRule


def _normalize_multiline_text(value):
    lines = [line.strip() for line in (value or '').splitlines() if line.strip()]
    return '\n'.join(lines)


class FoodProductForm(forms.ModelForm):
    image_upload = forms.ImageField(required=False)

    class Meta:
        model = FoodProduct
        fields = [
            'name',
            'category',
            'calories',
            'nutriscore',
            'proteins',
            'carbs',
            'fats',
            'difficulty',
            'image_url',
            'ingredients_text',
            'preparation_steps',
            'allergens_tags',
            'sugars_100g',
            'salt_100g',
        ]
        widgets = {
            'ingredients_text': forms.Textarea(attrs={'rows': 8, 'class': 'textarea', 'placeholder': 'Tomato\nOlive oil\nBasil'}),
            'preparation_steps': forms.Textarea(attrs={'rows': 8, 'class': 'textarea', 'placeholder': '1. Prepare ingredients\n2. Cook gently\n3. Serve warm'}),
            'allergens_tags': forms.Textarea(attrs={'rows': 4, 'class': 'textarea', 'placeholder': 'gluten, lactose'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        select_fields = {'category', 'difficulty', 'nutriscore'}
        for name, field in self.fields.items():
            if name == 'image_upload':
                field.widget.attrs.update({'class': 'control'})
            elif name in select_fields:
                field.widget.attrs.update({'class': 'select'})
            elif name not in {'ingredients_text', 'preparation_steps', 'allergens_tags'}:
                field.widget.attrs.update({'class': 'control'})
        self.fields['name'].widget.attrs.setdefault('placeholder', 'Recipe title')
        self.fields['image_url'].widget.attrs.setdefault('placeholder', 'https://...')

    def clean_ingredients_text(self):
        return _normalize_multiline_text(self.cleaned_data.get('ingredients_text'))

    def clean_preparation_steps(self):
        return _normalize_multiline_text(self.cleaned_data.get('preparation_steps'))

    def clean_allergens_tags(self):
        raw = self.cleaned_data.get('allergens_tags') or ''
        tags = [tag.strip() for tag in raw.replace('\n', ',').split(',') if tag.strip()]
        return ', '.join(tags)

    def save(self, commit=True):
        instance = super().save(commit=False)
        image_upload = self.cleaned_data.get('image_upload')
        if image_upload:
            instance.image = image_upload
            instance.image_url = ''
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class HealthConstraintForm(forms.ModelForm):
    class Meta:
        model = HealthConstraint
        fields = ['name', 'constraint_type', 'color', 'icon']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'control', 'placeholder': 'Diabete'})
        self.fields['constraint_type'].widget.attrs.update({'class': 'select'})
        self.fields['color'].widget.attrs.update({'class': 'control', 'placeholder': '#e8621a'})
        self.fields['icon'].widget.attrs.update({'class': 'control', 'placeholder': 'drop, heart, leaf...'})


class SubstitutionRuleForm(forms.ModelForm):
    class Meta:
        model = SubstitutionRule
        fields = ['target_constraint', 'forbidden_ingredient', 'substitute', 'difficulty']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target_constraint'].widget.attrs.update({'class': 'select'})
        self.fields['forbidden_ingredient'].widget.attrs.update({'class': 'control', 'placeholder': 'sucre blanc'})
        self.fields['substitute'].widget.attrs.update({'class': 'control', 'placeholder': 'stevia'})
        self.fields['difficulty'].widget.attrs.update({'class': 'select'})
