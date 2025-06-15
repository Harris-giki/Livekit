import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
<<<<<<< HEAD
class Car: #represents the data stored in the database
=======
class Car:
>>>>>>> 80da09c4ce1455d1decf5f03e7ca8888a90930d0
    vin: str
    make: str
    model: str
    year: int

class DatabaseDriver:
    def __init__(self, db_path: str = "auto_db.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
<<<<<<< HEAD
            #Initialize database; Create cars table
=======
            # Create cars table
>>>>>>> 80da09c4ce1455d1decf5f03e7ca8888a90930d0
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    vin TEXT PRIMARY KEY,
                    make TEXT NOT NULL,
                    model TEXT NOT NULL,
                    year INTEGER NOT NULL
                )
            """)
            conn.commit()
<<<<<<< HEAD
            
#creating a car in the database
=======

>>>>>>> 80da09c4ce1455d1decf5f03e7ca8888a90930d0
    def create_car(self, vin: str, make: str, model: str, year: int) -> Car:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cars (vin, make, model, year) VALUES (?, ?, ?, ?)",
                (vin, make, model, year)
            )
            conn.commit()
            return Car(vin=vin, make=make, model=model, year=year)
<<<<<<< HEAD
        
#get a car from the database
=======

>>>>>>> 80da09c4ce1455d1decf5f03e7ca8888a90930d0
    def get_car_by_vin(self, vin: str) -> Optional[Car]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cars WHERE vin = ?", (vin,))
            row = cursor.fetchone()
            if not row:
                return None
            
            return Car(
                vin=row[0],
                make=row[1],
                model=row[2],
                year=row[3]
            )