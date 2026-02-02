from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from accounts.models import Vendor

User = get_user_model()

class Command(BaseCommand):
    help = 'Create default Vendor, developer admin and dummy Vendor admins if not exist'

    def handle(self, *args, **options):
        # Use a transaction to ensure database integrity
        try:
            with transaction.atomic():
                # STEP 0: Create a temporary dummy Vendor
                dummy_vendor, created = Vendor.objects.get_or_create(
                    name="Temp Vendor",
                    defaults={
                        'location': 'Temporary Location',
                        'proprietor_name': 'Temp Proprietor',
                        'is_active': True,
                        'admin': None
                    }
                )

                # STEP 1: Create developer admin
                dev_user, created = User.objects.get_or_create(
                    phone_number='7736500760',
                    defaults={
                        'username': 'DEV_ADMIN',
                        'first_name': 'Dev',
                        'last_name': 'Admin',
                        'email': 'satheeshappzdev@gmail.com',
                        'country_code': 'IN',
                        'staff_role': 'Admin',
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                        'Vendor': dummy_vendor, # Ensure this matches your User field name
                    }
                )
                if created:
                    dev_user.set_password('devadminpassword')
                    dev_user.save()

                # STEP 2: Create default Vendor
                default_vendor, _ = Vendor.objects.get_or_create(
                    id=1,
                    defaults={
                        'name': 'Default Vendor',
                        'location': '123 Main Street, Demo City',
                        'proprietor_name': 'John Doe',
                        'admin': dev_user,
                    }
                )

                # STEP 3: Link developer admin to default Vendor
                dev_user.Vendor = default_vendor
                dev_user.save()

                # STEP 4: Create dummy Vendor admins
                for i in range(1, 4):
                    admin_user, u_created = User.objects.get_or_create(
                        phone_number=f'888888888{i}',
                        defaults={
                            'username': f'GYM_ADMIN_{i}',
                            'staff_role': 'Admin',
                            'is_staff': True,
                            'Vendor': dummy_vendor,
                        }
                    )
                    if u_created:
                        admin_user.set_password('vendoradminpassword')
                        admin_user.save()

                    # CHANGE: Renamed variable to 'v_obj' to avoid shadowing the 'Vendor' class
                    v_obj, _ = Vendor.objects.get_or_create(
                        name=f'Dummy Vendor {i}',
                        defaults={
                            'location': f'Sample Location {i}',
                            'proprietor_name': f'Proprietor {i}',
                            'admin': admin_user,
                        }
                    )

                    # Update User link
                    admin_user.Vendor = v_obj
                    admin_user.save()

                # STEP 5: Clean up temporary Vendor using .exists() for efficiency
                if not dummy_vendor.users_administered.exists():
                    dummy_vendor.delete()
                    self.stdout.write(self.style.SUCCESS('Temporary Vendor cleaned up'))

            self.stdout.write(self.style.SUCCESS('All vendors and admin users setup completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
