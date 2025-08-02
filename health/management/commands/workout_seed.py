from django.core.management.base import BaseCommand
from health.models import WorkoutCategory, WorkoutProgram, Equipment

class Command(BaseCommand):
    help = "Seed initial workout programs into the database"

    def handle(self, *args, **kwargs):
        data = [
            # Format: (Category, Exercise, Type, [Equipment])
            ("Chest", "Bench Press", "Compound", ["Barbell", "Bench"]),
            ("Chest", "Dumbbell Press", "Compound", ["Dumbbells", "Bench"]),
            ("Chest", "Chest Fly", "Isolation", ["Dumbbells", "Machine"]),
            ("Chest", "Push-ups", "Bodyweight", []),
            ("Chest", "Incline Bench Press", "Compound", ["Barbell", "Incline Bench"]),
            ("Back", "Deadlift", "Compound", ["Barbell"]),
            ("Back", "Lat Pulldown", "Isolation", ["Pulley Machine"]),
            ("Back", "Pull-ups / Chin-ups", "Bodyweight", ["Bar", "Assisted Machine"]),
            ("Back", "Seated Cable Row", "Compound", ["Cable Machine"]),
            ("Back", "T-Bar Row", "Compound", ["T-Bar", "Landmine"]),
            ("Shoulders", "Overhead Press (Barbell/Dumbbell)", "Compound", ["Barbell", "Dumbbells"]),
            ("Shoulders", "Lateral Raises", "Isolation", ["Dumbbells"]),
            ("Shoulders", "Front Raises", "Isolation", ["Dumbbells", "Plates"]),
            ("Shoulders", "Rear Delt Fly", "Isolation", ["Dumbbells", "Machine"]),
            ("Shoulders", "Arnold Press", "Compound", ["Dumbbells"]),
            ("Arms (Biceps)", "Barbell Curl", "Isolation", ["Barbell"]),
            ("Arms (Biceps)", "Dumbbell Curl", "Isolation", ["Dumbbells"]),
            ("Arms (Biceps)", "Preacher Curl", "Isolation", ["EZ Bar", "Machine"]),
            ("Arms (Biceps)", "Concentration Curl", "Isolation", ["Dumbbell"]),
            ("Arms (Triceps)", "Tricep Pushdown", "Isolation", ["Cable Machine"]),
            ("Arms (Triceps)", "Skull Crushers", "Isolation", ["EZ Bar"]),
            ("Arms (Triceps)", "Close-grip Bench Press", "Compound", ["Barbell"]),
            ("Arms (Triceps)", "Dips (Bench/Parallel Bars)", "Bodyweight", ["Parallel Bars"]),
            ("Legs", "Squats (Back/Front)", "Compound", ["Barbell"]),
            ("Legs", "Leg Press", "Compound", ["Leg Press Machine"]),
            ("Legs", "Lunges (Walking/Stationary)", "Compound", ["Dumbbells", "Bodyweight"]),
            ("Legs", "Leg Extension", "Isolation", ["Machine"]),
            ("Legs", "Hamstring Curl", "Isolation", ["Machine"]),
            ("Legs", "Calf Raises (Standing/Seated)", "Isolation", ["Machine", "Free Weights"]),
            ("Core / Abs", "Plank", "Isometric", ["Bodyweight"]),
            ("Core / Abs", "Sit-ups / Crunches", "Bodyweight", ["Mat"]),
            ("Core / Abs", "Hanging Leg Raise", "Bodyweight", ["Bar"]),
            ("Core / Abs", "Cable Woodchopper", "Isolation", ["Cable Machine"]),
            ("Core / Abs", "Russian Twists", "Bodyweight / DB", ["Mat", "Medicine Ball"]),
            ("Cardio", "Treadmill Running / Walking", "Cardio", ["Treadmill"]),
            ("Cardio", "Elliptical Trainer", "Cardio", ["Elliptical Machine"]),
            ("Cardio", "Stationary Bike", "Cardio", ["Bike Machine"]),
            ("Cardio", "Rowing Machine", "Cardio", ["Rowing Machine"]),
            ("Cardio", "Jump Rope", "Cardio", ["Rope"]),
        ]

        for category_name, exercise_name, type_name, equipment_list in data:
            category_obj, _ = WorkoutCategory.objects.get_or_create(name=category_name)

            workout_obj, created = WorkoutProgram.objects.get_or_create(
                name=exercise_name,
                category=category_obj,
                type=type_name,
            )

            # Add equipment
            workout_obj.equipment.clear()
            for eq_name in equipment_list:
                eq_obj, _ = Equipment.objects.get_or_create(name=eq_name)
                workout_obj.equipment.add(eq_obj)

        self.stdout.write(self.style.SUCCESS("✅ Workout programs seeded successfully!"))
