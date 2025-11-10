#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '日日鮮肉品專賣.settings.development')
django.setup()

from django.db import connection

# Check the actual database schema
with connection.cursor() as cursor:
    cursor.execute("PRAGMA table_info(orders_order)")
    columns = cursor.fetchall()
    print("Actual database columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

print("\nModel expects these fields:")
from orders.models import Order
for field in Order._meta.fields:
    print(f"  {field.name} -> {field.column}")