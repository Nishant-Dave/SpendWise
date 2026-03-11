"""
Forms for the SpendWise expenses app.

- CategoryForm   : create / edit a Category (name + emoji)
- TransactionForm: create / edit a Transaction (all fields)
- RegisterForm   : custom user-registration form
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, Transaction, EMOJI_CHOICES


# ---------------------------------------------------------------------------
# User Registration
# ---------------------------------------------------------------------------

class RegisterForm(UserCreationForm):
    """Extends the built-in UserCreationForm with an optional email field."""

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com',
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to every field automatically
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class CategoryForm(forms.ModelForm):
    """
    Form to create or edit a Category.

    The emoji field is rendered as a <select> using the predefined
    EMOJI_CHOICES list so users never need to type an emoji manually.
    """

    class Meta:
        model = Category
        # user is set in the view (request.user) — not exposed in the form
        fields = ('name', 'emoji')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Groceries, Salary, Netflix…',
                'maxlength': 100,
            }),
            'emoji': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
        labels = {
            'name': 'Category Name',
            'emoji': 'Icon (emoji)',
        }


# ---------------------------------------------------------------------------
# Transaction
# ---------------------------------------------------------------------------

class TransactionForm(forms.ModelForm):
    """
    Form to create or edit a Transaction.

    The category queryset is intentionally left empty here and filtered
    in the view to show only the current user's categories.
    Categories are NOT restricted to income/expense type.
    """

    class Meta:
        model = Transaction
        # user is set in the view (request.user) — not exposed in the form
        fields = ('type', 'amount', 'category', 'description', 'date')
        widgets = {
            'type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Short description (optional)',
                'maxlength': 255,
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',   # renders as an HTML5 date picker
            }),
        }
        labels = {
            'type': 'Transaction Type',
            'amount': 'Amount (₹)',
            'category': 'Category',
            'description': 'Description',
            'date': 'Date',
        }

    def __init__(self, user=None, *args, **kwargs):
        """
        Accept the logged-in user so the category queryset can be
        filtered to only show that user's own categories.
        """
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['category'].queryset = (
                Category.objects.filter(user=user)
            )
        # Mark category as not required (model allows NULL)
        self.fields['category'].required = False
        self.fields['category'].empty_label = '— No Category —'
