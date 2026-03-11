"""
Signals for the SpendWise expenses app.

post_save on User → auto-create default Category objects for every new user.
"""

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Category

# Default categories created for every new user.
# Each tuple: (name, emoji)
DEFAULT_CATEGORIES = [
    ('Salary',        '💰'),
    ('Entertainment', '🎬'),
    ('Shopping',      '🛒'),
    ('Rent',          '🏠'),
    ('EMI',           '💳'),
    ('Miscellaneous', '❓'),
    ('Fuel',          '⛽'),
    ('Groceries',     '🍱'),
]


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    """
    When a brand-new User is saved, create the default set of categories
    for that user so the app is immediately usable.
    """
    if not created:
        return

    Category.objects.bulk_create([
        Category(user=instance, name=name, emoji=emoji)
        for name, emoji in DEFAULT_CATEGORIES
    ])
