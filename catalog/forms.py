from django import forms
from django.forms import inlineformset_factory

from catalog.models import Product, Version


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProductForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'image', 'category', 'price',)

    def clean_name(self):
        cleaned_data = self.cleaned_data['name']
        forbidden_words = ['казино', 'криптовалюта', 'крипта', 'биржа', 'дешево',
                           'бесплатно', 'обман', 'полиция', 'радар']
        if any(word in cleaned_data.lower() for word in forbidden_words):
            raise forms.ValidationError('В названии продукта использованы запрещенные слова.')
        return cleaned_data

    def clean_description(self):
        cleaned_data = self.cleaned_data['description']
        forbidden_words = ['казино', 'криптовалюта', 'крипта', 'биржа', 'дешево',
                           'бесплатно', 'обман', 'полиция', 'радар']
        if any(word in cleaned_data.lower() for word in forbidden_words):
            raise forms.ValidationError('В описании продукта использованы запрещенные слова.')
        return cleaned_data


class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ['version_number', 'version_title', 'is_current']


VersionFormSet = inlineformset_factory(
    Product,
    Version,
    form=VersionForm,
    extra=1,  # количество форм для создания новых версий
    can_delete=True  # разрешаем удаление версий
)
