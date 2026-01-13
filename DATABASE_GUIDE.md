# Database Guide - Child Learning System

## Overview
The database uses **SQLite** to store information about children, their face encodings, and quiz results. The database file is named `children.db` and is located in the project root directory.

## Database Structure

### 1. **children** Table
Stores basic information about each registered child.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key, auto-incremented |
| `name` | TEXT | Child's name (UNIQUE, NOT NULL) |
| `gender` | TEXT | Child's gender ('boy' or 'girl') |
| `created_at` | TIMESTAMP | When the child was registered |
| `last_login` | TIMESTAMP | Last time the child logged in |
| `total_quizzes` | INTEGER | Total number of quizzes taken |
| `total_score` | INTEGER | Sum of all quiz scores |

### 2. **face_encodings** Table
Stores face recognition encodings for each child (separate table due to large size).

| Column | Type | Description |
|--------|------|-------------|
| `child_id` | INTEGER | Foreign key to children.id (PRIMARY KEY) |
| `encoding` | BLOB | Pickled face encoding data |

**Relationship**: One-to-one with `children` table (one encoding per child).

### 3. **quiz_results** Table
Stores individual quiz attempt results.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key, auto-incremented |
| `child_id` | INTEGER | Foreign key to children.id |
| `quiz_date` | TIMESTAMP | When the quiz was taken |
| `score` | INTEGER | Score achieved |
| `total_questions` | INTEGER | Total questions in quiz |

**Relationship**: Many-to-one with `children` table (one child can have many quiz results).

## How It Works

### Registration Flow
1. When a child signs up via face registration:
   - Face encoding is generated from camera image
   - Child's name and gender are collected
   - `add_child()` is called:
     - Inserts record into `children` table
     - Stores face encoding in `face_encodings` table (as pickled BLOB)

### Login Flow
1. When a child logs in via face recognition:
   - Camera captures face
   - Face encoding is generated
   - `get_all_face_encodings()` retrieves all stored encodings
   - System compares new encoding with stored encodings
   - If match found, `update_last_login()` updates the timestamp
   - Child information is returned

### Quiz Flow
1. When a child completes a quiz:
   - `add_quiz_result()` is called with:
     - Child's name
     - Score achieved
     - Total questions
   - New record added to `quiz_results` table
   - `children` table statistics updated:
     - `total_quizzes` incremented
     - `total_score` increased by new score

## Key Methods in `database.py`

### `add_child(name, gender, face_encoding)`
- Adds a new child to the database
- Returns `True` if successful, `False` if child already exists

### `get_child_by_name(name)`
- Retrieves complete child information including face encoding
- Returns dictionary with all child data

### `get_all_children()`
- Gets list of all registered children (without face encodings)
- Useful for displaying children list

### `get_all_face_encodings()`
- Returns dictionary mapping child names to face encodings
- Used during login for face matching

### `update_last_login(name)`
- Updates the `last_login` timestamp when child logs in

### `add_quiz_result(child_name, score, total_questions)`
- Records a quiz attempt
- Updates child statistics automatically

### `get_child_stats(child_name)`
- Returns statistics for a child:
  - Total quizzes
  - Total score
  - Number of quiz results
  - Average percentage

## Viewing the Database

### Option 1: Use the Database Viewer Script
Run the interactive viewer:
```bash
python view_database.py
```

This provides:
- Database structure overview
- Summary statistics
- List of all children
- Detailed child information
- Quiz results viewing

### Option 2: Use SQLite Command Line
```bash
sqlite3 children.db
```

Then run SQL commands:
```sql
-- View all tables
.tables

-- View children table structure
.schema children

-- View all children
SELECT * FROM children;

-- View quiz results
SELECT * FROM quiz_results;

-- View with joins
SELECT c.name, qr.score, qr.total_questions, qr.quiz_date
FROM children c
JOIN quiz_results qr ON c.id = qr.child_id;
```

### Option 3: Use SQLite Browser (GUI Tool)
Download DB Browser for SQLite: https://sqlitebrowser.org/
- Open `children.db` file
- Browse tables visually
- Run SQL queries
- View data in tables

## Database File Location
- **File**: `children.db`
- **Location**: Project root directory
- **Format**: SQLite 3 database

## Important Notes

1. **Face Encodings**: Stored as BLOB (Binary Large Object) using Python's `pickle` module. These are large arrays (128 dimensions) used for face recognition.

2. **Cascade Deletes**: If a child is deleted, all related quiz results and face encodings are automatically deleted (ON DELETE CASCADE).

3. **Unique Names**: Each child must have a unique name. Attempting to add a duplicate name will fail.

4. **Auto-increment IDs**: Child IDs are automatically assigned and cannot be manually set.

5. **Timestamps**: Uses SQLite's CURRENT_TIMESTAMP for automatic date/time recording.

## Example Usage in Code

```python
from database import ChildDatabase

# Initialize database
db = ChildDatabase()

# Add a new child (during registration)
face_encoding = [...]  # Generated from face_recognition
db.add_child("Alice", "girl", face_encoding)

# Get child information (during login)
child = db.get_child_by_name("Alice")
print(f"Welcome {child['name']}!")

# Add quiz result (after quiz completion)
db.add_quiz_result("Alice", 8, 10)  # 8 out of 10 correct

# Get statistics
stats = db.get_child_stats("Alice")
print(f"Average: {stats['avg_percentage']}%")
```

## Troubleshooting

**Database not found?**
- The database is created automatically when you first use `ChildDatabase()`
- Check if `children.db` exists in the project root

**Can't see face encodings?**
- Face encodings are stored as binary data (BLOB)
- Use `get_child_by_name()` to retrieve them
- They're automatically loaded when needed for face recognition

**Quiz results not showing?**
- Make sure `add_quiz_result()` is called after each quiz
- Check that the child name matches exactly (case-sensitive)
