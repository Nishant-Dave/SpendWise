from django.db import models
from django.contrib.auth.models import User


# ---------------------------------------------------------------------------
# Predefined emoji choices for categories.
# Format: (stored_value, human_readable_label)
# ---------------------------------------------------------------------------
EMOJI_CHOICES = [
    # Income / General Finance
    ('💰', '💰 Money Bag'),
    ('💵', '💵 Dollar Banknote'),
    ('💳', '💳 Credit Card'),
    ('🏦', '🏦 Bank'),
    ('📈', '📈 Chart Increasing'),
    ('💹', '💹 Chart with Rupee'),
    ('🤑', '🤑 Money-Mouth Face'),
    # Food & Drink
    ('🍔', '🍔 Burger'),
    ('🍕', '🍕 Pizza'),
    ('☕', '☕ Coffee'),
    ('🍱', '🍱 Bento Box'),
    ('🛒', '🛒 Shopping Cart'),
    # Transport
    ('🚗', '🚗 Car'),
    ('🚌', '🚌 Bus'),
    ('✈️', '✈️ Airplane'),
    ('⛽', '⛽ Fuel Pump'),
    # Home & Utilities
    ('🏠', '🏠 House'),
    ('💡', '💡 Electricity'),
    ('💧', '💧 Water'),
    ('📡', '📡 Internet / TV'),
    # Health & Fitness
    ('🏥', '🏥 Hospital'),
    ('💊', '💊 Medicine'),
    ('🏋️', '🏋️ Gym'),
    # Entertainment & Shopping
    ('🎮', '🎮 Video Game'),
    ('🎬', '🎬 Movie'),
    ('🎵', '🎵 Music'),
    ('👗', '👗 Clothing'),
    ('📚', '📚 Books / Education'),
    # Travel & Leisure
    ('🌴', '🌴 Vacation'),
    ('🏨', '🏨 Hotel'),
    # Savings & Investment
    ('🐷', '🐷 Piggy Bank'),
    ('📊', '📊 Investments'),
    # Miscellaneous
    ('🎁', '🎁 Gift'),
    ('🔧', '🔧 Maintenance'),
    ('📱', '📱 Phone / Tech'),
    ('❓', '❓ Other'),
]


class Category(models.Model):
    """
    A user-defined spending / income category.

    Categories are NOT locked to income or expense — the same category
    can be used for both.  The emoji field gives each category a visual
    identity throughout the UI.
    """

    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='categories',
    )
    emoji = models.CharField(
        max_length=10,
        choices=EMOJI_CHOICES,
        default='❓',
        help_text='Select an emoji to represent this category.',
    )

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        # Each user can only have one category with the same name
        unique_together = ('user', 'name')
        ordering = ['name']

    def __str__(self):
        return f'{self.emoji} {self.name}'


class Transaction(models.Model):
    """
    A single financial transaction (income or expense) belonging to a user.
    """

    INCOME = 'Income'
    EXPENSE = 'Expense'
    TRANSACTION_TYPE_CHOICES = [
        (INCOME, 'Income'),
        (EXPENSE, 'Expense'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Amount in Indian Rupees (₹).',
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    date = models.DateField()
    type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES,
        default=EXPENSE,
    )

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-id']

    def __str__(self):
        symbol = '+' if self.type == self.INCOME else '-'
        category_label = str(self.category) if self.category else 'No Category'
        return f'[{self.type}] {symbol}₹{self.amount} — {category_label} ({self.date})'
