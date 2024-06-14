from django import forms
from .models import Category, MenuItem, Order

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name=name).exists():
            raise forms.ValidationError("Category with this name already exists.")
        return name

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['title', 'description', 'price', 'category']

    def clean_title(self):
        title = self.cleaned_data.get('title')
        category = self.cleaned_data.get('category')
        if MenuItem.objects.filter(title=title, category=category).exists():
            raise forms.ValidationError("Menu item with this title already exists in this category.")
        return title
