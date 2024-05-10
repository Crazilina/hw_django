from django import forms

from catalog.models import Product


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
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


class VersionForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
