import logging
import sqlite3
from fastapi import APIRouter, HTTPException
from typing import List

from database import get_db_connection
from models import StudentCreate, StudentUpdate, StudentOut

router = APIRouter()

# --- Create student ---
@router.post("/", response_model=dict)
def add_student(student: StudentCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE number=?", (student.phone,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Phone number already exists")

    try:
        cursor.execute("""
            INSERT INTO students (first_name, last_name, number, birthdate, email)
            VALUES (?, ?, ?, ?, ?)
        """, (student.first_name, student.last_name, student.phone, student.birthdate, student.email))
        conn.commit()
        logging.info(f"Student added: {student.dict()}")
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        cursor.close()
        conn.close()

    return {"success": True, "message": "Student registered successfully!"}

# --- Read students ---
@router.get("/", response_model=List[StudentOut])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, first_name, last_name, number AS phone, birthdate, email FROM students")
    rows = cursor.fetchall()
    students = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return students

# --- Update student ---
@router.put("/{student_id}", response_model=dict)
def update_student(student_id: int, student: StudentUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE number=? AND id!=?", (student.phone, student_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Phone number already exists")

    try:
        cursor.execute("""
            UPDATE students
            SET first_name=?, last_name=?, number=?, birthdate=?, email=?
            WHERE id=?
        """, (student.first_name, student.last_name, student.phone, student.birthdate, student.email, student_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        logging.info(f"Student updated: {student.dict()}")
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        cursor.close()
        conn.close()

    return {"success": True, "message": "Student updated successfully!"}

# --- Delete student ---
@router.delete("/{student_id}", response_model=dict)
def delete_student(student_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"success": True, "message": "Student deleted"}
