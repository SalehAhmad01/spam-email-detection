from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

# Common Tailwind CSS classes for form fields
TAILWIND_INPUT_CLASS = (
    "w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm text-white "
    "placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 "
    "transition-colors"
)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'name@example.com'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'email':
                field.widget.attrs['class'] = TAILWIND_INPUT_CLASS
                field.widget.attrs['placeholder'] = f"Enter {field.label.lower()}"


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Enter your password'})
    )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT_CLASS, 'placeholder': 'Email Address'}),
        }
