# Python shell script for seeding fitness programming data
# Run this in Django shell: python manage.py shell

from workout.models import *
from django.contrib.auth import get_user_model
import json

User = get_user_model()

def create_seed_data():
    print("Starting to seed fitness programming data...")
    
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
            print(f"Created fitness level: {level_name}")
    
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
            print(f"Created goal: {goal_name}")
    
    # Create Equipment
    equipment_data = [
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
    
    for name, category, description in equipment_data:
        equipment, created = Equipment.objects.get_or_create(
            name=name,
            defaults={'category': category, 'description': description}
        )
        if created:
            print(f"Created equipment: {name}")
    
    # Create Exercises
    exercises_data = [
        # Barbell exercises
        ('Back Squat', 'Barbell', 'Quadriceps, Glutes, Hamstrings', 'Stand with barbell on upper back, squat down keeping chest up, drive through heels to stand'),
        ('Bench Press', 'Barbell', 'Chest, Triceps, Front Deltoids', 'Lie on bench, grip barbell shoulder-width, lower to chest, press up'),
        ('Deadlift', 'Barbell', 'Hamstrings, Glutes, Erector Spinae, Traps', 'Stand with barbell, hinge at hips, keep back straight, lift by extending hips'),
        ('Overhead Press', 'Barbell', 'Shoulders, Triceps, Core', 'Stand with barbell at shoulder level, press overhead keeping core tight'),
        ('Barbell Row', 'Barbell', 'Latissimus Dorsi, Rhomboids, Rear Deltoids', 'Hinge at hips, pull barbell to lower chest, squeeze shoulder blades'),
        ('Front Squat', 'Barbell', 'Quadriceps, Core, Upper Back', 'Hold barbell in front rack position, squat keeping torso upright'),
        ('Romanian Deadlift', 'Barbell', 'Hamstrings, Glutes, Lower Back', 'Hold barbell, hinge at hips keeping legs slightly bent'),
        ('Close-grip Bench Press', 'Barbell', 'Triceps, Chest, Front Deltoids', 'Bench press with narrow grip focusing on triceps'),
        
        # Dumbbell exercises
        ('Dumbbell Bench Press', 'Dumbbell', 'Chest, Triceps, Front Deltoids', 'Lie on bench with dumbbells, press up with full range of motion'),
        ('Incline Dumbbell Press', 'Dumbbell', 'Upper Chest, Front Deltoids, Triceps', 'Press dumbbells on inclined bench targeting upper chest'),
        ('Dumbbell Shoulder Press', 'Dumbbell', 'Shoulders, Triceps', 'Sit or stand, press dumbbells overhead'),
        ('One-arm Dumbbell Row', 'Dumbbell', 'Latissimus Dorsi, Rhomboids, Biceps', 'Support on bench, row dumbbell to hip'),
        ('Dumbbell RDL', 'Dumbbell', 'Hamstrings, Glutes', 'Hold dumbbells, hinge at hips with slight knee bend'),
        ('Lateral Raise', 'Dumbbell', 'Side Deltoids', 'Raise dumbbells to sides until parallel to floor'),
        ('Goblet Squat', 'Dumbbell', 'Quadriceps, Glutes', 'Hold dumbbell at chest, squat keeping torso upright'),
        ('Arnold Press', 'Dumbbell', 'Shoulders, Triceps', 'Rotating shoulder press movement'),
        
        # Machine exercises
        ('Leg Press', 'Machine', 'Quadriceps, Glutes', 'Sit in leg press machine, press weight with full range of motion'),
        ('Lat Pulldown', 'Machine', 'Latissimus Dorsi, Biceps, Rhomboids', 'Pull bar down to upper chest, squeeze shoulder blades'),
        ('Chest Press Machine', 'Machine', 'Chest, Triceps, Front Deltoids', 'Push handles forward with controlled movement'),
        ('Seated Row Machine', 'Machine', 'Latissimus Dorsi, Rhomboids, Rear Deltoids', 'Pull handles to torso, squeeze shoulder blades'),
        ('Leg Curl', 'Machine', 'Hamstrings', 'Curl heels toward glutes while lying or seated'),
        ('Leg Extension', 'Machine', 'Quadriceps', 'Extend legs against resistance'),
        ('Seated Calf Raise', 'Machine', 'Calves', 'Raise heels while seated with weight on thighs'),
        ('Machine Press', 'Machine', 'Chest, Triceps', 'General machine press movement'),
        
        # Cable exercises
        ('Cable Row', 'Cable', 'Latissimus Dorsi, Rhomboids, Rear Deltoids', 'Pull cable to torso with neutral spine'),
        ('Face Pull', 'Cable', 'Rear Deltoids, Rhomboids', 'Pull cable to face level, separate handles'),
        ('Cable Fly', 'Cable', 'Chest, Front Deltoids', 'Bring cables together in fly motion'),
        ('Triceps Pushdown', 'Cable', 'Triceps', 'Push cable down extending elbows'),
        ('Cable Pullover', 'Cable', 'Latissimus Dorsi, Serratus', 'Pull cable overhead in arc motion'),
        ('Pallof Press', 'Cable', 'Core, Obliques', 'Hold cable at chest, resist rotation'),
        
        # Bodyweight exercises
        ('Push-up', 'Bodyweight', 'Chest, Triceps, Core', 'Lower body to floor, push up maintaining straight line'),
        ('Incline Push-up', 'Bodyweight', 'Chest, Triceps', 'Push-ups with hands elevated on bench'),
        ('Modified Push-up', 'Bodyweight', 'Chest, Triceps', 'Push-ups from knees or inclined surface'),
        ('Pull-up', 'Bodyweight', 'Latissimus Dorsi, Biceps', 'Hang from bar, pull up until chin over bar'),
        ('Assisted Pull-up', 'Bodyweight', 'Latissimus Dorsi, Biceps', 'Pull-ups with assistance from machine or band'),
        ('Plank', 'Bodyweight', 'Core, Shoulders', 'Hold straight line position on forearms'),
        ('Side Plank', 'Bodyweight', 'Obliques, Core', 'Hold side position on one forearm'),
        ('Glute Bridge', 'Bodyweight', 'Glutes, Hamstrings', 'Lie on back, lift hips by squeezing glutes'),
        ('Single-leg Glute Bridge', 'Bodyweight', 'Glutes, Hamstrings', 'Glute bridge with one leg extended'),
        ('Hip Thrust', 'Bodyweight', 'Glutes, Hamstrings', 'Shoulders on bench, thrust hips up'),
        ('Walking Lunge', 'Bodyweight', 'Quadriceps, Glutes', 'Step forward into lunge, alternate legs'),
        ('Bulgarian Split Squat', 'Bodyweight', 'Quadriceps, Glutes', 'Rear foot elevated lunge'),
        ('Step-ups', 'Bodyweight', 'Quadriceps, Glutes', 'Step up onto bench or platform'),
        ('Wall Sit', 'Bodyweight', 'Quadriceps, Glutes', 'Sit against wall with thighs parallel to floor'),
        ('Mountain Climbers', 'Bodyweight', 'Core, Shoulders, Cardio', 'Rapid alternating knee to chest in plank position'),
        ('Dead Bug', 'Bodyweight', 'Core, Hip Flexors', 'Lie on back, extend opposite arm and leg'),
        ('Bird Dog', 'Bodyweight', 'Core, Lower Back', 'On hands and knees, extend opposite arm and leg'),
        ('Back Extension', 'Bodyweight', 'Lower Back, Glutes', 'Extend spine from prone position'),
        ('Farmer Carry', 'Bodyweight', 'Grip, Core, Traps', 'Walk carrying heavy weights at sides'),
        ('Bodyweight Squat', 'Bodyweight', 'Quadriceps, Glutes', 'Squat without added weight'),
        ('Split Squat', 'Bodyweight', 'Quadriceps, Glutes', 'Static lunge position'),
        ('Ab Wheel', 'Bodyweight', 'Core, Shoulders', 'Roll wheel forward extending body, return to start'),
        ('Dips', 'Bodyweight', 'Triceps, Chest', 'Lower body between parallel bars, push up'),
        
        # Cardio exercises
        ('Treadmill Walk', 'Cardio Equipment', 'Cardiovascular', 'Walk on treadmill at incline'),
        ('Stationary Bike', 'Cardio Equipment', 'Cardiovascular, Quadriceps', 'Cycle at moderate to high intensity'),
        ('Elliptical', 'Cardio Equipment', 'Cardiovascular, Full Body', 'Low impact cardio movement'),
        ('Rowing Machine', 'Cardio Equipment', 'Cardiovascular, Back, Legs', 'Full body rowing motion'),
        ('Swimming', 'Cardio Equipment', 'Cardiovascular, Full Body', 'Swimming laps'),
        
        # Specialty exercises
        ('Paused Squat', 'Barbell', 'Quadriceps, Glutes', 'Squat with pause at bottom'),
        ('Spoto Bench', 'Barbell', 'Chest, Triceps', 'Bench press with pause above chest'),
        ('Deficit Deadlift', 'Barbell', 'Hamstrings, Glutes', 'Deadlift standing on platform'),
        ('Hammer Curl', 'Dumbbell', 'Biceps, Forearms', 'Curl with neutral grip'),
        ('EZ Curl', 'Barbell', 'Biceps', 'Bicep curl with EZ bar'),
        ('Rear Delt Fly', 'Dumbbell', 'Rear Deltoids, Rhomboids', 'Reverse fly movement'),
        ('T-bar Row', 'Barbell', 'Latissimus Dorsi, Rhomboids', 'Row using T-bar or landmine'),
        ('High-bar Squat', 'Barbell', 'Quadriceps, Glutes', 'Squat with bar high on traps'),
        ('Hack Squat', 'Machine', 'Quadriceps, Glutes', 'Squat on hack squat machine'),
        ('Chest-supported Row', 'Machine', 'Latissimus Dorsi, Rhomboids', 'Row with chest support'),
    ]
    
    for name, equipment_name, muscle_groups, instructions in exercises_data:
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
                print(f"Created exercise: {name}")
        except Equipment.DoesNotExist:
            print(f"Equipment {equipment_name} not found for exercise {name}")
    
    # Create a default trainer user if doesn't exist
    trainer, created = User.objects.get_or_create(
        username='trainer_demo',
        defaults={
            'email': 'trainer@example.com',
            'first_name': 'Demo',
            'last_name': 'Trainer',
            'is_staff': True
        }
    )
    if created:
        trainer.set_password('password123')
        trainer.save()
        print("Created demo trainer user")
    
    # Create weekly templates
    create_beginner_templates(trainer)
    create_medium_templates(trainer)
    create_advanced_templates(trainer)
    create_master_templates(trainer)
    
    print("Seeding completed successfully!")

def create_beginner_templates(trainer):
    """Create all beginner level templates"""
    print("Creating Beginner level templates...")
    
    # Get fitness level and goals
    beginner = FitnessLevel.objects.get(name='beginner')
    weight_loss = Goal.objects.get(name='weight_loss')
    weight_gain = Goal.objects.get(name='weight_gain')
    competition = Goal.objects.get(name='competition')
    maintenance = Goal.objects.get(name='basic_maintenance')
    
    # 1.1 Weight Loss (Beginner)
    template = WeeklyTemplate.objects.create(
        trainer=trainer,
        name="Beginner Weight Loss Program",
        fitness_level=beginner,
        goal=weight_loss,
        description="Build habit, full-body circuits, high NEAT, moderate cardio. 4 full-body strength + 2 cardio sessions.",
        total_sessions_per_week=6,
        estimated_duration_per_session="45-55min"
    )
    
    # Monday (Full-Body Circuit A)
    monday = DayTemplate.objects.create(
        weekly_template=template,
        day='monday',
        name='Full-Body Circuit A',
        estimated_duration='45-55min'
    )
    
    activities = [
        ('Goblet Squat', 3, '10-12', '', '12-15min', 'Keep chest up, full depth'),
        ('Incline Push-up', 3, '8-12', '', '10min', 'Use bench to scale'),
        ('Seated Row Machine', 3, '10-12', '', '10min', 'Squeeze scapula'),
        ('Dumbbell RDL', 3, '10', '', '10min', 'Neutral spine'),
        ('Plank', 3, '30-45s', '', '8min', 'Brace core'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=monday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 6-7'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")
    
    # Tuesday (Cardio Intervals)
    tuesday = DayTemplate.objects.create(
        weekly_template=template,
        day='tuesday',
        name='Cardio Intervals, Low Impact',
        estimated_duration='30-40min'
    )
    
    cardio_activities = [
        ('Treadmill Walk', 1, '5min', '', '5min', 'Warm-up pace'),
        ('Stationary Bike', 10, '1min brisk/1min easy', '', '20min', 'Interval training'),
        ('Treadmill Walk', 1, '5-10min', '', '10min', 'Cool-down pace'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(cardio_activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=tuesday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                activity_type='cardio'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")
    
    # Continue with remaining days...
    create_remaining_beginner_days(template)
    
    # Create other beginner templates
    create_beginner_weight_gain(trainer, beginner, weight_gain)
    create_beginner_competition(trainer, beginner, competition)
    create_beginner_maintenance(trainer, beginner, maintenance)

def create_remaining_beginner_days(template):
    """Create remaining days for beginner weight loss template"""
    
    # Wednesday (Full-Body Circuit B)
    wednesday = DayTemplate.objects.create(
        weekly_template=template,
        day='wednesday',
        name='Full-Body Circuit B',
        estimated_duration='45-55min'
    )
    
    wed_activities = [
        ('Step-ups', 3, '10/leg', '', '12min', 'Knee tracks toes'),
        ('Lat Pulldown', 3, '10-12', '', '10min', 'Control down'),
        ('Dumbbell Shoulder Press', 3, '8-10', '', '10min', 'No arch'),
        ('Glute Bridge', 3, '12-15', '', '8min', 'Pause at top'),
        ('Dead Bug', 3, '10/side', '', '8min', 'Low back down'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(wed_activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=wednesday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 6-7'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")
    
    # Thursday (Full-Body Circuit C)
    thursday = DayTemplate.objects.create(
        weekly_template=template,
        day='thursday',
        name='Full-Body Circuit C',
        estimated_duration='45-55min'
    )
    
    thu_activities = [
        ('Leg Press', 3, '10-12', '', '10min', 'Full ROM'),
        ('Chest Press Machine', 3, '8-10', '', '10min', 'Tempo 2-1-2'),
        ('Cable Row', 3, '10-12', '', '10min', 'Neutral wrist'),
        ('Back Extension', 3, '12', '', '8min', 'Controlled'),
        ('Farmer Carry', 4, '30m', '', '8min', 'Upright posture'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(thu_activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=thursday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 6-7'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")
    
    # Friday (Full-Body Circuit D)
    friday = DayTemplate.objects.create(
        weekly_template=template,
        day='friday',
        name='Full-Body Circuit D',
        estimated_duration='40-50min'
    )
    
    fri_activities = [
        ('Wall Sit', 3, '45-60s', '', '8min', 'Back flat against wall'),
        ('Modified Push-up', 3, '10-12', '', '10min', 'Focus on form'),
        ('Lat Pulldown', 3, '8-10', '', '10min', 'Full range of motion'),
        ('Single-leg Glute Bridge', 3, '10/leg', '', '8min', 'Control the movement'),
        ('Side Plank', 3, '20-30s/side', '', '8min', 'Maintain straight line'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(fri_activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=friday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 6-7'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")
    
    # Saturday (Steady-State Cardio)
    saturday = DayTemplate.objects.create(
        weekly_template=template,
        day='saturday',
        name='Steady-State Cardio',
        estimated_duration='35-45min'
    )
    
    ActivityTemplate.objects.create(
        day_template=saturday,
        exercise=Exercise.objects.get(name='Stationary Bike'),
        order=1,
        sets=1,
        reps='35-45min',
        estimated_duration='35-45min',
        form_cues='Conversational pace',
        activity_type='cardio'
    )
    
    # Sunday - Rest Day
    sunday = DayTemplate.objects.create(
        weekly_template=template,
        day='sunday',
        name='Rest Day',
        is_rest_day=True,
        estimated_duration='0min',
        notes='Complete rest day for recovery'
    )

def create_beginner_weight_gain(trainer, fitness_level, goal):
    """Create beginner weight gain template"""
    template = WeeklyTemplate.objects.create(
        trainer=trainer,
        name="Beginner Weight Gain Program",
        fitness_level=fitness_level,
        goal=goal,
        description="Hypertrophy foundation, increased training frequency, adequate calories/protein. 4 full-body + 2 light cardio/recovery sessions.",
        total_sessions_per_week=6,
        estimated_duration_per_session="50-60min"
    )
    
    # Monday (Full-Body A)
    monday = DayTemplate.objects.create(
        weekly_template=template,
        day='monday',
        name='Full-Body A',
        estimated_duration='50-60min'
    )
    
    activities = [
        ('Back Squat', 4, '8', '', '12-15min', 'Full depth, chest up'),
        ('Bench Press', 4, '8', '', '12-15min', 'Control the weight'),
        ('Lat Pulldown', 3, '10', '', '10min', 'Squeeze at bottom'),
        ('Dumbbell RDL', 3, '10', '', '10min', 'Hinge at hips'),
        ('Seated Calf Raise', 3, '12-15', '', '5-8min', 'Full range'),
        ('Plank', 3, '45s', '', '5min', 'Hold steady'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=monday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 6-7'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")

def create_beginner_competition(trainer, fitness_level, goal):
    """Create beginner competition template"""
    template = WeeklyTemplate.objects.create(
        trainer=trainer,
        name="Beginner Competition Program",
        fitness_level=fitness_level,
        goal=goal,
        description="Technique-first, mock attempts light, basic strength skill development. 4 technique days + 2 GPP sessions.",
        total_sessions_per_week=6,
        estimated_duration_per_session="60min"
    )
    
    # Monday (Squat Focus + Bench)
    monday = DayTemplate.objects.create(
        weekly_template=template,
        day='monday',
        name='Squat Focus + Bench',
        estimated_duration='60min'
    )
    
    activities = [
        ('Back Squat', 5, '3', '@RPE6', '15min', 'Focus on technique'),
        ('Bench Press', 4, '3', '@RPE6', '12min', 'Paused reps'),
        ('Paused Squat', 3, '3', '', '10min', '2 second pause'),
        ('Close-grip Bench Press', 3, '5', '', '10min', 'Tricep focus'),
        ('Pallof Press', 3, '12', '', '10min', 'Anti-rotation'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=monday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 6'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")

def create_beginner_maintenance(trainer, fitness_level, goal):
    """Create beginner maintenance template"""
    template = WeeklyTemplate.objects.create(
        trainer=trainer,
        name="Beginner Basic Maintenance Program",
        fitness_level=fitness_level,
        goal=goal,
        description="Health, posture, consistency, low soreness. 4 strength + 2 light cardio sessions.",
        total_sessions_per_week=6,
        estimated_duration_per_session="45-55min"
    )
    
    # Monday (Strength A)
    monday = DayTemplate.objects.create(
        weekly_template=template,
        day='monday',
        name='Strength A',
        estimated_duration='45-55min'
    )
    
    activities = [
        ('Goblet Squat', 3, '10', '', '10min', 'Controlled movement'),
        ('Incline Push-up', 3, '8-10', '', '10min', 'Full range'),
        ('Seated Row Machine', 3, '10-12', '', '10min', 'Squeeze back'),
        ('Glute Bridge', 3, '12-15', '', '8min', 'Pause at top'),
        ('Plank', 3, '45s', '', '8min', 'Maintain form'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=monday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 5-6'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")

def create_medium_templates(trainer):
    """Create medium level templates"""
    print("Creating Medium level templates...")
    
    medium = FitnessLevel.objects.get(name='medium')
    weight_loss = Goal.objects.get(name='weight_loss')
    weight_gain = Goal.objects.get(name='weight_gain')
    competition = Goal.objects.get(name='competition')
    maintenance = Goal.objects.get(name='basic_maintenance')
    
    # Medium Weight Loss
    template = WeeklyTemplate.objects.create(
        trainer=trainer,
        name="Medium Weight Loss Program",
        fitness_level=medium,
        goal=weight_loss,
        description="Calorie burn with quality lifts, mixed intervals, higher training frequency. 4 strength + 2 conditioning sessions.",
        total_sessions_per_week=6,
        estimated_duration_per_session="60-70min"
    )
    
    # Add sample day for medium level
    monday = DayTemplate.objects.create(
        weekly_template=template,
        day='monday',
        name='Lower Power',
        estimated_duration='60-70min'
    )
    
    activities = [
        ('Back Squat', 4, '6-8', '', '15min', 'Explosive up, controlled down'),
        ('Romanian Deadlift', 4, '8', '', '12min', 'Hip hinge pattern'),
        ('Walking Lunge', 3, '10/leg', '', '10min', 'Alternating legs'),
        ('Leg Curl', 3, '12', '', '8min', 'Controlled movement'),
        ('Seated Calf Raise', 3, '15', '', '8min', 'Full range of motion'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=monday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 7-8'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")

def create_advanced_templates(trainer):
    """Create advanced level templates"""
    print("Creating Advanced level templates...")
    
    advanced = FitnessLevel.objects.get(name='advanced')
    weight_loss = Goal.objects.get(name='weight_loss')
    
    # Advanced Weight Loss
    template = WeeklyTemplate.objects.create(
        trainer=trainer,
        name="Advanced Weight Loss Program",
        fitness_level=advanced,
        goal=weight_loss,
        description="Preserve strength, increase intensity via density and intervals. 4 strength + 2 high-intensity conditioning.",
        total_sessions_per_week=6,
        estimated_duration_per_session="65-75min"
    )
    
    # Add sample day
    monday = DayTemplate.objects.create(
        weekly_template=template,
        day='monday',
        name='Lower Strength',
        estimated_duration='65-75min'
    )
    
    activities = [
        ('Back Squat', 5, '4', '@75-80%', '15min', 'Heavy singles focus'),
        ('Romanian Deadlift', 4, '6-8', '', '12min', 'Hamstring emphasis'),
        ('Split Squat', 3, '8/leg', '', '10min', 'Single leg strength'),
        ('Leg Curl', 3, '12', '', '8min', 'Isolation work'),
        ('Ab Wheel', 3, '10', '', '8min', 'Core stability'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=monday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 8-9'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")

def create_master_templates(trainer):
    """Create master level templates"""
    print("Creating Master level templates...")
    
    master = FitnessLevel.objects.get(name='master')
    weight_loss = Goal.objects.get(name='weight_loss')
    
    # Master Weight Loss
    template = WeeklyTemplate.objects.create(
        trainer=trainer,
        name="Master Weight Loss Program",
        fitness_level=master,
        goal=weight_loss,
        description="5 high-intensity lifts + 1 metabolic session; maximum efficiency.",
        total_sessions_per_week=6,
        estimated_duration_per_session="70-80min"
    )
    
    # Add sample day
    monday = DayTemplate.objects.create(
        weekly_template=template,
        day='monday',
        name='Lower Power',
        estimated_duration='70-80min'
    )
    
    activities = [
        ('Back Squat', 6, '3', '@80-85%', '20min', 'Maximum power output'),
        ('Romanian Deadlift', 4, '5-6', '', '15min', 'Speed and power'),
        ('Split Squat', 3, '8', '', '12min', 'Unilateral strength'),
        ('Ab Wheel', 3, '10', '', '10min', 'Advanced core work'),
    ]
    
    for i, (exercise_name, sets, reps, weight, duration, cues) in enumerate(activities, 1):
        try:
            exercise = Exercise.objects.get(name=exercise_name)
            ActivityTemplate.objects.create(
                day_template=monday,
                exercise=exercise,
                order=i,
                sets=sets,
                reps=reps,
                weight_percentage=weight,
                estimated_duration=duration,
                form_cues=cues,
                rpe_target='RPE 8-9'
            )
        except Exercise.DoesNotExist:
            print(f"Exercise not found: {exercise_name}")

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Seeds fitness programming data into the database."

    def handle(self, *args, **options):
        # import your function
        create_seed_data()
        self.stdout.write(self.style.SUCCESS('Seeding completed successfully.'))
