# Meal & Macro Tracker
#### Video Demo: <URL HERE>
#### Description:

## Overview
Meal & Macro Tracker is a web application built with Flask that helps users track their daily food intake, calories and macronutrient consumption (protein, carbohydrates, and fats). The application allows users to set daily macronutrient goals and monitor their progress throughout the day.
## Features

### User Authentication
- **Registration System**: New users can create an account with a username and password
- **Secure Login**: Passwords are hashed using Werkzeug's security functions
- **Differentiated Error Messages**: The login system provides specific feedback:
  - "User does not exist" when the username is not registered
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
- **Food Database**: Pre-populated with common foods and their accurate nutritional values per 100g
- **Custom Food Creation**: Users can add their own foods to the database with:
  - Custom food names (automatically converted to uppercase to prevent duplicates)
  - Calorie content per 100g (the primary source for calorie calculations)
  - Macronutrient values per 100g for protein, carbs, and fats
  - Validation to prevent invalid entries:
    - Calories must be between 0 and 900 kcal per 100g
    - Each macronutrient must be between 0 and 100 grams
    - The sum of all macros cannot exceed 100g per 100g of food
    - Duplicate food names are not allowed (case-insensitive check)
    - Negative values are not permitted
- **Historical Date Navigation**: Browse and edit meals from any previous day
  - Arrow navigation (← Previous / Next →) to move between dates
  - Date displayed as "Sunday 28", "Monday 29", etc.
  - Cannot navigate to future dates
  - Add meals to past dates to backfill your tracking history
- **Meal Logging**: Users can:
  - Select a food from the database (including their custom foods)
  - Enter the amount consumed in grams
  - Add meals to the current day or any previous date
  - View all meals for a specific date
- **Edit and Delete Meals**: 
  - Edit meal portions inline by clicking the pencil (✏️) icon
  - Delete meals with confirmation by clicking the trash (🗑️) icon
  - Changes persist when navigating between dates
  - Can edit meals from any historical date
- **Daily Totals**: Automatic calculation of total macros and calories for each day
- **Accurate Calorie Calculations**: 
  - Calories are calculated from the food's stored calorie data: `calories_100g * grams / 100`
  - NOT calculated from macros (4-4-9 formula), which can be inaccurate due to fiber, alcohol, and other factors
  - This ensures precision and matches real-world nutritional data

### Dashboard
- **Real-time Progress**: Shows current day's consumption vs. daily goals
- **Visual Progress Bars**: For each macronutrient (protein, carbs, fats, calories)
- **Percentage Completion**: Displays how close the user is to their goals for today
- **Color-coded Cards**: Each macronutrient has its own color for easy identification:
  - Green for Protein
  - Blue for Carbohydrates
  - Yellow for Fats
  - Red for Calories
- **Weekly Average Tracking**: Shows 7-day averages for:
  - Daily calorie intake
  - Daily protein consumption
  - Daily carbohydrate consumption
  - Daily fat consumption
  - Comparison against goals (when goals are set)
- **Quick Actions**: Easy access to add meals, set goals, or log weight

### Weight Tracking
- **Weight Logging**: Users can record their weight in kilograms with decimal precision
- **Historical Data**: View the last 30 weight entries
- **Change Tracking**: Automatically calculates weight changes between entries:
  - Shows positive changes in red (weight gain)
  - Shows negative changes in green (weight loss)
  - Shows neutral changes in gray
- **Current Weight Display**: Shows the most recent weight prominently on the dashboard

## Technical Implementation

### File Structure
mealplanner/
app.py                      # Main Flask application
schema.sql                  # Database schema
populate_foods.sql          # Migration script for food database
macros.db                   # SQLite database
templates/
    ─ layout.html             # Base template with navbar
    ─ index.html              # Dashboard
    ─ login.html              # Login page
    ─ register.html           # Registration page
    ─ goals.html              # Goal setting page
    ─ meals.html              # Meal tracking page with food logs and edits
    ─ weight.html             # Weight tracking page


### Database Schema

#### users table: Stores user authentication information.
#### goals table: Stores user macronutrient goals
#### foods table: Contains food items with nutritional values per 100g.
#### meals table: Logs individual meal entries.
#### weight table: Tracks user weight over time.


### Key Design Decisions

1. **SQLite Database**: Chosen for simplicity and portability, suitable for a personal tracking application. No need for a separate database server.

2. **Session-based Authentication**: Using Flask sessions for user authentication rather than tokens, as this is a server-rendered application. The secret key should be changed in production.

3. **Jinja2 Templates**: Used for server-side rendering with template inheritance (layout.html) for consistent UI across all pages.

4. **Bootstrap 5**: Chosen for responsive design without custom CSS, keeping the project focused on functionality rather than design complexity.

5. **Accurate Calorie Data**: Instead of calculating calories from macronutrients using the 4-4-9 formula (which is only an approximation), we store and use actual calorie values per 100g. This is more accurate because:
   - Fiber contributes to carb weight but provides fewer calories
   - Alcohol provides 7 kcal/g but isn't tracked as a macro
   - Food processing and digestion affect actual caloric availability
   - Real-world nutritional databases provide measured calorie values

6. **Date Filtering**: Using SQLite's DATE() function to filter meals by specific dates, allowing users to view and edit historical data.

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

10. **Uppercase Food Names**: All food names are automatically converted to uppercase to prevent duplicates caused by different capitalizations (e.g., "Chicken", "chicken", "CHICKEN" are all treated as the same food).

11. **Historical Meal Tracking**: Users can add, edit, and delete meals from any previous date, not just the current day. This allows for:
    - Backfilling data when tracking was missed
    - Correcting mistakes in past entries
    - Comprehensive historical analysis
    - More flexible meal planning and tracking

12. **Weekly Averages**: The dashboard shows 7-day averages instead of just today's summary, providing better insights into overall dietary patterns and trends over time. If a day has no meal logs, the average won't count that day.

### Challenges Overcome

1. **Database Cursor Handling**: Initially tried to iterate over SQLite cursors directly in Jinja2 templates. Resolved by converting cursors to lists using `|list` filter in templates or `.fetchall()` in Python.

2. **Column Name Mismatch**: Original schema used 'date' column name, but this conflicted with SQLite's DATE() function. Changed to 'created_at' throughout the application for consistency.

3. **User Isolation**: Ensuring each user only sees their own data required consistently filtering by `user_id` in every query. Added `@login_required` decorator to prevent unauthorized access.

4. **Calorie Calculation Accuracy**: Initially calculated calories from macros using the 4-4-9 formula, which is only an approximation. Switched to storing actual calorie data per 100g in the foods table and calculating meal calories proportionally. This required a database migration and updating all calorie calculation logic.

5. **Custom Food Validation**: Implementing comprehensive validation for user-submitted food data to prevent:
   - Negative values
   - Values exceeding physical limits (>100g per 100g for macros)
   - Unrealistic calorie values (>900 kcal per 100g)
   - Duplicate food names
   - SQL injection (using parameterized queries)

6. **Progress Bar Accuracy**: Ensuring progress bars display correctly when users exceed their goals (capping visual at 100% while showing actual percentage).

7. **Weight Change Calculation**: Implementing the weight difference calculation in Jinja2 templates required careful handling of loop indices and conditional formatting.

8. **Date Navigation**: Implementing backward/forward date navigation while preventing access to future dates required careful date manipulation with Python's datetime module and conditional button disabling in the template.

9. **Historical Meal Creation**: Allowing users to add meals to past dates required modifying the INSERT query to accept a custom timestamp instead of always using 'now', and ensuring the date context is maintained throughout the add/edit/delete flow.

10. **Weekly Average with Sparse Data**: Calculating 7-day averages when users don't log meals every day required using a subquery that groups by date first, then calculates averages only for days with data.


## Usage Guide

1. **First Time Setup**:
   - Register a new account
   - Set your daily macronutrient goals
   - Add your current weight (optional)

2. **Daily Tracking**:
   - Navigate to "Meals" to log meals
   - Use existing foods or create new ones
   - View your progress on the Dashboard

3. **Adding Custom Foods**:
   - Go to "Meals"
   - Use the green "Create New Food" form
   - Enter calorie content per 100g (most important!)
   - Enter macronutrient values per 100g
   - The food will be available immediately

4. **Historical Tracking**:
   - Go to "Meals"
   - Use Previous / Next arrows to navigate dates
   - Add meals to any past date using the form
   - Edit or delete historical meals as needed
   - Current date is shown as "Sunday 28", "Monday 29", etc.

5. **Editing Meals**:
   - Click the pencil (✏️) icon to edit portion size
   - Click the checkmark (✅) to save changes
   - Click the X (❌) to cancel editing
   - Click the trash (🗑️) to delete a meal

6. **Monitoring Progress**:
   - Dashboard shows real-time progress bars for today
   - Color-coded cards for each macronutrient
   - Weekly average section shows 7-day trends
   - Quick action buttons for common tasks

## Future Enhancements

Potential features for future versions:
- Add ability to copy meals from one day to another
- Implement meal templates for frequently eaten combinations
- Add graphs for weight trends over time
- Add graphs for macronutrient trends (30-day, 90-day views)
- Export data to CSV for external analysis
- Add food search/filter functionality
- Mobile app version
- Barcode scanner integration for packaged foods
- Recipe calculator that sums up ingredients
- Meal planning feature for upcoming days
- Photo upload for meals
- Sharing/collaboration features
- Multi-language support

