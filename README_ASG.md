# Student Incentive System

A Flask MVC command-line application for tracking student community service hours with staff oversight and student incentives.

## Project Overview

The Student Incentive System allows staff to log community service hours for students, students to request confirmation of their hours, and provides a leaderboard system with milestone-based accolades to incentivize community service participation.

## Features

1. **Staff Log Hours for Students** - Staff can record community service hours for students
2. **Student Request Confirmation** - Students can request formal confirmation of logged hours  
3. **View Student Leaderboard** - Display ranked list of students by confirmed hours
4. **Student View Accolades** - Students can view earned milestones (10/25/50+ hours)

## Installation & Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Initialize the database:
   ```bash
   flask init
   ```

## CLI Commands Documentation

### Database Initialization

```bash
flask init
```
**Description**: Creates and initializes the database with default users
- Creates sample users: bob, sally, rob
- Creates students: student1, student2
- Creates staff: staff1, staff2
- Sets up the database schema

**Example Output**:
```
Created user: bob
Created student: student1
Created student: student2
Created staff: staff1
Created staff: staff2
database intialized
```

### 1. Staff Log Hours for Student

```bash
flask staff-log-hours [staff_username] [student_username] [hours] [activity]
```

**Description**: Allows staff members to log community service hours for students

**Parameters**:
- `staff_username` (default: staff1) - Username of the staff member
- `student_username` (default: student1) - Username of the student
- `hours` (default: 10) - Number of hours to log
- `activity` (default: community service) - Description of the activity

**Example**:
```bash
flask staff-log-hours staff1 student1 15 "volunteered at local food bank"
```

**Example Output**:
```
Staff staff1 logged 15 hours for student student1
Activity: volunteered at local food bank
Log ID: 9f58af47-11d3-4aef-9d3f-f840a2cc05bd
```

### 2. Student Request Confirmation of Hours

```bash
flask request-confirmation [student_username] [activity_log_id]
```

**Description**: Enables students to request formal confirmation of their logged hours by staff

**Parameters**:
- `student_username` (default: student1) - Username of the student
- `activity_log_id` (required) - ID of the activity log to request confirmation for

**Example**:
```bash
flask request-confirmation student1 9f58af47-11d3-4aef-9d3f-f840a2cc05bd
```

**Example Output**:
```
Student student1 requested confirmation for activity log 9f58af47-11d3-4aef-9d3f-f840a2cc05bd
Status changed to: pending
```

### 3. View Student Leaderboard

```bash
flask view-leaderboard
```

**Description**: Displays a ranked leaderboard of all students based on their confirmed community service hours

**Parameters**: None

**Example**:
```bash
flask view-leaderboard
```

**Example Output**:
```
Student Leaderboard (Ranked by Confirmed Community Service Hours):
======================================================================
1. student2 - 30 hours - 0 accolades
2. student1 - 15 hours - 0 accolades
```

### 4. Student View Accolades

```bash
flask view-accolades [student_username]
```

**Description**: Shows milestone accolades earned by a student based on confirmed hours

**Parameters**:
- `student_username` (default: student1) - Username of the student

**Available Milestones**:
- 10 Hour Milestone
- 25 Hour Milestone  
- 50 Hour Milestone
- 100 Hour Milestone
- 200 Hour Milestone
- 300 Hour Milestone

**Example**:
```bash
flask view-accolades student1
```

**Example Output**:
```
Accolades for student1:
Total confirmed community service hours: 15
==================================================
1. 10 Hour Milestone
```

### Additional Staff Command

```bash
flask staff-confirm-hours [staff_username] [activity_log_id]
```

**Description**: Allows staff to confirm student hours that are in pending status

**Parameters**:
- `staff_username` (default: staff1) - Username of the staff member
- `activity_log_id` (required) - ID of the activity log to confirm

**Example**:
```bash
flask staff-confirm-hours staff1 9f58af47-11d3-4aef-9d3f-f840a2cc05bd
```

## Complete Workflow Example

Here's a complete example of the system workflow:

```bash
# 1. Initialize the database
flask init

# 2. Staff logs hours for a student
flask staff-log-hours staff1 student1 15 "volunteered at local food bank"
# Output: Log ID: 9f58af47-11d3-4aef-9d3f-f840a2cc05bd

# 3. Student requests confirmation
flask request-confirmation student1 9f58af47-11d3-4aef-9d3f-f840a2cc05bd

# 4. Staff confirms the hours
flask staff-confirm-hours staff1 9f58af47-11d3-4aef-9d3f-f840a2cc05bd

# 5. View updated leaderboard
flask view-leaderboard

# 6. Student views their accolades
flask view-accolades student1
```

## ⚠️ Important Note About Log IDs

**When using the system, you MUST use the actual Log ID that gets generated!**

Each time you run `flask staff-log-hours`, the system generates a unique Log ID. You must copy this exact ID (not the example one shown above) and use it in the subsequent `request-confirmation` and `staff-confirm-hours` commands.

**Example of what to do:**

1. Run the staff-log-hours command:
   ```bash
   flask staff-log-hours staff1 student1 15 "volunteered at local food bank"
   ```
   
2. Copy the actual Log ID from the output (e.g., `c396d501-6933-4d53-9ccd-f627d7aca836`)

3. Use that real Log ID in the next commands:
   ```bash
   flask request-confirmation student1 c396d501-6933-4d53-9ccd-f627d7aca836
   flask staff-confirm-hours staff1 c396d501-6933-4d53-9ccd-f627d7aca836
   ```

If you use the wrong Log ID, you'll get errors like "Activity log not found!"

## System Architecture

### Models
- **User**: Base user model with authentication
- **Student**: Extends User, tracks community service hours
- **Staff**: Extends User, can log and confirm hours for students
- **ActivityLog**: Records community service activities with confirmation status
- **Accolade**: Milestone achievements based on confirmed hours
- **LeaderBoardEntry**: Ranking system for student comparison

### Key Features
- **Hour Tracking**: Only confirmed hours count toward leaderboard and accolades
- **Approval Workflow**: Hours must be requested for confirmation by students and approved by staff
- **Milestone System**: Automatic accolade calculation based on confirmed hours
- **Leaderboard**: Real-time ranking of students by confirmed community service hours

## Technical Requirements

- Python 3.x
- Flask
- SQLAlchemy
- Click (for CLI)
- SQLite (default database)

## Testing

Additional commands for testing:

```bash
# User management
flask user create [username] [password]
flask user list [format]

# Run tests
flask test user [type]
```

## Database Schema

The system uses SQLAlchemy models with the following key relationships:
- Students have many ActivityLogs
- ActivityLogs track hours and confirmation status
- Accolades are awarded based on confirmed hour milestones
- LeaderBoard entries rank students by total confirmed hours

## Status Tracking

Activity logs have three possible statuses:
- **pending**: Initial status when hours are logged
- **confirmed**: Hours have been verified and approved by staff
- **rejected**: Hours have been reviewed and not approved (future enhancement)

Only **confirmed** hours count toward the leaderboard rankings and accolade milestones.