from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from master.models import Vendor
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Create realistic Kerala-based vendors for testing'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # STEP 1: Create developer admin
                dev_user, created = User.objects.get_or_create(
                    phone_number='7736500760',
                    defaults={
                        'first_name': 'Satheesh',
                        'last_name': 'Dev',
                        'email': 'satheeshappzdev@gmail.com',
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )
                if created:
                    dev_user.set_password('devadminpassword')
                    dev_user.save()
                    self.stdout.write(self.style.SUCCESS(f'Created dev admin: {dev_user.phone_number}'))

                # STEP 2: Create realistic Kerala vendors
                vendors_data = [
                    {
                        'phone': '9876543210',
                        'shop_name': 'Malabar Biriyani House',
                        'shop_description': 'Authentic Kozhikode biriyani and traditional Kerala cuisine',
                        'email': 'malabarbiriyani@example.com',
                        'address': 'SM Street, Near Calicut Medical College',
                        'city': 'Kozhikode',
                        'state': 'Kerala',
                        'pincode': '673032',
                        'latitude': Decimal('11.2588'),
                        'longitude': Decimal('75.7804'),
                        'gstin': '32AABCU9603R1ZM',
                        'pan': 'AABCU9603R',
                    },
                    {
                        'phone': '9876543211',
                        'shop_name': 'Paragon Restaurant',
                        'shop_description': 'Famous for seafood and traditional Malabar dishes',
                        'email': 'paragonrestaurant@example.com',
                        'address': 'Kannur Road, Near Beach',
                        'city': 'Kozhikode',
                        'state': 'Kerala',
                        'pincode': '673001',
                        'latitude': Decimal('11.2480'),
                        'longitude': Decimal('75.7720'),
                        'gstin': '32AABCP9604R1ZN',
                        'pan': 'AABCP9604R',
                    },
                    {
                        'phone': '9876543212',
                        'shop_name': 'Zain\'s Hotel',
                        'shop_description': 'Popular for biriyani and grilled items',
                        'email': 'zainshotel@example.com',
                        'address': 'Mavoor Road, Junction',
                        'city': 'Kozhikode',
                        'state': 'Kerala',
                        'pincode': '673004',
                        'latitude': Decimal('11.2639'),
                        'longitude': Decimal('75.7877'),
                        'gstin': '32AABCZ9605R1ZO',
                        'pan': 'AABCZ9605R',
                    },
                    {
                        'phone': '9876543213',
                        'shop_name': 'Salkara Restaurant',
                        'shop_description': 'Traditional Kerala breakfast and lunch',
                        'email': 'salkara@example.com',
                        'address': 'Palayam, Near Railway Station',
                        'city': 'Kozhikode',
                        'state': 'Kerala',
                        'pincode': '673002',
                        'latitude': Decimal('11.2510'),
                        'longitude': Decimal('75.7750'),
                        'gstin': '32AABCS9606R1ZP',
                        'pan': 'AABCS9606R',
                    },
                    {
                        'phone': '9876543214',
                        'shop_name': 'Kingsbay Restaurant',
                        'shop_description': 'Multi-cuisine restaurant with sea view',
                        'email': 'kingsbay@example.com',
                        'address': 'Beach Road, Beypore',
                        'city': 'Kozhikode',
                        'state': 'Kerala',
                        'pincode': '673015',
                        'latitude': Decimal('11.1720'),
                        'longitude': Decimal('75.8050'),
                        'gstin': '32AABCK9607R1ZQ',
                        'pan': 'AABCK9607R',
                    },
                ]

                for idx, vendor_data in enumerate(vendors_data, 1):
                    # Create vendor admin user
                    admin_user, u_created = User.objects.get_or_create(
                        phone_number=vendor_data['phone'],
                        defaults={
                            'first_name': vendor_data['shop_name'].split()[0],
                            'last_name': 'Admin',
                            'email': vendor_data['email'],
                            'is_staff': True,
                            'is_active': True,
                        }
                    )
                    if u_created:
                        admin_user.set_password('vendor123')
                        admin_user.save()
                        self.stdout.write(self.style.SUCCESS(f'Created vendor admin: {admin_user.phone_number}'))

                    # Create vendor
                    vendor, v_created = Vendor.objects.get_or_create(
                        user=admin_user,
                        defaults={
                            'shop_name': vendor_data['shop_name'],
                            'shop_description': vendor_data['shop_description'],
                            'phone': vendor_data['phone'],
                            'email': vendor_data['email'],
                            'address': vendor_data['address'],
                            'city': vendor_data['city'],
                            'state': vendor_data['state'],
                            'pincode': vendor_data['pincode'],
                            'latitude': vendor_data['latitude'],
                            'longitude': vendor_data['longitude'],
                            'gstin': vendor_data['gstin'],
                            'pan': vendor_data['pan'],
                            'is_active': True,
                        }
                    )
                    if v_created:
                        self.stdout.write(self.style.SUCCESS(f'Created vendor: {vendor.shop_name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Vendor already exists: {vendor.shop_name}'))

                self.stdout.write(self.style.SUCCESS('✅ All Kerala vendors setup completed!'))
                self.stdout.write(self.style.SUCCESS(f'📍 Location: Kozhikode, Kerala'))
                self.stdout.write(self.style.SUCCESS(f'🔑 Default password for all vendors: vendor123'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ An error occurred: {e}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))