# #!/bin/sh

# set -e

# echo "=== Iron Board Setup Started ==="

# echo "Generating migrations..."
# python manage.py makemigrations

# echo "Applying migrations..."
# python manage.py migrate

# echo "Creating default gym and admin users..."
# python manage.py init_gym_admins

# echo "Seeding fitness data..."
# if [ ! -f .seeded_fitness_data ]; then
#     python manage.py seed_fitness_data && touch .seeded_fitness_data
#     echo "✅ Fitness data seeded successfully"
# else
#     echo "ℹ️ Fitness data already seeded, skipping..."
# fi

# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# echo "=== Starting Django Development Server ==="
# exec python manage.py runserver 0.0.0.0:8000
# # Note: For production, use entrypoint-prod.sh with Gunicorn