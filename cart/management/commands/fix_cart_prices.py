"""
Management command to fix cart item prices.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from cart.models import CartItem


class Command(BaseCommand):
    help = 'Fix cart items with None or invalid prices'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Find cart items with None or 0 prices
        problematic_items = CartItem.objects.filter(
            price_at_addition__isnull=True
        ).union(
            CartItem.objects.filter(price_at_addition=0)
        )
        
        if not problematic_items.exists():
            self.stdout.write(self.style.SUCCESS('No problematic cart items found!'))
            return
        
        self.stdout.write(f'Found {problematic_items.count()} problematic cart items')
        
        fixed_count = 0
        error_count = 0
        
        with transaction.atomic():
            for item in problematic_items:
                try:
                    old_price = item.price_at_addition
                    
                    # Try to get price from variant first, then product
                    new_price = None
                    
                    if item.variant and hasattr(item.variant, 'final_price') and item.variant.final_price:
                        new_price = item.variant.final_price
                    elif item.product:
                        if item.product.sale_price:
                            new_price = item.product.sale_price
                        elif item.product.price:
                            new_price = item.product.price
                    
                    if new_price is not None and new_price > 0:
                        if not dry_run:
                            item.price_at_addition = new_price
                            item.save()
                        
                        self.stdout.write(
                            f'Item {item.id}: {old_price} -> {new_price} '
                            f'(Product: {item.product.name})'
                        )
                        fixed_count += 1
                    else:
                        # Set default price of 0 if no valid price found
                        if not dry_run:
                            item.price_at_addition = Decimal('0.00')
                            item.save()
                        
                        self.stdout.write(
                            self.style.WARNING(
                                f'Item {item.id}: Set to 0.00 (no valid price found) '
                                f'(Product: {item.product.name})'
                            )
                        )
                        fixed_count += 1
                
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error fixing item {item.id}: {str(e)}'
                        )
                    )
                    error_count += 1
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN: Would fix {fixed_count} items with {error_count} errors'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Fixed {fixed_count} items with {error_count} errors'
                )
            )