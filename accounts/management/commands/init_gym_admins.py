from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from accounts.models import Gym

User = get_user_model()

class Command(BaseCommand):
    help = 'Create default gym, developer admin and dummy gym admins if not exist'

    def handle(self, *args, **options):
        # STEP 0: Create a temporary dummy gym to satisfy NOT NULL constraint
        try:
            dummy_gym, created = Gym.objects.get_or_create(
                name="Temp Gym",
                defaults={
                    'location': 'Temporary Location',
                    'proprietor_name': 'Temp Proprietor',
                    'is_active': True,
                    'admin': None
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Temporary gym created'))
            else:
                self.stdout.write('Temporary gym already exists')
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating dummy gym: {str(e)}'))
            return

        # STEP 1: Create developer admin user with unique username
        dev_phone = '7736500760'
        dev_email = 'satheeshappzdev@gmail.com'
        dev_password = 'devadminpassword'
        
        dev_user, created = User.objects.get_or_create(
            phone_number=dev_phone,
            defaults={
                'username': 'DEV_ADMIN',  # Set explicit username
                'first_name': 'Dev',
                'last_name': 'Admin',
                'email': dev_email,
                'country_code': 'IN',
                'staff_role': 'Admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'gym': dummy_gym,
            }
        )
        if created:
            dev_user.set_password(dev_password)
            dev_user.save()
            self.stdout.write(self.style.SUCCESS('Developer admin user created'))
        else:
            self.stdout.write('Developer admin user already exists')

        # STEP 2: Create default gym with admin set
        try:
            default_gym, gym_created = Gym.objects.get_or_create(
                id=1,
                defaults={
                    'name': 'Default Gym',
                    'location': '123 Main Street, Demo City',
                    'latitude': 12.971598,
                    'longitude': 77.594566,
                    'proprietor_name': 'John Doe',
                    'is_active': True,
                    'admin': dev_user,
                }
            )
            if gym_created:
                self.stdout.write(self.style.SUCCESS('Default gym created'))
            else:
                self.stdout.write('Default gym already exists')
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR(f'Error creating default gym: {str(e)}'))
            return

        # STEP 3: Update developer admin's gym field
        dev_user.gym = default_gym
        dev_user.save()
        self.stdout.write(self.style.SUCCESS('Developer admin linked to default gym'))

        # STEP 4: Create 3 dummy gym admins with unique usernames
        for i in range(1, 4):
            admin_phone = f'888888888{i}'
            admin_email = f'gymadmin{i}@example.com'
            
            admin_user, user_created = User.objects.get_or_create(
                phone_number=admin_phone,
                defaults={
                    'username': f'GYM_ADMIN_{i}',  # Set explicit unique username
                    'first_name': f'GymAdmin{i}',
                    'last_name': 'Admin',
                    'email': admin_email,
                    'country_code': 'IN',
                    'staff_role': 'Admin',
                    'is_staff': True,
                    'is_superuser': False,
                    'is_active': True,
                    'gym': dummy_gym,
                }
            )
            if user_created:
                admin_user.set_password('gymadminpassword')
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(f'Gym admin user {i} created'))
            else:
                self.stdout.write(f'Gym admin user {i} already exists')

            # Create dummy gym with admin set
            gym_name = f'Dummy Gym {i}'
            gym, gym_created = Gym.objects.get_or_create(
                name=gym_name,
                defaults={
                    'location': f'Sample Location {i}',
                    'proprietor_name': f'Proprietor {i}',
                    'is_active': True,
                    'admin': admin_user,
                }
            )

            # Update gym field of admin user to the correct gym
            admin_user.gym = gym
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Gym admin user {i} linked to {gym_name}'))

        # STEP 5: Clean up temporary gym
        if dummy_gym.users.count() == 0:
            dummy_gym.delete()
            self.stdout.write(self.style.SUCCESS('Temporary gym cleaned up'))
        else:
            self.stdout.write(self.style.WARNING(f'Temporary gym still has {dummy_gym.users.count()} users'))

        self.stdout.write(self.style.SUCCESS('All gyms and admin users setup completed'))
