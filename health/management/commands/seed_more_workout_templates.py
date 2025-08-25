from django.core.management.base import BaseCommand
from health.models import WorkoutTemplate, WorkoutTemplateDay, WorkoutProgram

TEMPLATES = [
    # 1. Endurance & Hypertrophy Hybrid (5-Day)
    {
        "name": "Endurance & Hypertrophy Hybrid (5-Day)",
        "description": "Blends higher reps for muscle plus short finishers for conditioning.",
        "days": [
            (1, [("Bench Press", 4, "15", ""), ("Incline Bench Press", 3, "12", ""), ("Push-ups", 2, "AMRAP", ""), ("Plank", 2, "60s", "")]),
            (2, [("Deadlift", 4, "12", ""), ("Lat Pulldown", 3, "15", ""), ("Seated Cable Row", 3, "12", ""), ("Treadmill Running / Walking", 1, "15min", "")]),
            (3, [("Squats (Back/Front)", 4, "15", ""), ("Leg Press", 3, "15", ""), ("Hamstring Curl", 2, "15", ""), ("Jump Rope", 1, "5min", "")]),
            (4, [("Overhead Press (Barbell/Dumbbell)", 3, "12", ""), ("Front Raises", 2, "15", ""), ("Skull Crushers", 2, "15", ""), ("Bike Machine", 1, "12min", "")]),
            (5, [("Lunges (Walking/Stationary)", 3, "15/leg", ""), ("Russian Twists", 2, "25", ""), ("Push-ups", 2, "AMRAP", ""), ("Elliptical Trainer", 1, "15min", "")]),
        ]
    },
    # 2. HIIT + Weights Express (4-Day)
    {
        "name": "HIIT + Weights Express (4-Day)",
        "description": "Alternate fast circuits, weights, and HIIT for fat loss and fitness.",
        "days": [
            (1, [("Squats (Back/Front)", 3, "12", ""), ("Push-ups", 3, "20", ""), ("Lat Pulldown", 3, "15", ""), ("Burpees", 2, "12", "")]),
            (2, [("Deadlift", 3, "10", ""), ("Seated Cable Row", 3, "12", ""), ("Plank", 2, "45s", ""), ("Jump Rope", 2, "2min", "")]),
            (4, [("Lunges (Walking/Stationary)", 3, "15/leg", ""), ("Arnold Press", 3, "10", ""), ("Dumbbell Curl", 2, "15", ""), ("Mountain Climbers", 2, "30s", "")]),
            (5, [("Leg Press", 3, "15", ""), ("Overhead Press (Barbell/Dumbbell)", 3, "12", ""), ("Sit-ups / Crunches", 2, "20", ""), ("Bike Intervals", 1, "10min", "")]),
        ]
    },
    # 3. Home Bodyweight Only (5-Day)
    {
        "name": "Home Bodyweight Only (5-Day)",
        "description": "Perfect when you can't access a gym; zero equipment, effective training.",
        "days": [
            (1, [("Push-ups", 4, "AMRAP", ""), ("Plank", 3, "60s", ""), ("Lunges (Walking/Stationary)", 3, "20", ""), ("Russian Twists", 3, "25", "")]),
            (2, [("Squats (Back/Front)", 4, "20", "Bodyweight only"), ("Sit-ups / Crunches", 3, "20", ""), ("Incline Push-ups", 3, "15", ""), ("Glute Bridge", 3, "20", "")]),
            (3, [("Mountain Climbers", 4, "30s", ""), ("Plank", 3, "45s", ""), ("Reverse Lunges", 3, "20", ""), ("Superman", 2, "15", "")]),
            (4, [("Dips (Bench/Parallel Bars)", 3, "15", "Chair for dips"), ("Bulgarian Split Squat", 3, "12/leg", ""), ("Bear Crawl", 2, "30s", ""), ("Push-ups", 2, "AMRAP", "")]),
            (5, [("Burpees", 4, "12", ""), ("Plank", 2, "60s", ""), ("Crunches", 2, "20", ""), ("Squat Jumps", 2, "12", "")]),
        ]
    },
    # 4. Functional Strength & Agility (4-Day)
    {
        "name": "Functional Strength & Agility (4-Day)",
        "description": "Combine weights, balance, rotational and agility moves.",
        "days": [
            (1, [("Deadlift", 4, "8", ""), ("Kettlebell Swing", 3, "15", ""), ("Plank", 2, "60s", ""), ("Lateral Lunges", 2, "12/side", "")]),
            (2, [("Push-ups", 3, "AMRAP", ""), ("Dumbbell Snatch", 3, "10/arm", ""), ("Bear Crawl", 2, "30s", ""), ("Medicine Ball Slams", 2, "15", "")]),
            (4, [("Squats (Back/Front)", 3, "12", ""), ("Box Jump", 3, "10", ""), ("Single Leg Deadlift", 2, "12/leg", ""), ("Farmer's Walk", 2, "30s", "")]),
            (5, [("Bulgarian Split Squat", 3, "12/leg", ""), ("Hanging Leg Raise", 2, "10", ""), ("Push-ups", 2, "AMRAP", ""), ("Jump Rope", 2, "2min", "")]),
        ]
    },
    # 5. Youth / Teens Foundation (3-Day)
    {
        "name": "Youth/Teens Foundation (3-Day)",
        "description": "Safe whole-body movement, confidence, and core strength for youth.",
        "days": [
            (1, [("Bodyweight Squats", 3, "15", ""), ("Push-ups", 2, "AMRAP", ""), ("Plank", 2, "40s", ""), ("Jump Rope", 1, "3min", "")]),
            (3, [("Lunges (Walking/Stationary)", 3, "12/leg", ""), ("Sit-ups / Crunches", 2, "15", ""), ("Medicine Ball Throws", 2, "10", ""), ("Jogging", 1, "6min", "")]),
            (5, [("Wall Sit", 2, "40s", ""), ("Push-ups", 2, "AMRAP", ""), ("Bear Crawl", 1, "30s", ""), ("Stretching", 1, "10min", "")]),
        ]
    },
    # 6. Lower-Upper-Lower HIIT (3-Day)
    {
        "name": "Lower-Upper-Lower HIIT (3-Day)",
        "description": "High-intensity intervals interspersed with major lifts; quick fat loss.",
        "days": [
            (1, [("Squats (Back/Front)", 4, "10", ""), ("Jump Rope", 3, "2min", ""), ("Lunges (Walking/Stationary)", 3, "15", ""), ("Mountain Climbers", 2, "30s", "")]),
            (3, [("Push-ups", 3, "20", ""), ("Bench Press", 4, "10", ""), ("Pull-ups / Chin-ups", 3, "AMRAP", ""), ("Burpees", 2, "15", "")]),
            (5, [("Deadlift", 4, "8", ""), ("Bike Sprints", 3, "1min fast:2min easy", ""), ("Leg Press", 3, "12", ""), ("Plank", 2, "60s", "")]),
        ]
    },
    # 7. Classic Yoga-Mobility (3-Day)
    {
        "name": "Yoga & Mobility Routine (3-Day)",
        "description": "Flexibility, core control, and recovery—perfect for all levels.",
        "days": [
            (1, [("Sun Salutation Flow", 3, "8", "Yoga flow"), ("Plank", 2, "60s", ""), ("Child's Pose", 1, "2min", ""), ("Seated Twist", 1, "1min", "")]),
            (3, [("Downward Dog", 2, "1min", ""), ("Cobra Stretch", 2, "1min", ""), ("Pigeon Pose", 1, "2min", ""), ("Russian Twists", 2, "15", "")]),
            (5, [("Cat-Cow", 2, "1min", ""), ("Side Plank", 2, "45s/side", ""), ("Hamstring Stretch", 1, "2min", ""), ("Thread the Needle", 1, "1min", "")]),
        ]
    },
    # 8. Post-Injury / Rehab Basic (3-Day)
    {
        "name": "Rehab & Active Recovery (3-Day)",
        "description": "Light, joint-friendly—consult physiotherapist for restrictions.",
        "days": [
            (1, [("Leg Extension", 2, "12", ""), ("Chest Fly", 2, "12", ""), ("Seated Cable Row", 2, "12", ""), ("Plank", 1, "30s", "")]),
            (3, [("Glute Bridge", 2, "15", ""), ("Hamstring Curl", 2, "12", ""), ("Rear Delt Fly", 2, "12", ""), ("Stretching", 1, "10min", "")]),
            (5, [("Standing Calf Raise", 2, "15", ""), ("Push-ups", 2, "Knee", ""), ("Lat Pulldown", 2, "12", ""), ("Foam Roll", 1, "10min", "")]),
        ]
    },
    # 9. Advanced Powerlifting Split (6-Day)
    {
        "name": "Powerlifting Advanced (6-Day)",
        "description": "Squat, bench, deadlift each twice per week—designed for strength.",
        "days": [
            (1, [("Squats (Back/Front)", 5, "5", ""), ("Leg Press", 4, "10", ""), ("Calf Raises (Standing/Seated)", 3, "15", "")]),
            (2, [("Bench Press", 5, "5", ""), ("Incline Bench Press", 3, "8", ""), ("Tricep Pushdown", 3, "10", "")]),
            (3, [("Deadlift", 5, "5", ""), ("Seated Cable Row", 3, "10", ""), ("Barbell Curl", 3, "10", "")]),
            (4, [("Squats (Back/Front)", 3, "8", ""), ("Hamstring Curl", 3, "12", ""), ("Calf Raises (Standing/Seated)", 3, "15", "")]),
            (5, [("Bench Press", 3, "8", ""), ("Overhead Press (Barbell/Dumbbell)", 3, "8", ""), ("Tricep Pushdown", 3, "12", "")]),
            (6, [("Deadlift", 3, "8", ""), ("T-Bar Row", 3, "10", ""), ("Dumbbell Curl", 2, "12", "")]),
        ]
    },
    # 10. Women’s Athletic Total-Body Tone (5-Day)
    {
        "name": "Women’s Athletic Total-Body Tone (5-Day)",
        "description": "For athletic women after full-body strength, toning, and variety.",
        "days": [
            (1, [("Squats (Back/Front)", 4, "12", ""), ("Push-ups", 3, "AMRAP", ""), ("Calf Raises (Standing/Seated)", 3, "20", ""), ("Russian Twists", 3, "20", "")]),
            (2, [("Bench Press", 4, "10", ""), ("Lat Pulldown", 3, "15", ""), ("Glute Bridge", 3, "15", ""), ("Plank", 2, "60s", "")]),
            (3, [("Deadlift", 4, "8", ""), ("Lunges (Walking/Stationary)", 3, "15/leg", ""), ("Sit-ups / Crunches", 2, "20", ""), ("Rear Delt Fly", 2, "15", "")]),
            (4, [("Leg Press", 3, "15", ""), ("Overhead Press (Barbell/Dumbbell)", 3, "10", ""), ("Arnold Press", 2, "10", ""), ("Jump Rope", 2, "3min", "")]),
            (5, [("Push-ups", 3, "AMRAP", ""), ("Incline Bench Press", 3, "10", ""), ("Barbell Curl", 2, "12", ""), ("Hip Thrust", 2, "15", "")]),
        ]
    }
]

class Command(BaseCommand):
    help = "Seed 10 additional world-class workout templates into the database"

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
        self.stdout.write(self.style.SUCCESS("✅ 10 more premium weekly workout templates created."))
