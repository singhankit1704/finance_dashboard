"""
Run: python seed_data.py
Seeds 3 users (admin, analyst, viewer) and sample transactions.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_dashboard.settings')
django.setup()

from users.models import User
from transactions.models import Transaction
from datetime import date, timedelta
import random

print("Seeding users...")
# Admin
admin, _ = User.objects.get_or_create(username='admin')
admin.set_password('Admin@123')
admin.role = 'admin'
admin.email = 'admin@finance.com'
admin.first_name = 'Alice'
admin.last_name = 'Admin'
admin.save()

# Analyst
analyst, _ = User.objects.get_or_create(username='analyst')
analyst.set_password('Analyst@123')
analyst.role = 'analyst'
analyst.email = 'analyst@finance.com'
analyst.first_name = 'Bob'
analyst.last_name = 'Analyst'
analyst.save()

# Viewer
viewer, _ = User.objects.get_or_create(username='viewer')
viewer.set_password('Viewer@123')
viewer.role = 'viewer'
viewer.email = 'viewer@finance.com'
viewer.first_name = 'Carol'
viewer.last_name = 'Viewer'
viewer.save()

print("Seeding transactions...")
categories_income = ['salary', 'freelance', 'investment']
categories_expense = ['rent', 'food', 'transport', 'utilities', 'healthcare', 'entertainment']

Transaction.objects.all().delete()
today = date.today()
for i in range(30):
    for user in [admin, analyst, viewer]:
        # Income
        Transaction.objects.create(
            user=user,
            amount=round(random.uniform(1000, 8000), 2),
            type='income',
            category=random.choice(categories_income),
            date=today - timedelta(days=i * 3),
            description=f'Income record #{i}'
        )
        # Expense
        Transaction.objects.create(
            user=user,
            amount=round(random.uniform(100, 3000), 2),
            type='expense',
            category=random.choice(categories_expense),
            date=today - timedelta(days=i * 3 + 1),
            description=f'Expense record #{i}'
        )

print("Done! Users created:")
print("  admin / Admin@123   (role: admin)")
print("  analyst / Analyst@123 (role: analyst)")
print("  viewer / Viewer@123  (role: viewer)")
