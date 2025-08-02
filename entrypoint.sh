#!/bin/sh

# Set DB connection
export DATABASE_URL="postgresql://ironboard_user:xPL7y6qe1gLHAg2B9SWvW06vXSC8lxSe@dpg-d1v8576uk2gs73bc448g-a.oregon-postgres.render.com/ironboard_db"

# Insert default Gym if not exists
psql "$DATABASE_URL" <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM accounts_gym WHERE id = 1) THEN
        INSERT INTO accounts_gym (id, name, location, latitude, longitude, proprietor_name, is_active)
        VALUES (1, 'Default Gym', '123 Main Street, Demo City', 12.971598, 77.594566, 'John Doe', TRUE);
    END IF;
END
\$\$;
EOF

# Now migrate
python manage.py migrate

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

# Collect static files
python manage.py collectstatic --noinput

# Start server
python manage.py runserver 0.0.0.0:8000
