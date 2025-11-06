"""
Reset migrations script for clean database setup.
Use this when encountering migration conflicts.
"""
import os
import sys
import shutil
from pathlib import Path

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eshop.settings.development')

def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")

def delete_migration_files():
    """Delete all migration files except __init__.py"""
    print_header("🗑️  STEP 1: CLEANING OLD MIGRATIONS")
    
    apps = ['authentication', 'products', 'cart', 'orders']
    deleted_count = 0
    
    for app in apps:
        migrations_dir = Path(app) / 'migrations'
        if migrations_dir.exists():
            for file in migrations_dir.glob('*.py'):
                if file.name != '__init__.py':
                    file.unlink()
                    deleted_count += 1
                    print(f"   Deleted: {file}")
            
            # Also delete __pycache__
            pycache = migrations_dir / '__pycache__'
            if pycache.exists():
                shutil.rmtree(pycache)
                print(f"   Deleted: {pycache}")
    
    print(f"\n✅ Deleted {deleted_count} migration files")

def delete_database():
    """Delete SQLite database if exists."""
    print_header("🗄️  STEP 2: REMOVING OLD DATABASE")
    
    db_file = Path('db.sqlite3')
    if db_file.exists():
        db_file.unlink()
        print(f"✅ Deleted database: {db_file}")
    else:
        print("ℹ️  No database file found (using PostgreSQL?)")

def create_fresh_migrations():
    """Create fresh migrations."""
    print_header("📝 STEP 3: CREATING FRESH MIGRATIONS")
    
    import django
    django.setup()
    
    from django.core.management import call_command
    
    # Create migrations
    print("Creating new migrations...")
    call_command('makemigrations')
    print("\n✅ Fresh migrations created")

def apply_migrations():
    """Apply all migrations."""
    print_header("🔄 STEP 4: APPLYING MIGRATIONS")
    
    import django
    django.setup()
    
    from django.core.management import call_command
    
    # Apply migrations
    print("Applying migrations to database...")
    call_command('migrate')
    print("\n✅ Migrations applied successfully")

def main():
    """Execute migration reset."""
    print("\n╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "MIGRATION RESET UTILITY" + " " * 30 + "║")
    print("║" + " " * 10 + "Clean slate for database migrations" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print("\n⚠️  WARNING: This will delete all migrations and database data!")
    response = input("\nContinue? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("\n❌ Operation cancelled by user")
        sys.exit(0)
    
    try:
        delete_migration_files()
        delete_database()
        create_fresh_migrations()
        apply_migrations()
        
        print_header("🎉 MIGRATION RESET COMPLETE!")
        print("✅ All migrations cleaned and recreated")
        print("✅ Database schema updated successfully")
        print("\n🚀 Next steps:")
        print("   1. Run: python setup_eshop.py")
        print("   2. Or run: python manage.py createsuperuser")
        print("   3. Start server: python manage.py runserver --settings=eshop.settings.development")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ Migration reset failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()