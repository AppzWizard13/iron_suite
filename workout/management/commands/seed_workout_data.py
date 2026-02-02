# workout/management/__init__.py
# (Create this empty file)

# workout/management/commands/__init__.py  
# (Create this empty file)

# workout/management/commands/seed_workout_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from workout.models import *

User = get_user_model()

# Equipment data
EQUIPMENT_DATA = [
    ('Barbell', 'Strength', 'Olympic barbell for heavy compound movements'),
    ('Dumbbell', 'Strength', 'Adjustable dumbbells for isolation and unilateral work'),
    ('Machine', 'Strength', 'Weight machines for controlled movements'),
    ('Cable', 'Strength', 'Cable machine for various pulling and pushing exercises'),
    ('Bodyweight', 'Bodyweight', 'No equipment needed - bodyweight exercises'),
    ('Cardio Equipment', 'Cardio', 'Treadmill, bike, elliptical, rower'),
    ('Resistance Bands', 'Accessory', 'Elastic bands for light resistance work'),
    ('Kettlebell', 'Strength', 'Kettlebells for dynamic movements'),
    ('Medicine Ball', 'Functional', 'Weighted ball for core and functional training'),
    ('Suspension Trainer', 'Functional', 'TRX or similar suspension training system'),
]

# Exercise data
EXERCISES_DATA = [
    # Barbell exercises
    ('Bench Press', 'Barbell', 'Chest, Triceps, Front Deltoids', 'Lie on bench, grip barbell shoulder-width, lower to chest, press up'),
    ('Incline Bench Press', 'Barbell', 'Upper Chest, Front Deltoids, Triceps', 'Press barbell on inclined bench targeting upper chest'),
    ('Deadlift', 'Barbell', 'Hamstrings, Glutes, Erector Spinae, Traps', 'Stand with barbell, hinge at hips, keep back straight, lift by extending hips'),
    ('Squats (Back/Front)', 'Barbell', 'Quadriceps, Glutes, Hamstrings', 'Stand with barbell, squat down keeping chest up, drive through heels to stand'),
    ('Overhead Press (Barbell/Dumbbell)', 'Barbell', 'Shoulders, Triceps, Core', 'Stand with barbell at shoulder level, press overhead keeping core tight'),
    ('Barbell Curl', 'Barbell', 'Biceps', 'Curl barbell up with controlled movement'),
    ('Skull Crushers', 'Barbell', 'Triceps', 'Lying tricep extension with barbell'),
    
    # Dumbbell exercises
    ('Dumbbell Snatch', 'Dumbbell', 'Full Body, Shoulders', 'Explosive movement from floor to overhead'),
    ('Arnold Press', 'Dumbbell', 'Shoulders, Triceps', 'Rotating shoulder press movement'),
    ('Dumbbell Curl', 'Dumbbell', 'Biceps', 'Curl dumbbells with controlled movement'),
    ('Front Raises', 'Dumbbell', 'Front Deltoids', 'Raise dumbbells to front until parallel to floor'),
    ('Rear Delt Fly', 'Dumbbell', 'Rear Deltoids, Rhomboids', 'Reverse fly movement'),
    
    # Machine exercises
    ('Leg Press', 'Machine', 'Quadriceps, Glutes', 'Sit in leg press machine, press weight with full range of motion'),
    ('Lat Pulldown', 'Machine', 'Latissimus Dorsi, Biceps, Rhomboids', 'Pull bar down to upper chest, squeeze shoulder blades'),
    ('Seated Cable Row', 'Machine', 'Latissimus Dorsi, Rhomboids, Rear Deltoids', 'Pull handles to torso, squeeze shoulder blades'),
    ('Leg Extension', 'Machine', 'Quadriceps', 'Extend legs against resistance'),
    ('Hamstring Curl', 'Machine', 'Hamstrings', 'Curl heels toward glutes while lying or seated'),
    ('Tricep Pushdown', 'Cable', 'Triceps', 'Push cable down extending elbows'),
    ('Calf Raises (Standing/Seated)', 'Machine', 'Calves', 'Raise heels while standing or seated'),
    
    # Cable exercises
    ('T-Bar Row', 'Cable', 'Latissimus Dorsi, Rhomboids', 'Row using T-bar or landmine setup'),
    ('Chest Fly', 'Cable', 'Chest, Front Deltoids', 'Bring cables together in fly motion'),
    
    # Bodyweight exercises
    ('Push-ups', 'Bodyweight', 'Chest, Triceps, Core', 'Lower body to floor, push up maintaining straight line'),
    ('Incline Push-ups', 'Bodyweight', 'Chest, Triceps', 'Push-ups with hands elevated on bench'),
    ('Pull-ups / Chin-ups', 'Bodyweight', 'Latissimus Dorsi, Biceps', 'Hang from bar, pull up until chin over bar'),
    ('Dips (Bench/Parallel Bars)', 'Bodyweight', 'Triceps, Chest', 'Lower body between parallel bars, push up'),
    ('Plank', 'Bodyweight', 'Core, Shoulders', 'Hold straight line position on forearms'),
    ('Sit-ups / Crunches', 'Bodyweight', 'Abdominals', 'Curl upper body toward knees'),
    ('Russian Twists', 'Bodyweight', 'Obliques, Core', 'Seated rotation with or without weight'),
    ('Lunges (Walking/Stationary)', 'Bodyweight', 'Quadriceps, Glutes', 'Step forward into lunge, alternate legs'),
    ('Bulgarian Split Squat', 'Bodyweight', 'Quadriceps, Glutes', 'Rear foot elevated lunge'),
    ('Glute Bridge', 'Bodyweight', 'Glutes, Hamstrings', 'Lie on back, lift hips by squeezing glutes'),
    ('Hip Thrust', 'Bodyweight', 'Glutes, Hamstrings', 'Shoulders on bench, thrust hips up'),
    ('Mountain Climbers', 'Bodyweight', 'Core, Shoulders, Cardio', 'Rapid alternating knee to chest in plank position'),
    ('Burpees', 'Bodyweight', 'Full Body, Cardio', 'Squat, jump back to plank, push-up, jump forward, jump up'),
    ('Bear Crawl', 'Bodyweight', 'Full Body, Core', 'Crawl on hands and feet'),
    ('Wall Sit', 'Bodyweight', 'Quadriceps, Glutes', 'Sit against wall with thighs parallel to floor'),
    ('Single Leg Deadlift', 'Bodyweight', 'Hamstrings, Glutes, Balance', 'Hinge on one leg'),
    ('Box Jump', 'Bodyweight', 'Quadriceps, Glutes, Power', 'Jump onto elevated surface'),
    ('Squat Jumps', 'Bodyweight', 'Quadriceps, Glutes, Power', 'Jump from squat position'),
    ('Lateral Lunges', 'Bodyweight', 'Quadriceps, Glutes, Adductors', 'Lunge to the side'),
    ('Reverse Lunges', 'Bodyweight', 'Quadriceps, Glutes', 'Step backward into lunge'),
    ('Superman', 'Bodyweight', 'Lower Back, Glutes', 'Lie prone, lift chest and legs'),
    ('Hanging Leg Raise', 'Bodyweight', 'Core, Hip Flexors', 'Hang from bar, raise legs'),
    
    # Cardio exercises
    ('Treadmill Running / Walking', 'Cardio Equipment', 'Cardiovascular', 'Walk or run on treadmill'),
    ('Jump Rope', 'Cardio Equipment', 'Cardiovascular, Coordination', 'Jump rope at steady pace'),
    ('Bike Machine', 'Cardio Equipment', 'Cardiovascular, Quadriceps', 'Cycle at moderate to high intensity'),
    ('Elliptical Trainer', 'Cardio Equipment', 'Cardiovascular, Full Body', 'Low impact cardio movement'),
    ('Jogging', 'Cardio Equipment', 'Cardiovascular', 'Light running pace'),
    ('Bike Intervals', 'Cardio Equipment', 'Cardiovascular, HIIT', 'High intensity bike intervals'),
    ('Bike Sprints', 'Cardio Equipment', 'Cardiovascular, HIIT', 'Sprint intervals on bike'),
    
    # Specialty exercises
    ('Kettlebell Swing', 'Kettlebell', 'Hamstrings, Glutes, Core', 'Explosive hip hinge movement'),
    ('Medicine Ball Throws', 'Medicine Ball', 'Core, Power', 'Explosive throwing movement'),
    ('Medicine Ball Slams', 'Medicine Ball', 'Core, Power', 'Slam ball to ground'),
    ('Farmer\'s Walk', 'Dumbbell', 'Grip, Core, Traps', 'Walk carrying heavy weights at sides'),
    
    # Flexibility/Mobility
    ('Stretching', 'Bodyweight', 'Flexibility', 'General stretching routine'),
    ('Foam Roll', 'Bodyweight', 'Recovery', 'Self-myofascial release'),
    ('Sun Salutation Flow', 'Bodyweight', 'Flexibility, Flow', 'Yoga flow sequence'),
    ('Child\'s Pose', 'Bodyweight', 'Flexibility', 'Yoga resting pose'),
    ('Seated Twist', 'Bodyweight', 'Flexibility, Core', 'Seated spinal rotation'),
    ('Downward Dog', 'Bodyweight', 'Flexibility, Strength', 'Yoga pose'),
    ('Cobra Stretch', 'Bodyweight', 'Flexibility', 'Back extension stretch'),
    ('Pigeon Pose', 'Bodyweight', 'Flexibility', 'Hip flexibility pose'),
    ('Cat-Cow', 'Bodyweight', 'Flexibility', 'Spinal mobility movement'),
    ('Hamstring Stretch', 'Bodyweight', 'Flexibility', 'Hamstring flexibility'),
    ('Thread the Needle', 'Bodyweight', 'Flexibility', 'Thoracic spine mobility'),
]

# Workout templates (using your exact structure)
TEMPLATES = [
    # 1. Endurance & Hypertrophy Hybrid (5-Day)
    {
        "name": "Endurance & Hypertrophy Hybrid (5-Day)",
        "description": "Blends higher reps for muscle plus short finishers for conditioning.",
        "fitness_level": "medium",
        "goal": "weight_gain",
        "days": [
            ("monday", [("Bench Press", 4, "15", ""), ("Incline Bench Press", 3, "12", ""), ("Push-ups", 2, "AMRAP", ""), ("Plank", 2, "60s", "")]),
            ("tuesday", [("Deadlift", 4, "12", ""), ("Lat Pulldown", 3, "15", ""), ("Seated Cable Row", 3, "12", ""), ("Treadmill Running / Walking", 1, "15min", "")]),
            ("wednesday", [("Squats (Back/Front)", 4, "15", ""), ("Leg Press", 3, "15", ""), ("Hamstring Curl", 2, "15", ""), ("Jump Rope", 1, "5min", "")]),
            ("thursday", [("Overhead Press (Barbell/Dumbbell)", 3, "12", ""), ("Front Raises", 2, "15", ""), ("Skull Crushers", 2, "15", ""), ("Bike Machine", 1, "12min", "")]),
            ("friday", [("Lunges (Walking/Stationary)", 3, "15/leg", ""), ("Russian Twists", 2, "25", ""), ("Push-ups", 2, "AMRAP", ""), ("Elliptical Trainer", 1, "15min", "")]),
        ]
    },
    # 2. HIIT + Weights Express (4-Day)
    {
        "name": "HIIT + Weights Express (4-Day)",
        "description": "Alternate fast circuits, weights, and HIIT for fat loss and fitness.",
        "fitness_level": "medium",
        "goal": "weight_loss",
        "days": [
            ("monday", [("Squats (Back/Front)", 3, "12", ""), ("Push-ups", 3, "20", ""), ("Lat Pulldown", 3, "15", ""), ("Burpees", 2, "12", "")]),
            ("tuesday", [("Deadlift", 3, "10", ""), ("Seated Cable Row", 3, "12", ""), ("Plank", 2, "45s", ""), ("Jump Rope", 2, "2min", "")]),
            ("thursday", [("Lunges (Walking/Stationary)", 3, "15/leg", ""), ("Arnold Press", 3, "10", ""), ("Dumbbell Curl", 2, "15", ""), ("Mountain Climbers", 2, "30s", "")]),
            ("friday", [("Leg Press", 3, "15", ""), ("Overhead Press (Barbell/Dumbbell)", 3, "12", ""), ("Sit-ups / Crunches", 2, "20", ""), ("Bike Intervals", 1, "10min", "")]),
        ]
    },
    # 3. Home Bodyweight Only (5-Day)
    {
        "name": "Home Bodyweight Only (5-Day)",
        "description": "Perfect when you can't access a Vendor; zero equipment, effective training.",
        "fitness_level": "beginner",
        "goal": "basic_maintenance",
        "days": [
            ("monday", [("Push-ups", 4, "AMRAP", ""), ("Plank", 3, "60s", ""), ("Lunges (Walking/Stationary)", 3, "20", ""), ("Russian Twists", 3, "25", "")]),
            ("tuesday", [("Squats (Back/Front)", 4, "20", "Bodyweight only"), ("Sit-ups / Crunches", 3, "20", ""), ("Incline Push-ups", 3, "15", ""), ("Glute Bridge", 3, "20", "")]),
            ("wednesday", [("Mountain Climbers", 4, "30s", ""), ("Plank", 3, "45s", ""), ("Reverse Lunges", 3, "20", ""), ("Superman", 2, "15", "")]),
            ("thursday", [("Dips (Bench/Parallel Bars)", 3, "15", "Chair for dips"), ("Bulgarian Split Squat", 3, "12/leg", ""), ("Bear Crawl", 2, "30s", ""), ("Push-ups", 2, "AMRAP", "")]),
            ("friday", [("Burpees", 4, "12", ""), ("Plank", 2, "60s", ""), ("Sit-ups / Crunches", 2, "20", ""), ("Squat Jumps", 2, "12", "")]),
        ]
    },
    # 4. Functional Strength & Agility (4-Day)
    {
        "name": "Functional Strength & Agility (4-Day)",
        "description": "Combine weights, balance, rotational and agility moves.",
        "fitness_level": "advanced",
        "goal": "basic_maintenance",
        "days": [
            ("monday", [("Deadlift", 4, "8", ""), ("Kettlebell Swing", 3, "15", ""), ("Plank", 2, "60s", ""), ("Lateral Lunges", 2, "12/side", "")]),
            ("tuesday", [("Push-ups", 3, "AMRAP", ""), ("Dumbbell Snatch", 3, "10/arm", ""), ("Bear Crawl", 2, "30s", ""), ("Medicine Ball Slams", 2, "15", "")]),
            ("thursday", [("Squats (Back/Front)", 3, "12", ""), ("Box Jump", 3, "10", ""), ("Single Leg Deadlift", 2, "12/leg", ""), ("Farmer\'s Walk", 2, "30s", "")]),
            ("friday", [("Bulgarian Split Squat", 3, "12/leg", ""), ("Hanging Leg Raise", 2, "10", ""), ("Push-ups", 2, "AMRAP", ""), ("Jump Rope", 2, "2min", "")]),
        ]
    },
    # 5. Youth / Teens Foundation (3-Day)
    {
        "name": "Youth/Teens Foundation (3-Day)",
        "description": "Safe whole-body movement, confidence, and core strength for youth.",
        "fitness_level": "beginner",
        "goal": "basic_maintenance",
        "days": [
            ("monday", [("Squats (Back/Front)", 3, "15", "Bodyweight"), ("Push-ups", 2, "AMRAP", ""), ("Plank", 2, "40s", ""), ("Jump Rope", 1, "3min", "")]),
            ("wednesday", [("Lunges (Walking/Stationary)", 3, "12/leg", ""), ("Sit-ups / Crunches", 2, "15", ""), ("Medicine Ball Throws", 2, "10", ""), ("Jogging", 1, "6min", "")]),
            ("friday", [("Wall Sit", 2, "40s", ""), ("Push-ups", 2, "AMRAP", ""), ("Bear Crawl", 1, "30s", ""), ("Stretching", 1, "10min", "")]),
        ]
    },
    # 6. Lower-Upper-Lower HIIT (3-Day)
    {
        "name": "Lower-Upper-Lower HIIT (3-Day)",
        "description": "High-intensity intervals interspersed with major lifts; quick fat loss.",
        "fitness_level": "advanced",
        "goal": "weight_loss",
        "days": [
            ("monday", [("Squats (Back/Front)", 4, "10", ""), ("Jump Rope", 3, "2min", ""), ("Lunges (Walking/Stationary)", 3, "15", ""), ("Mountain Climbers", 2, "30s", "")]),
            ("wednesday", [("Push-ups", 3, "20", ""), ("Bench Press", 4, "10", ""), ("Pull-ups / Chin-ups", 3, "AMRAP", ""), ("Burpees", 2, "15", "")]),
            ("friday", [("Deadlift", 4, "8", ""), ("Bike Sprints", 3, "1min fast:2min easy", ""), ("Leg Press", 3, "12", ""), ("Plank", 2, "60s", "")]),
        ]
    },
    # 7. Classic Yoga-Mobility (3-Day)
    {
        "name": "Yoga & Mobility Routine (3-Day)",
        "description": "Flexibility, core control, and recovery—perfect for all levels.",
        "fitness_level": "beginner",
        "goal": "basic_maintenance",
        "days": [
            ("monday", [("Sun Salutation Flow", 3, "8", "Yoga flow"), ("Plank", 2, "60s", ""), ("Child\'s Pose", 1, "2min", ""), ("Seated Twist", 1, "1min", "")]),
            ("wednesday", [("Downward Dog", 2, "1min", ""), ("Cobra Stretch", 2, "1min", ""), ("Pigeon Pose", 1, "2min", ""), ("Russian Twists", 2, "15", "")]),
            ("friday", [("Cat-Cow", 2, "1min", ""), ("Plank", 2, "45s", ""), ("Hamstring Stretch", 1, "2min", ""), ("Thread the Needle", 1, "1min", "")]),
        ]
    },
    # 8. Post-Injury / Rehab Basic (3-Day)
    {
        "name": "Rehab & Active Recovery (3-Day)",
        "description": "Light, joint-friendly—consult physiotherapist for restrictions.",
        "fitness_level": "beginner",
        "goal": "basic_maintenance",
        "days": [
            ("monday", [("Leg Extension", 2, "12", ""), ("Chest Fly", 2, "12", ""), ("Seated Cable Row", 2, "12", ""), ("Plank", 1, "30s", "")]),
            ("wednesday", [("Glute Bridge", 2, "15", ""), ("Hamstring Curl", 2, "12", ""), ("Rear Delt Fly", 2, "12", ""), ("Stretching", 1, "10min", "")]),
            ("friday", [("Calf Raises (Standing/Seated)", 2, "15", ""), ("Push-ups", 2, "Knee", "Modified"), ("Lat Pulldown", 2, "12", ""), ("Foam Roll", 1, "10min", "")]),
        ]
    },
    # 9. Advanced Powerlifting Split (6-Day)
    {
        "name": "Powerlifting Advanced (6-Day)",
        "description": "Squat, bench, deadlift each twice per week—designed for strength.",
        "fitness_level": "advanced",
        "goal": "competition",
        "days": [
            ("monday", [("Squats (Back/Front)", 5, "5", ""), ("Leg Press", 4, "10", ""), ("Calf Raises (Standing/Seated)", 3, "15", "")]),
            ("tuesday", [("Bench Press", 5, "5", ""), ("Incline Bench Press", 3, "8", ""), ("Tricep Pushdown", 3, "10", "")]),
            ("wednesday", [("Deadlift", 5, "5", ""), ("Seated Cable Row", 3, "10", ""), ("Barbell Curl", 3, "10", "")]),
            ("thursday", [("Squats (Back/Front)", 3, "8", ""), ("Hamstring Curl", 3, "12", ""), ("Calf Raises (Standing/Seated)", 3, "15", "")]),
            ("friday", [("Bench Press", 3, "8", ""), ("Overhead Press (Barbell/Dumbbell)", 3, "8", ""), ("Tricep Pushdown", 3, "12", "")]),
            ("saturday", [("Deadlift", 3, "8", ""), ("T-Bar Row", 3, "10", ""), ("Dumbbell Curl", 2, "12", "")]),
        ]
    },
    # 10. Women's Athletic Total-Body Tone (5-Day)
    {
        "name": "Women's Athletic Total-Body Tone (5-Day)",
        "description": "For athletic women after full-body strength, toning, and variety.",
        "fitness_level": "medium",
        "goal": "basic_maintenance",
        "days": [
            ("monday", [("Squats (Back/Front)", 4, "12", ""), ("Push-ups", 3, "AMRAP", ""), ("Calf Raises (Standing/Seated)", 3, "20", ""), ("Russian Twists", 3, "20", "")]),
            ("tuesday", [("Bench Press", 4, "10", ""), ("Lat Pulldown", 3, "15", ""), ("Glute Bridge", 3, "15", ""), ("Plank", 2, "60s", "")]),
            ("wednesday", [("Deadlift", 4, "8", ""), ("Lunges (Walking/Stationary)", 3, "15/leg", ""), ("Sit-ups / Crunches", 2, "20", ""), ("Rear Delt Fly", 2, "15", "")]),
            ("thursday", [("Leg Press", 3, "15", ""), ("Overhead Press (Barbell/Dumbbell)", 3, "10", ""), ("Arnold Press", 2, "10", ""), ("Jump Rope", 2, "3min", "")]),
            ("friday", [("Push-ups", 3, "AMRAP", ""), ("Incline Bench Press", 3, "10", ""), ("Barbell Curl", 2, "12", ""), ("Hip Thrust", 2, "15", "")]),
        ]
    }
]

class Command(BaseCommand):
    help = "Seed complete workout data including fitness levels, goals, equipment, exercises, and templates"

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Starting to seed workout data...")
        
        # Create Fitness Levels
        fitness_levels = [
            ('beginner', 'Beginner'),
            ('medium', 'Medium'),
            ('advanced', 'Advanced'),
            ('master', 'Master'),
        ]
        
        for level_code, level_name in fitness_levels:
            fitness_level, created = FitnessLevel.objects.get_or_create(
                name=level_code,
                defaults={'description': f'{level_name} level fitness programming'}
            )
            if created:
                self.stdout.write(f"✅ Created fitness level: {level_name}")

        # Create Goals
        goals = [
            ('weight_loss', 'Weight Loss'),
            ('weight_gain', 'Weight Gain'),
            ('competition', 'Competition'),
            ('basic_maintenance', 'Basic Maintenance'),
        ]
        
        for goal_code, goal_name in goals:
            goal, created = Goal.objects.get_or_create(
                name=goal_code,
                defaults={'description': f'{goal_name} focused programming'}
            )
            if created:
                self.stdout.write(f"✅ Created goal: {goal_name}")

        # Create Equipment
        for name, category, description in EQUIPMENT_DATA:
            equipment, created = Equipment.objects.get_or_create(
                name=name,
                defaults={'category': category, 'description': description}
            )
            if created:
                self.stdout.write(f"✅ Created equipment: {name}")

        # Create Exercises
        for name, equipment_name, muscle_groups, instructions in EXERCISES_DATA:
            try:
                equipment = Equipment.objects.get(name=equipment_name)
                exercise, created = Exercise.objects.get_or_create(
                    name=name,
                    equipment=equipment,
                    defaults={
                        'muscle_groups': muscle_groups,
                        'instructions': instructions,
                        'safety_notes': 'Maintain proper form throughout the movement'
                    }
                )
                if created:
                    self.stdout.write(f"✅ Created exercise: {name}")
            except Equipment.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"❌ Equipment '{equipment_name}' not found for exercise '{name}'. Skipping."))

        # Create default trainer user with vendor_id = 1
        try:
            # Try to create trainer with vendor_id = 1
            trainer, created = User.objects.get_or_create(
                username='trainer_demo',
                defaults={
                    'email': 'trainer@example.com',
                    'first_name': 'Demo',
                    'last_name': 'Trainer',
                    'is_staff': True,
                    'vendor_id': 1,  # Use default vendor_id = 1
                }
            )
            if created:
                trainer.set_password('password123')
                trainer.save()
                self.stdout.write("✅ Created demo trainer user with vendor_id = 1")
            else:
                self.stdout.write("📋 Using existing trainer user")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating trainer user: {e}"))
            self.stdout.write(self.style.WARNING("🔄 Trying to use existing staff user..."))
            try:
                trainer = User.objects.filter(is_staff=True).first()
                if not trainer:
                    self.stdout.write(self.style.ERROR("❌ No staff user found. Please create a trainer user first through admin."))
                    return
                self.stdout.write(f"📋 Using existing trainer: {trainer.username}")
            except Exception as e2:
                self.stdout.write(self.style.ERROR(f"❌ Error getting existing trainer: {e2}"))
                return

        # Create Workout Templates
        templates_created = 0
        templates_skipped = 0
        
        for tpl in TEMPLATES:
            try:
                fitness_level = FitnessLevel.objects.get(name=tpl["fitness_level"])
                goal = Goal.objects.get(name=tpl["goal"])
                
                template, created = WeeklyTemplate.objects.get_or_create(
                    name=tpl["name"],
                    defaults={
                        "description": tpl["description"],
                        "trainer": trainer,
                        "fitness_level": fitness_level,
                        "goal": goal,
                        "total_sessions_per_week": len(tpl["days"]),
                        "estimated_duration_per_session": "45-60min"
                    }
                )
                
                if created:
                    templates_created += 1
                    self.stdout.write(f"✅ Created template: {tpl['name']}")
                    
                    # Create day templates and activities
                    for day_name, workouts in tpl["days"]:
                        # Check if it's a rest day
                        is_rest_day = len(workouts) == 0
                        
                        day_template = DayTemplate.objects.create(
                            weekly_template=template,
                            day=day_name,
                            name=f"{day_name.title()} Workout" if not is_rest_day else "Rest Day",
                            is_rest_day=is_rest_day,
                            estimated_duration="45-60min" if not is_rest_day else "0min"
                        )
                        
                        # Create activities for this day
                        for order, (exercise_name, sets, reps, notes) in enumerate(workouts, 1):
                            try:
                                exercise = Exercise.objects.get(name=exercise_name)
                                
                                # Handle different types of sets values
                                try:
                                    sets_int = int(sets)
                                except (ValueError, TypeError):
                                    sets_int = 1
                                
                                ActivityTemplate.objects.create(
                                    day_template=day_template,
                                    exercise=exercise,
                                    order=order,
                                    sets=sets_int,
                                    reps=str(reps),
                                    weight_percentage="",
                                    estimated_duration="10min",
                                    form_cues=notes if notes else "Focus on proper form",
                                    rpe_target="RPE 7-8",
                                    activity_type='cardio' if exercise.equipment and 'cardio' in exercise.equipment.category.lower() else 'exercise'
                                )
                                
                            except Exercise.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"❌ Exercise '{exercise_name}' not found. Skipping."))
                                continue
                            except Exception as ex:
                                self.stdout.write(self.style.WARNING(f"❌ Error creating activity '{exercise_name}': {ex}"))
                                continue
                else:
                    templates_skipped += 1
                    self.stdout.write(f"📋 Template already exists: {tpl['name']}")
                
            except (FitnessLevel.DoesNotExist, Goal.DoesNotExist) as e:
                self.stdout.write(self.style.ERROR(f"❌ Missing fitness level or goal for template '{tpl['name']}': {e}"))
                templates_skipped += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error creating template '{tpl['name']}': {e}"))
                templates_skipped += 1

        # Final summary
        self.stdout.write(self.style.SUCCESS("🎉 Successfully completed seeding workout data!"))
        self.stdout.write(f"📊 Final Statistics:")
        self.stdout.write(f"   - Fitness Levels: {FitnessLevel.objects.count()}")
        self.stdout.write(f"   - Goals: {Goal.objects.count()}")
        self.stdout.write(f"   - Equipment Types: {Equipment.objects.count()}")
        self.stdout.write(f"   - Exercises: {Exercise.objects.count()}")
        self.stdout.write(f"   - Weekly Templates: {WeeklyTemplate.objects.count()} (Created: {templates_created}, Skipped: {templates_skipped})")
        self.stdout.write(f"   - Day Templates: {DayTemplate.objects.count()}")
        self.stdout.write(f"   - Activity Templates: {ActivityTemplate.objects.count()}")
        
        if templates_created > 0:
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully created {templates_created} new workout templates!"))
        if templates_skipped > 0:
            self.stdout.write(f"📋 Skipped {templates_skipped} existing templates")
