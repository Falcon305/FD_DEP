from django import forms
from django.forms import ModelForm



class ProductForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'quantity', 
                'category', 'price', 'is_published', 'address', 'city', 'zipcode', 'delivery']
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)