import sqlite3
from dataclasses import dataclass
from typing import Optional, Dict, Any
from config import DATABASE_PATH, logger


@dataclass
class UserData:
    """Simple container for conversation state"""
    pass


class StudentDatabase:
    """Handles all student database operations"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
        self.add_dummy_data()
    
    def init_database(self):
        """Create the students table if it doesn't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS students (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        major TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        cgpa REAL NOT NULL
                    )
                ''')
                conn.commit()
                logger.info("Student database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    def add_dummy_data(self):
        """Add some dummy student data if table is empty"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if table has data
                cursor.execute('SELECT COUNT(*) FROM students')
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Add dummy data
                    dummy_students = [
                        ("2023428", "Haris", "BSCS", 2023, 3.26),
                    ]
                    
                    cursor.executemany(
                        'INSERT INTO students (id, name, major, year, cgpa) VALUES (?, ?, ?, ?, ?)',
                        dummy_students
                    )
                    conn.commit()
                    logger.info(f"Added {len(dummy_students)} dummy student records")
                
        except Exception as e:
            logger.error(f"Failed to add dummy data: {e}")
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve student information by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM students WHERE id = ?', (student_id,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'major': row[2],
                        'year': row[3],
                        'cgpa': row[4]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve student {student_id}: {e}")
            return None
    
    def get_student_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve student information by name (case-insensitive)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM students WHERE LOWER(name) = LOWER(?)', (name,))
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row[0],
                        'name': row[1],
                        'major': row[2],
                        'year': row[3],
                        'cgpa': row[4]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve student {name}: {e}")
            return None
    
    def add_student(self, student_id: str, name: str, major: str, year: int, cgpa: float) -> bool:
        """Add a new student to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO students (id, name, major, year, cgpa) VALUES (?, ?, ?, ?, ?)',
                    (student_id, name, major, year, cgpa)
                )
                conn.commit()
                logger.info(f"Added new student: {student_id} - {name}")
                return True
                
        except sqlite3.IntegrityError:
            logger.warning(f"Student ID {student_id} already exists")
            return False
        except Exception as e:
            logger.error(f"Failed to add student: {e}")
            return False
    
    