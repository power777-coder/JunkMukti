from django import forms
from .models import Waste, Review, Message


class WasteForm(forms.ModelForm):
    class Meta:
        model = Waste
        fields = [
            'waste_type',
            'category',
            'description',
            'weight_kg',
            'location',
            'image',
        ]
        widgets = {
            'waste_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select waste type'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the waste item in detail...'
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Weight in kg',
                'step': '0.01'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f"{i} Stars") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your experience...'
            }),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Message subject'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Type your message...'
            }),
        }


class BidForm(forms.Form):
    amount = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your bid amount',
            'step': '0.01',
            'min': '0'
        })
    )


class WasteFilterForm(forms.Form):
    waste_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + Waste.WASTE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price_min = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price'
        })
    )
    price_max = forms.FloatField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price'
        })
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest'),
            ('final_price', 'Price Low to High'),
            ('-final_price', 'Price High to Low'),
            ('weight_kg', 'Weight Low to High'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

