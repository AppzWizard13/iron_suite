#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Set Django Settings here so manage.py knows what to load
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-myoceanbasket.settings.development}

echo "=== Iron Board Setup Started ==="

echo "Generating migrations..."
python manage.py makemigrations --noinput

echo "Applying migrations..."
python manage.py migrate

echo "Creating default gym and admin users..."
if [ ! -f .init_gym_admins ]; then
    python manage.py init_gym_admins && touch .init_gym_admins
    echo "✅ Admin data seeded successfully"
else
    echo "ℹ️ Admin data already seeded, skipping..."
fi

echo "Seeding fitness data..."
if [ ! -f .seeded_fitness_data ]; then
    python manage.py seed_fitness_data && touch .seeded_fitness_data
    echo "✅ Fitness data seeded successfully"
else
    echo "ℹ️ Fitness data already seeded, skipping..."
fi

echo "Seeding configuration values..."
if [ ! -f .seeded_config ]; then
    python manage.py seed_config && touch .seeded_config
    echo "✅ Configuration values seeded successfully"
else
    echo "ℹ️ Configuration values already seeded, skipping..."
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Starting Django Development Server ==="
exec python manage.py runserver 0.0.0.0:8000
