# Meal & Macro Tracker
#### Video Demo: <URL HERE>
#### Description:

## Overview
Meal & Macro Tracker is a web application built with Flask that helps users track their daily food intake and macronutrient consumption (protein, carbohydrates, and fats). The application allows users to set daily macronutrient goals and monitor their progress throughout the day.

## Features

### User Authentication
- **Registration System**: New users can create an account with a username and password
- **Secure Login**: Passwords are hashed using Werkzeug's security functions
- **Differentiated Error Messages**: The login system provides specific feedback:
  - "The user doesn't exists" when the username is not registered
  - "Incorrect password" when the password is wrong for an existing user
  - This improves user experience by clearly indicating the issue
- **Session Management**: Users remain logged in using Flask sessions
- **Protected Routes**: All main features require authentication using the `@login_required` decorator

### Goal Setting
- Users can set daily macronutrient goals for:
  - Protein (grams)
  - Carbohydrates (grams)
  - Fats (grams)
  - Calories (optional)
- Goals can be updated at any time
- The system stores the history of goal changes

### Meal Tracking
- **Food Database**: Pre-populated with common foods and their macronutrient values per 100g
- **Custom Food Creation**: Users can add their own foods to the database with:
  - Custom food names (e.g., "Frutilla", "Mango", etc.)
  - Macronutrient values per 100g for protein, carbs, and fats
  - Validation to prevent invalid entries:
    - Each macronutrient must be between 0 and 100 grams
    - The sum of all macros cannot exceed 100g per 100g of food
    - Duplicate food names are not allowed (case-insensitive check)
    - Negative values are not permitted
- **Meal Logging**: Users can:
  - Select a food from the database (including their custom foods)
  - Enter the amount consumed in grams
  - Automatically calculate macronutrients and calories
- **Daily View**: All meals are displayed for the current day with totals
- **Automatic Calculations**: The system calculates:
  - Protein: grams × (protein_100g / 100)
  - Carbs: grams × (carbs_100g / 100)
  - Fats: grams × (fat_100g / 100)
  - Calories: (protein × 4) + (carbs × 4) + (fat × 9)

### Dashboard
- **Real-time Progress**: Shows current consumption vs. daily goals
- **Visual Progress Bars**: For each macronutrient (protein, carbs, fats, calories)
- **Percentage Completion**: Displays how close the user is to their goals
- **Color-coded Cards**: Each macronutrient has its own color for easy identification:
  - Green for Protein
  - Blue for Carbohydrates
  - Yellow for Fats
  - Red for Calories
  
- **Quick Actions**: Easy access to add meals, set goals, or log weight

### Weight Tracking
- **Weight Logging**: Users can record their weight in kilograms with decimal precision
- **Historical Data**: View the last 30 weight entries
- **Change Tracking**: Automatically calculates weight changes between entries:
  - Shows positive changes in red (weight gain)
  - Shows negative changes in green (weight loss)
  - Shows neutral changes in gray
- **Current Weight Display**: Shows the most recent weight prominently in a dedicated card




## Technical Implementation

### File Structure
```
cs50FinalProject/
├── app.py              # Main Flask application
├── schema.sql          # Database schema
├── macros.db          # SQLite database
└── templates/
    ├── layout.html    # Base template with navbar
    ├── index.html     # Dashboard
    ├── login.html     # Login page
    ├── register.html  # Registration page
    ├── goals.html     # Goal setting page
    ├── meals.html     # Meal tracking page
    └── weight.html    # Weight tracking page
```

### Database Schema

#### users table
Stores user authentication information:
- `id`: Primary key
- `username`: Unique username
- `hash`: Hashed password using Werkzeug
- `created_at`: Registration timestamp

#### goals table
Stores user macronutrient goals:
- `id`: Primary key
- `user_id`: Foreign key to users
- `protein_g`, `carbs_g`, `fat_g`: Daily goals in grams
- `calories`: Optional calorie goal
- `created_at`: Timestamp

#### foods table
Contains food items with nutritional values per 100g:
- `id`: Primary key
- `name`: Food name (unique, case-insensitive)
- `protein_100g`, `carbs_100g`, `fat_100g`: Macros per 100g (REAL type for decimal precision)

#### meals table
Logs individual meal entries:
- `id`: Primary key
- `user_id`: Foreign key to users
- `food_id`: Foreign key to foods
- `grams`: Amount consumed (REAL type for decimal precision)
- `protein_g`, `carbs_g`, `fat_g`, `calories`: Calculated values
- `created_at`: Timestamp

#### weight table
Tracks user weight over time:
- `id`: Primary key
- `user_id`: Foreign key to users
- `weight_kg`: Weight in kilograms (REAL type for decimal precision)
- `recorded_at`: Timestamp

### Key Design Decisions

1. **SQLite Database**: Chosen for simplicity and portability, suitable for a personal tracking application. No need for a separate database server.

2. **Session-based Authentication**: Using Flask sessions for user authentication rather than tokens, as this is a server-rendered application. The secret key should be changed in production.

3. **Jinja2 Templates**: Used for server-side rendering with template inheritance (layout.html) for consistent UI across all pages.

4. **Bootstrap 5**: Chosen for responsive design without custom CSS, keeping the project focused on functionality rather than design complexity.

5. **Calorie Calculation**: Using the standard 4-4-9 formula (protein and carbs = 4 cal/g, fats = 9 cal/g) as this is the scientifically accepted method.

6. **Date Filtering**: Using SQLite's DATE() function to filter meals by current day, ensuring users see only today's meals by default.

7. **Progress Bars**: Capped at 100% visually but show actual percentages in text to indicate if goals are exceeded.

8. **Custom Food Validation**: Implemented multiple layers of validation:
   - Frontend: HTML5 input validation with min/max attributes
   - Backend: Python validation to prevent malicious inputs
   - Database: Unique constraint on food names (case-insensitive)
   - Business logic: Sum of macros cannot exceed 100g per 100g of food

9. **User-specific Data**: All foods are shared across users (global database), but meals, goals, and weight are user-specific. This design decision was made because:
   - Food nutritional values are universal facts
   - Sharing the food database prevents duplication
   - Users can still add their own custom foods
   - Personal tracking data remains private per user

10. **Error Messages in Login**: Differentiated error messages improve UX by clearly indicating whether the username doesn't exist or the password is incorrect, helping users understand what to fix.

### Challenges Overcome

1. **Database Cursor Handling**: Initially tried to iterate over SQLite cursors directly in Jinja2 templates. Resolved by converting cursors to lists using `|list` filter in templates or `.fetchall()` in Python.

2. **Column Name Mismatch**: Original schema used 'date' column name, but this conflicted with SQLite's DATE() function. Changed to 'created_at' throughout the application for consistency.

3. **User Isolation**: Ensuring each user only sees their own data required consistently filtering by `user_id` in every query. Added `@login_required` decorator to prevent unauthorized access.

4. **Real-time Calculations**: Decided to store calculated macronutrient values rather than calculate on-the-fly for better performance and data integrity.

5. **Custom Food Validation**: Implementing comprehensive validation for user-submitted food data to prevent:
   - Negative values
   - Values exceeding physical limits (>100g per 100g)
   - Duplicate food names
   - SQL injection (using parameterized queries)

6. **Progress Bar Accuracy**: Ensuring progress bars display correctly when users exceed their goals (capping visual at 100% while showing actual percentage).

7. **Weight Change Calculation**: Implementing the weight difference calculation in Jinja2 templates required careful handling of loop indices and conditional formatting.

## How to Run

1. Install dependencies:
```bash
pip install flask
```

2. Initialize the database:
```bash
sqlite3 macros.db < schema.sql
```

3. Run the application:
```bash
flask run
```

4. Navigate to `http://127.0.0.1:5000`

5. Create an account and start tracking!

## Usage Guide

1. **First Time Setup**:
   - Register a new account
   - Set your daily macronutrient goals
   - Add your current weight

2. **Daily Tracking**:
   - Navigate to "Comidas" to log meals
   - Use existing foods or create new ones
   - View your progress on the Dashboard

3. **Adding Custom Foods**:
   - Go to "Comidas"
   - Use the green "Crear Nuevo Alimento" form
   - Enter macronutrient values per 100g
   - The food will be available immediately

4. **Monitoring Progress**:
   - Dashboard shows real-time progress bars
   - Color-coded cards for each macronutrient
   - Overall progress indicator with helpful messages

## Future Enhancements

Potential features for future versions:
- Add ability to delete/edit meals
- Implement meal templates for frequently eaten combinations
- Add graphs for weight trends over time
- Add graphs for macronutrient trends
- Export data to CSV for external analysis
- Add food search/filter functionality
- Mobile app version
- Barcode scanner integration for packaged foods
- Recipe calculator that sums up ingredients
- Meal planning feature for upcoming days
- Integration with fitness trackers
- Photo upload for meals
- Sharing/collaboration features

## Security Considerations

- Passwords are hashed using Werkzeug's `generate_password_hash()` before storage
- SQL injection is prevented through parameterized queries
- Session secret key should be changed in production (currently set to a placeholder)
- User input is validated on both frontend and backend
- Protected routes require authentication via `@login_required` decorator

## Acknowledgments

This project was created as the final project for CS50's Introduction to Computer Science course. Special thanks to David J. Malan and the CS50 team for their excellent instruction and resources.
