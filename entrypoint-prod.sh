#!/bin/sh

echo "=== Iron Board Production Setup Started ==="

# Set DB connection for staging/production environment using environment variables
export DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

echo "Creating default gym..."
# Insert default Gym if not exists
psql "$DATABASE_URL" <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM accounts_gym WHERE id = 1) THEN
        INSERT INTO accounts_gym (id, name, location, latitude, longitude, proprietor_name, is_active)
        VALUES (1, 'Production Gym', '123 Production Street, Production City', 12.971598, 77.594566, 'Production Admin', TRUE);
    END IF;
END
\$\$;
EOF

echo "Generating migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate

echo "Creating admin users..."
python manage.py init_gym_admins

# Seeding scripts (run once only, create marker file after each)
if [ ! -f .seeded_seed_workout_templates ]; then
    echo "Seeding initial workout templates..."
    python manage.py seed_workout_templates && touch .seeded_seed_workout_templates
fi

if [ ! -f .seeded_seed_more_workout_templates ]; then
    echo "Seeding more workout templates (variety)..."
    python manage.py seed_more_workout_templates && touch .seeded_seed_more_workout_templates
fi

if [ ! -f .seeded_workout_seed ]; then
    echo "Seeding basic workouts..."
    python manage.py workout_seed && touch .seeded_workout_seed
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "=== Starting Gunicorn Production Server ==="
# Run production server with Gunicorn
exec gunicorn iron_board.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100
