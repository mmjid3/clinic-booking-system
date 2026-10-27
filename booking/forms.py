from django import forms
from .models import Appointment, Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['staff', 'service']
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'name@example.com'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email address is already registered. Please log in instead.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars") for i in range(5, 0, -1)],
                                   attrs={'class': 'form-select'}),
            'comment': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience with this doctor...'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        }