from django.db import models
from django.conf import settings


class Transaction(models.Model):
    """
    Represents a financial record (income or expense).
    Each transaction belongs to the user who created it.
    Admins can see and manage all transactions.
    """
    TYPE_INCOME = 'income'
    TYPE_EXPENSE = 'expense'
    TYPE_CHOICES = [
        (TYPE_INCOME, 'Income'),
        (TYPE_EXPENSE, 'Expense'),
    ]

    CATEGORY_CHOICES = [
        ('salary', 'Salary'),
        ('freelance', 'Freelance'),
        ('investment', 'Investment'),
        ('rent', 'Rent'),
        ('food', 'Food & Dining'),
        ('transport', 'Transport'),
        ('utilities', 'Utilities'),
        ('healthcare', 'Healthcare'),
        ('entertainment', 'Entertainment'),
        ('education', 'Education'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    is_deleted = models.BooleanField(default=False)  # soft delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type.upper()} | {self.category} | {self.amount} on {self.date}"
