# Fit Fusion Data Dictionary

This document describes the database schema for the Fit Fusion application (`backend/app/models.py`).

---

## Table: `User`

| Column Name         | Data Type    | Constraints                             | Description                                                                          |
|---------------------|--------------|------------------------------------------|--------------------------------------------------------------------------------------|
| `id`                | Integer      | Primary Key, Auto-increment             | Unique identifier for each user.                                                     |
| `username`          | String(80)   | Unique, Not Null                        | Display name chosen by the user.                                                     |
| `email`             | String(120)  | Unique, Not Null                        | User's email address (used for authentication).                                      |
| `password`          | String(256)  | Not Null                                | PBKDF2–SHA256 hashed password.                                                       |
| `age`               | Integer      | Not Null                                | User's age in years.                                                                 |
| `gender`            | String(10)   | Not Null                                | "male" or "female" (affects BMR calculation).                                        |
| `height`            | Float        | Not Null                                | Height in meters (converted to/from feet & inches in the UI).                       |
| `weight`            | Float        | Not Null                                | Weight in kilograms (converted to/from pounds in the UI).                            |
| `activity_level`    | String(20)   | Not Null                                | One of: `sedentary`, `light`, `moderate`, `active`, `very_active`.                   |
| `workout_preference`| String(20)   | Nullable                                | E.g. `cardio`, `weight_training`, `strength_training`.                               |
| `goal`              | String(50)   | Nullable                                | Free-text fitness goal (e.g., "Lose weight", "Build muscle").                        |
| `created_at`        | DateTime     | Default = UTC now                       | Account creation timestamp.                                                          |

## Table: `WorkoutLog`

| Column Name    | Data Type   | Constraints                      | Description                                                  |
|----------------|-------------|-----------------------------------|----------------------------------------------------------------|
| `id`           | Integer     | Primary Key, Auto-increment      | Unique identifier for each workout entry.                    |
| `user_id`      | Integer     | Foreign Key → `User.id`, Not Null | References the user who logged this workout.                 |
| `workout_type` | String(50)  | Not Null                         | Category, e.g. "Cardio", "Weight Training", "Strength Training". |
| `exercise`     | String(100) | Not Null                         | Name of the exercise (e.g. "Squat", "Bench Press").           |
| `sets`         | Integer     | Not Null                         | Number of sets performed.                                    |
| `reps`         | Integer     | Not Null                         | Number of repetitions per set.                                |
| `weight`       | Float       | Nullable                         | Weight used in kilograms (converted from pounds in the UI).  |
| `date`         | DateTime    | Default = UTC now                | Timestamp for when this workout was logged.                  |

## Table: `Goal`

| Column Name       | Data Type   | Constraints                       | Description                                                          |
|-------------------|-------------|-------------------------------------|-------------------------------------------------------------------------|
| `id`              | Integer     | Primary Key, Auto-increment        | Unique identifier for each goal.                                     |
| `user_id`         | Integer     | Foreign Key → `User.id`, Not Null   | References the goal's owner.                                         |
| `goal_type`       | String(30)  | Not Null                            | `weight`, `strength`, `workout_count`, or `custom`.                  |
| `title`           | String(150) | Not Null                            | Human-readable goal description, e.g. "Bench 225 lbs".               |
| `target_value`    | Float       | Not Null                            | Value that marks the goal complete.                                  |
| `start_value`     | Float       | Nullable                            | Value at goal creation, used to compute progress %.                  |
| `current_value`   | Float       | Nullable                            | Latest tracked value.                                                |
| `unit`            | String(20)  | Nullable                            | Unit label (lbs, reps, workouts, etc.).                               |
| `target_date`     | Date        | Nullable                            | Optional deadline.                                                   |
| `status`          | String(20)  | Default = `active`                  | `active` or `completed` (auto-set when target is reached).           |
| `created_at`      | DateTime    | Default = UTC now                   | When the goal was created.                                           |

## Table: `Exercise`

| Column Name    | Data Type   | Constraints             | Description                                                  |
|----------------|-------------|---------------------------|------------------------------------------------------------------|
| `id`           | Integer     | Primary Key, Auto-increment | Unique identifier for each exercise.                        |
| `name`         | String(100) | Unique, Not Null          | Exercise name (e.g. "Bench Press").                          |
| `category`     | String(50)  | Not Null                  | "Cardio", "Weight Training", or "Strength Training".         |
| `muscle_group` | String(50)  | Not Null                  | Primary muscle group targeted.                               |
| `equipment`    | String(50)  | Nullable                  | Equipment required.                                          |
| `difficulty`   | String(20)  | Nullable                  | "Beginner", "Intermediate", or "Advanced".                   |
| `instructions` | Text        | Nullable                  | Short form-cue description.                                  |

Seeded at startup from `backend/app/seed_data.py` if the table is empty.

## Table: `NutritionLog`

| Column Name  | Data Type   | Constraints                       | Description                                     |
|--------------|-------------|-------------------------------------|--------------------------------------------------|
| `id`         | Integer     | Primary Key, Auto-increment        | Unique identifier for each food entry.          |
| `user_id`    | Integer     | Foreign Key → `User.id`, Not Null   | References the logging user.                    |
| `food_name`  | String(150) | Not Null                            | Name of the food/meal logged.                   |
| `calories`   | Float       | Not Null                            | Calories for this entry.                        |
| `protein`    | Float       | Nullable                            | Grams of protein.                               |
| `carbs`      | Float       | Nullable                            | Grams of carbohydrates.                         |
| `fat`        | Float       | Nullable                            | Grams of fat.                                   |
| `meal_type`  | String(20)  | Nullable                            | `breakfast`, `lunch`, `dinner`, or `snack`.      |
| `date`       | Date        | Default = today                     | Day this entry counts toward.                   |

---

## Relationships

- **User → WorkoutLog**: 1-to-many, cascade delete.
- **User → Goal**: 1-to-many, cascade delete.
- **User → NutritionLog**: 1-to-many, cascade delete.

## Conversion & Usage Notes

- **Height & Weight** — stored in meters/kilograms; the API converts to/from feet-inches and pounds at the edges (`backend/app/utils.py`) so the frontend always works in US units.
- **BMI / TDEE** — computed server-side (`calculate_bmi`, `calculate_tdee` in `backend/app/utils.py`) using the Mifflin–St Jeor formula and returned by `GET /api/workouts/dashboard`.
- **Goal progress** — `Goal.progress_percent()` computes `(current - start) / (target - start) * 100`, clamped to 0–100.
