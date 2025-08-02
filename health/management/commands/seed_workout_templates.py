from django.core.management.base import BaseCommand
from health.models import WorkoutTemplate, WorkoutTemplateDay, WorkoutProgram

# Templates
TEMPLATES = [
    # --------------------- 1. Busy Professional 3-day Full-body ---------------------
    {
        "name": "Busy Professional Full-Body (3-Day)",
        "description": "Whole-body workouts for the time-crunched, maximizing muscle and strength gains.",
        "days": [
            (1, [
                ("Squats (Back/Front)", 3, "10", ""),
                ("Bench Press", 3, "10", ""),
                ("Lat Pulldown", 3, "12", ""),
                ("Plank", 2, "45s", ""),
            ]),
            (3, [
                ("Deadlift", 3, "8", ""),
                ("Push-ups", 3, "AMRAP", ""),
                ("Seated Cable Row", 3, "10", ""),
                ("Calf Raises (Standing/Seated)", 2, "15", ""),
            ]),
            (5, [
                ("Lunges (Walking/Stationary)", 3, "10/leg", ""),
                ("Overhead Press (Barbell/Dumbbell)", 3, "10", ""),
                ("Dips (Bench/Parallel Bars)", 2, "AMRAP", ""),
                ("Russian Twists", 2, "20", ""),
            ]),
        ]
    },
    # --------------------- 2. Female Shape (4-Day Legs & Glutes focus) ---------------------
    {
        "name": "Female Shape & Tone (4-Day, Lower Focus)",
        "description": "Targets lower body and glutes for shaping and toning.",
        "days": [
            (1, [
                ("Squats (Back/Front)", 4, "10", ""),
                ("Leg Press", 3, "12", ""),
                ("Glute Bridge", 3, "15", "Use barbell or bodyweight"),
                ("Calf Raises (Standing/Seated)", 3, "15", ""),
            ]),
            (2, [
                ("Bench Press", 3, "10", ""),
                ("Lat Pulldown", 3, "10", ""),
                ("Dumbbell Curl", 2, "15", ""),
                ("Tricep Pushdown", 2, "15", ""),
            ]),
            (4, [
                ("Deadlift", 3, "8", ""),
                ("Lunges (Walking/Stationary)", 3, "12/leg", ""),
                ("Hamstring Curl", 3, "12", ""),
                ("Leg Extension", 2, "15", ""),
            ]),
            (5, [
                ("Push-ups", 3, "AMRAP", ""),
                ("Overhead Press (Barbell/Dumbbell)", 3, "10", ""),
                ("Rear Delt Fly", 2, "15", ""),
                ("Russian Twists", 2, "20", ""),
            ]),
        ]
    },
    # --------------------- 3. Athlete Power & Performance (5-Day) ---------------------
    {
        "name": "Athlete Power & Performance (5-Day)",
        "description": "Sprint, jump, and lift your way to superior athleticism.",
        "days": [
            (1, [
                ("Squats (Back/Front)", 4, "6", ""),
                ("Hang Power Clean", 3, "5", "If experience allows"),
                ("Plank", 2, "60s", ""),
                ("Box Jump", 2, "8", ""),
            ]),
            (2, [
                ("Deadlift", 4, "5", ""),
                ("Pull-ups / Chin-ups", 3, "AMRAP", ""),
                ("Seated Cable Row", 3, "8", ""),
                ("Russian Twists", 2, "20", ""),
            ]),
            (3, [
                ("Bench Press", 4, "8", ""),
                ("Push-ups", 3, "AMRAP", ""),
                ("Overhead Press (Barbell/Dumbbell)", 3, "10", ""),
                ("Skull Crushers", 2, "12", ""),
            ]),
            (5, [
                ("Lunges (Walking/Stationary)", 3, "10/leg", ""),
                ("Hamstring Curl", 3, "12", ""),
                ("Calf Raises (Standing/Seated)", 2, "20", ""),
                ("Sled Push", 2, "40m", "If equipment available"),
            ]),
            (6, [
                ("Sprints (Treadmill/Track)", 5, "40m", "Max effort, full rest"),
                ("Bike Intervals", 3, "1min fast:2min slow", ""),
                ("Plank", 2, "60s", ""),
            ]),
        ]
    },
    # --------------------- 4. Gym Fat Loss (6-Day with Cardio) ---------------------
    {
        "name": "Fat Loss Accelerator (6-Day)",
        "description": "High frequency, moderate volume, cardio for maximum fat burning.",
        "days": [
            (1, [
                ("Squats (Back/Front)", 3, "12", ""),
                ("Bench Press", 3, "12", ""),
                ("Plank", 2, "60s", ""),
                ("Treadmill Running / Walking", 1, "20min", ""),
            ]),
            (2, [
                ("Lat Pulldown", 3, "12", ""),
                ("Seated Cable Row", 3, "12", ""),
                ("Deadlift", 3, "8", ""),
                ("Rowing Machine", 1, "20min", ""),
            ]),
            (3, [
                ("Lunges (Walking/Stationary)", 3, "12/leg", ""),
                ("Leg Press", 3, "15", ""),
                ("Hamstring Curl", 2, "15", ""),
                ("Elliptical Trainer", 1, "20min", ""),
            ]),
            (4, [
                ("Overhead Press (Barbell/Dumbbell)", 3, "12", ""),
                ("Lateral Raises", 2, "15", ""),
                ("Rear Delt Fly", 2, "12", ""),
                ("Jump Rope", 1, "10min", ""),
            ]),
            (5, [
                ("Push-ups", 3, "AMRAP", ""),
                ("Sit-ups / Crunches", 2, "15", ""),
                ("Russian Twists", 2, "20", ""),
                ("Treadmill Running / Walking", 1, "20min", ""),
            ]),
            (6, [
                ("Full Body Stretch", 1, "10min", "Use mat"),
                ("Cardio", 1, "30min", "Your choice"),
            ]),
        ]
    },
    # --------------------- 5. Senior/Rehab-Friendly (3-Day) ---------------------
    {
        "name": "Seniors & Beginners (3-Day Circuit)",
        "description": "Gentle, joint-friendly full body injury prevention and mobility routine.",
        "days": [
            (1, [
                ("Leg Extension", 2, "12", ""),
                ("Chest Fly", 2, "12", ""),
                ("Seated Cable Row", 2, "12", ""),
                ("Plank", 1, "30s", ""),
            ]),
            (3, [
                ("Lunges (Walking/Stationary)", 2, "8/leg", ""),
                ("Push-ups", 2, "Knee/Inclined", "Adjust to level"),
                ("Lat Pulldown", 2, "12", ""),
                ("Sit-ups / Crunches", 1, "12", ""),
            ]),
            (5, [
                ("Hamstring Curl", 2, "12", ""),
                ("Overhead Press (Barbell/Dumbbell)", 2, "10", ""),
                ("Russian Twists", 1, "10", ""),
            ]),
        ]
    },
    # --------------------- 6. Strength & Size - Powerbuilding (5-Day) ---------------------
    {
        "name": "Strength & Size Powerbuilder (5-Day)",
        "description": "Combines core lifts with hypertrophy for serious muscle & PRs.",
        "days": [
            (1, [
                ("Bench Press", 5, "5", ""),
                ("Incline Bench Press", 4, "8", ""),
                ("Tricep Pushdown", 3, "12", ""),
            ]),
            (2, [
                ("Deadlift", 5, "5", ""),
                ("Lat Pulldown", 3, "8", ""),
                ("T-Bar Row", 3, "10", ""),
            ]),
            (3, [
                ("Squats (Back/Front)", 5, "5", ""),
                ("Leg Press", 4, "8", ""),
                ("Hamstring Curl", 3, "15", ""),
            ]),
            (5, [
                ("Overhead Press (Barbell/Dumbbell)", 4, "8", ""),
                ("Lateral Raises", 3, "15", ""),
                ("Rear Delt Fly", 3, "15", ""),
            ]),
            (6, [
                ("Pull-ups / Chin-ups", 3, "AMRAP", ""),
                ("Barbell Curl", 3, "12", ""),
                ("Push-ups", 2, "AMRAP", ""),
            ]),
        ]
    },
    # --------------------- 7. Core & Conditioning (4-Day) ---------------------
    {
        "name": "Core & Conditioning Focus (4-Day)",
        "description": "Train your abs, trunk strength and conditioning.",
        "days": [
            (1, [
                ("Plank", 3, "60s", ""),
                ("Cable Woodchopper", 3, "12", ""),
                ("Lat Pulldown", 3, "10", ""),
                ("Treadmill Running / Walking", 1, "20min", ""),
            ]),
            (2, [
                ("Russian Twists", 3, "20", ""),
                ("Deadlift", 3, "8", ""),
                ("Push-ups", 3, "AMRAP", ""),
                ("Bike Machine", 1, "20min", ""),
            ]),
            (4, [
                ("Sit-ups / Crunches", 3, "15", ""),
                ("Hanging Leg Raise", 2, "10", ""),
                ("Rowing Machine", 1, "15min", ""),
            ]),
            (5, [
                ("Plank", 3, "60s", ""),
                ("Burpees", 2, "15", ""),
                ("Elliptical Trainer", 1, "20min", ""),
                ("Stretching", 1, "10min", "Flexibility work"),
            ]),
        ]
    },
    # --------------------- 8. Upper/Lower Split - Classic (4-Day) ---------------------
    {
        "name": "Classic Upper Lower (4-Day)",
        "description": "Train all muscle groups, balanced recovery, time-flexible.",
        "days": [
            (1, [
                ("Bench Press", 3, "10", ""),
                ("Overhead Press (Barbell/Dumbbell)", 3, "10", ""),
                ("Tricep Pushdown", 2, "12", ""),
                ("Barbell Curl", 2, "12", ""),
            ]),
            (2, [
                ("Squats (Back/Front)", 4, "10", ""),
                ("Leg Press", 3, "12", ""),
                ("Leg Extension", 2, "15", ""),
                ("Calf Raises (Standing/Seated)", 2, "15", ""),
            ]),
            (4, [
                ("Pull-ups / Chin-ups", 3, "AMRAP", ""),
                ("Seated Cable Row", 3, "12", ""),
                ("Rear Delt Fly", 2, "12", ""),
                ("Russian Twists", 2, "20", ""),
            ]),
            (5, [
                ("Deadlift", 4, "8", ""),
                ("Lunges (Walking/Stationary)", 3, "12/leg", ""),
                ("Hamstring Curl", 2, "15", ""),
                ("Plank", 2, "60s", ""),
            ]),
        ]
    },
    # --------------------- 9. Glute Builder (3-day) ---------------------
    {
        "name": "Glute Builder (3-Day, Female Focus)",
        "description": "Isolation and compound moves for glute strength and shape.",
        "days": [
            (1, [
                ("Squats (Back/Front)", 4, "10", ""),
                ("Glute Bridge", 4, "15", "Weighted if possible"),
                ("Hamstring Curl", 3, "12", ""),
                ("Calf Raises (Standing/Seated)", 2, "20", ""),
            ]),
            (3, [
                ("Lunges (Walking/Stationary)", 4, "12/leg", ""),
                ("Leg Press", 3, "12", ""),
                ("Leg Extension", 2, "15", ""),
                ("Russian Twists", 2, "20", ""),
            ]),
            (5, [
                ("Deadlift", 3, "8", ""),
                ("Hip Thrust", 3, "12", "Use barbell/Smith if available"),
                ("Plank", 2, "45s", ""),
            ]),
        ]
    },
    # --------------------- 10. Physique Athlete - Advanced (6-Day) ---------------------
    {
        "name": "Physique Athlete Advanced (6-Day Split)",
        "description": "For serious bodybuilders or physique competitors – maximal muscle detail.",
        "days": [
            (1, [
                ("Bench Press", 4, "10", ""),
                ("Incline Bench Press", 4, "8", ""),
                ("Chest Fly", 4, "12", ""),
                ("Push-ups", 2, "AMRAP", ""),
            ]),
            (2, [
                ("Deadlift", 4, "8", ""),
                ("Seated Cable Row", 4, "10", ""),
                ("T-Bar Row", 3, "10", ""),
                ("Lat Pulldown", 3, "10", ""),
            ]),
            (3, [
                ("Squats (Back/Front)", 4, "8", ""),
                ("Leg Press", 4, "12", ""),
                ("Leg Extension", 3, "15", ""),
                ("Calf Raises (Standing/Seated)", 3, "20", ""),
            ]),
            (4, [
                ("Overhead Press (Barbell/Dumbbell)", 4, "10", ""),
                ("Lateral Raises", 3, "15", ""),
                ("Front Raises", 2, "12", ""),
                ("Arnold Press", 2, "12", ""),
            ]),
            (5, [
                ("Barbell Curl", 3, "12", ""),
                ("Dumbbell Curl", 3, "12", ""),
                ("Tricep Pushdown", 3, "12", ""),
                ("Skull Crushers", 2, "12", ""),
            ]),
            (6, [
                ("Lunges (Walking/Stationary)", 3, "12/leg", ""),
                ("Hamstring Curl", 3, "15", ""),
                ("Russian Twists", 2, "20", ""),
                ("Plank", 2, "60s", ""),
            ]),
        ]
    },
]


# Support for new exercise names: Create them if they do not exist
def get_or_create_workout(name):
    obj, created = WorkoutProgram.objects.get_or_create(name=name)
    return obj


class Command(BaseCommand):
    help = "Seed a variety of world-class weekly workout templates into the database"

    def handle(self, *args, **kwargs):
        for tpl in TEMPLATES:
            tpl_obj, _ = WorkoutTemplate.objects.get_or_create(
                name=tpl["name"],
                defaults={"description": tpl["description"]}
            )
            for day_number, workouts in tpl["days"]:
                for workout_name, sets, reps, notes in workouts:
                    try:
                        workout = WorkoutProgram.objects.get(name=workout_name)
                    except WorkoutProgram.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Workout '{workout_name}' not found. Skipping."))
                        continue
                    WorkoutTemplateDay.objects.get_or_create(
                        template=tpl_obj,
                        day_number=day_number,
                        workout=workout,
                        defaults={
                            "sets": sets,
                            "reps": reps,
                            "notes": notes
                        }
                    )
        self.stdout.write(self.style.SUCCESS("✅ All premium weekly workout templates created."))

