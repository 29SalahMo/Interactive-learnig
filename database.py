"""
Simple Database Manager for Child Learning System
Uses SQLite to store child information including name, gender, and face encodings
"""
import sqlite3
import os
import pickle
import json
from typing import Optional, Dict, List, Tuple


class ChildDatabase:
    """Manages child database operations"""
    
    def __init__(self, db_path: str = "children.db"):
        """
        Initialize database connection
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create children table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                gender TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                total_quizzes INTEGER DEFAULT 0,
                total_score INTEGER DEFAULT 0
            )
        """)
        
        # Create face_encodings table (store encodings separately due to size)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS face_encodings (
                child_id INTEGER PRIMARY KEY,
                encoding BLOB NOT NULL,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        """)
        
        # Create quiz_results table for tracking progress
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                FOREIGN KEY (child_id) REFERENCES children(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_child(self, name: str, gender: str, face_encoding) -> bool:
        """
        Add a new child to the database
        Args:
            name: Child's name
            gender: Child's gender ('boy' or 'girl')
            face_encoding: Face encoding array from face_recognition
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert child record
            cursor.execute("""
                INSERT INTO children (name, gender)
                VALUES (?, ?)
            """, (name, gender.lower()))
            
            child_id = cursor.lastrowid
            
            # Insert face encoding (serialize as pickle)
            encoding_blob = pickle.dumps(face_encoding)
            cursor.execute("""
                INSERT INTO face_encodings (child_id, encoding)
                VALUES (?, ?)
            """, (child_id, encoding_blob))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print(f"Child '{name}' already exists in database")
            return False
        except Exception as e:
            print(f"Error adding child to database: {e}")
            return False
    
    def get_child_by_name(self, name: str) -> Optional[Dict]:
        """
        Get child information by name
        Args:
            name: Child's name
        Returns:
            Dictionary with child info and face encoding, or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get child info
            cursor.execute("""
                SELECT * FROM children WHERE name = ?
            """, (name,))
            
            child_row = cursor.fetchone()
            if not child_row:
                conn.close()
                return None
            
            # Get face encoding
            cursor.execute("""
                SELECT encoding FROM face_encodings WHERE child_id = ?
            """, (child_row['id'],))
            
            encoding_row = cursor.fetchone()
            conn.close()
            
            if not encoding_row:
                return None
            
            # Deserialize encoding
            face_encoding = pickle.loads(encoding_row['encoding'])
            
            # Convert row to dictionary
            child_info = {
                'id': child_row['id'],
                'name': child_row['name'],
                'gender': child_row['gender'],
                'created_at': child_row['created_at'],
                'last_login': child_row['last_login'],
                'total_quizzes': child_row['total_quizzes'],
                'total_score': child_row['total_score'],
                'face_encoding': face_encoding
            }
            
            return child_info
        except Exception as e:
            print(f"Error getting child from database: {e}")
            return None
    
    def get_all_children(self) -> List[Dict]:
        """
        Get all children from database
        Returns:
            List of dictionaries with child information (without face encodings)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM children ORDER BY name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            children = []
            for row in rows:
                children.append({
                    'id': row['id'],
                    'name': row['name'],
                    'gender': row['gender'],
                    'created_at': row['created_at'],
                    'last_login': row['last_login'],
                    'total_quizzes': row['total_quizzes'],
                    'total_score': row['total_score']
                })
            
            return children
        except Exception as e:
            print(f"Error getting all children: {e}")
            return []
    
    def get_all_face_encodings(self) -> Dict[str, any]:
        """
        Get all face encodings for login matching
        Returns:
            Dictionary mapping child names to their face encodings
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT c.name, fe.encoding
                FROM children c
                JOIN face_encodings fe ON c.id = fe.child_id
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            encodings = {}
            for name, encoding_blob in rows:
                encodings[name] = pickle.loads(encoding_blob)
            
            return encodings
        except Exception as e:
            print(f"Error getting face encodings: {e}")
            return {}
    
    def update_last_login(self, name: str) -> bool:
        """Update last login timestamp for a child"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE children
                SET last_login = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (name,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating last login: {e}")
            return False
    
    def add_quiz_result(self, child_name: str, score: int, total_questions: int) -> bool:
        """
        Add quiz result for a child
        Args:
            child_name: Child's name
            score: Score achieved
            total_questions: Total number of questions
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get child ID
            cursor.execute("SELECT id FROM children WHERE name = ?", (child_name,))
            child_row = cursor.fetchone()
            if not child_row:
                conn.close()
                return False
            
            child_id = child_row[0]
            
            # Insert quiz result
            cursor.execute("""
                INSERT INTO quiz_results (child_id, score, total_questions)
                VALUES (?, ?, ?)
            """, (child_id, score, total_questions))
            
            # Update child statistics
            cursor.execute("""
                UPDATE children
                SET total_quizzes = total_quizzes + 1,
                    total_score = total_score + ?
                WHERE id = ?
            """, (score, child_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding quiz result: {e}")
            return False
    
    def get_child_stats(self, child_name: str) -> Optional[Dict]:
        """
        Get statistics for a child
        Args:
            child_name: Child's name
        Returns:
            Dictionary with statistics or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    c.name,
                    c.gender,
                    c.total_quizzes,
                    c.total_score,
                    COUNT(qr.id) as num_results,
                    AVG(qr.score * 100.0 / qr.total_questions) as avg_percentage
                FROM children c
                LEFT JOIN quiz_results qr ON c.id = qr.child_id
                WHERE c.name = ?
                GROUP BY c.id
            """, (child_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            return {
                'name': row['name'],
                'gender': row['gender'],
                'total_quizzes': row['total_quizzes'] or 0,
                'total_score': row['total_score'] or 0,
                'num_results': row['num_results'] or 0,
                'avg_percentage': round(row['avg_percentage'] or 0, 2)
            }
        except Exception as e:
            print(f"Error getting child stats: {e}")
            return None
    
    def delete_child(self, name: str) -> bool:
        """
        Delete a child from the database
        This will also delete their face encoding and all quiz results (CASCADE)
        Args:
            name: Child's name
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if child exists
            cursor.execute("SELECT id FROM children WHERE name = ?", (name,))
            if not cursor.fetchone():
                conn.close()
                return False
            
            # Delete child (CASCADE will delete face_encodings and quiz_results)
            cursor.execute("DELETE FROM children WHERE name = ?", (name,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting child from database: {e}")
            return False
    
    def update_child_name(self, old_name: str, new_name: str) -> bool:
        """
        Update a child's name
        Args:
            old_name: Current name
            new_name: New name
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE children
                SET name = ?
                WHERE name = ?
            """, (new_name, old_name))
            
            if cursor.rowcount == 0:
                conn.close()
                return False
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            print(f"Child '{new_name}' already exists in database")
            return False
        except Exception as e:
            print(f"Error updating child name: {e}")
            return False
    
    def get_quiz_results(self, child_name: str = None) -> List[Dict]:
        """
        Get quiz results, optionally filtered by child name
        Args:
            child_name: Optional child name to filter results
        Returns:
            List of quiz result dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if child_name:
                cursor.execute("""
                    SELECT qr.id, qr.quiz_date, qr.score, qr.total_questions,
                           (qr.score * 100.0 / qr.total_questions) as percentage,
                           c.name, c.id as child_id
                    FROM quiz_results qr
                    JOIN children c ON qr.child_id = c.id
                    WHERE c.name = ?
                    ORDER BY qr.quiz_date DESC
                """, (child_name,))
            else:
                cursor.execute("""
                    SELECT qr.id, qr.quiz_date, qr.score, qr.total_questions,
                           (qr.score * 100.0 / qr.total_questions) as percentage,
                           c.name, c.id as child_id
                    FROM quiz_results qr
                    JOIN children c ON qr.child_id = c.id
                    ORDER BY qr.quiz_date DESC
                """)
            
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    'id': row['id'],
                    'child_id': row['child_id'],
                    'child_name': row['name'],
                    'quiz_date': row['quiz_date'],
                    'score': row['score'],
                    'total_questions': row['total_questions'],
                    'percentage': round(row['percentage'], 2)
                })
            
            return results
        except Exception as e:
            print(f"Error getting quiz results: {e}")
            return []
    
    def delete_quiz_result(self, result_id: int) -> bool:
        """
        Delete a specific quiz result
        Note: This will also update the child's statistics
        Args:
            result_id: Quiz result ID
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the quiz result to update child stats
            cursor.execute("""
                SELECT child_id, score FROM quiz_results WHERE id = ?
            """, (result_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
            
            child_id, score = result
            
            # Delete the quiz result
            cursor.execute("DELETE FROM quiz_results WHERE id = ?", (result_id,))
            
            # Update child statistics
            cursor.execute("""
                UPDATE children
                SET total_quizzes = total_quizzes - 1,
                    total_score = total_score - ?
                WHERE id = ?
            """, (score, child_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting quiz result: {e}")
            return False
    
    def clear_child_quiz_results(self, child_name: str) -> bool:
        """
        Clear all quiz results for a child and reset their statistics
        Args:
            child_name: Child's name
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get child ID
            cursor.execute("SELECT id FROM children WHERE name = ?", (child_name,))
            child_row = cursor.fetchone()
            if not child_row:
                conn.close()
                return False
            
            child_id = child_row[0]
            
            # Delete all quiz results for this child
            cursor.execute("DELETE FROM quiz_results WHERE child_id = ?", (child_id,))
            
            # Reset child statistics
            cursor.execute("""
                UPDATE children
                SET total_quizzes = 0,
                    total_score = 0
                WHERE id = ?
            """, (child_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing quiz results: {e}")
            return False
    
    def reset_database(self) -> bool:
        """
        WARNING: Delete all data from the database
        This will remove all children, face encodings, and quiz results
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete all data (tables will remain)
            cursor.execute("DELETE FROM quiz_results")
            cursor.execute("DELETE FROM face_encodings")
            cursor.execute("DELETE FROM children")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error resetting database: {e}")
            return False

