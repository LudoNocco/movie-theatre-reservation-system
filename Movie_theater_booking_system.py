import os
import sqlite3
from datetime import datetime

# Define database file path
DB_FILE = 'cinema_management.db'

def create_tables():
    """Create necessary tables in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT UNIQUE NOT NULL,
            duration INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY,
            movie_id INTEGER,
            hall TEXT NOT NULL,
            time TEXT NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies (id)
        )
    ''')
    
cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            screening_id INTEGER,
            customer_name TEXT NOT NULL,
            FOREIGN KEY (screening_id) REFERENCES screenings (id),
            UNIQUE(screening_id, customer_name)
        )
    ''')
    
    conn.commit()
    conn.close()

def add_movie(title, duration):
    """Add a movie to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO movies (title, duration) VALUES (?, ?)", (title, duration))
        conn.commit()
        print(f"Movie '{title}' added successfully.")
    except sqlite3.IntegrityError:
        print(f"Error: Movie '{title}' already exists.")
    finally:
        conn.close()

def add_screening(movie_title, hall, time):
    """Add a screening to the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if the movie exists
        cursor.execute("SELECT id FROM movies WHERE title = ?", (movie_title,))
        movie = cursor.fetchone()
        if not movie:
            print(f"Error: Movie '{movie_title}' not found.")
            return

        # Check for scheduling conflicts
        cursor.execute("SELECT m.title FROM screenings s JOIN movies m ON s.movie_id = m.id WHERE s.hall = ? AND s.time = ?", (hall, time))
        conflict = cursor.fetchone()
        if conflict:
            print(f"Conflict: The hall '{hall}' is already booked at '{time}' for movie '{conflict[0]}'.")
            return

        cursor.execute("INSERT INTO screenings (movie_id, hall, time) VALUES (?, ?, ?)", (movie[0], hall, time))
        conn.commit()
        print(f"Screening for '{movie_title}' added successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def reserve_seat(movie_title, screening_time, customer_name):
    """Reserve a seat for a specific movie and screening."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.id FROM screenings s
            JOIN movies m ON s.movie_id = m.id
            WHERE m.title = ? AND s.time = ?
        """, (movie_title, screening_time))
        screening = cursor.fetchone()
        
        if not screening:
            print(f"Error: No screening found for '{movie_title}' at {screening_time}.")
            return

        # Check if the customer already has a reservation for this screening
        cursor.execute("""
            SELECT id FROM reservations
            WHERE screening_id = ? AND customer_name = ?
        """, (screening[0], customer_name))
        existing_reservation = cursor.fetchone()

        if existing_reservation:
            print(f"Error: {customer_name} already has a reservation for '{movie_title}' at {screening_time}.")
            return

        cursor.execute("INSERT INTO reservations (screening_id, customer_name) VALUES (?, ?)", (screening[0], customer_name))
        conn.commit()
        print(f"Seat reserved for {customer_name} for '{movie_title}' at {screening_time}.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def browse_reservations():
    """Display all reservations."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT m.title, s.time, r.customer_name
            FROM reservations r
            JOIN screenings s ON r.screening_id = s.id
            JOIN movies m ON s.movie_id = m.id
            ORDER BY m.title, s.time
        """)
        reservations = cursor.fetchall()
        
        if not reservations:
            print("No reservations found.")
            return

        current_movie = None
        for movie, time, customer in reservations:
            if movie != current_movie:
                print(f"\nMovie: {movie}")
                current_movie = movie
            print(f"  Screening at {time}: {customer}")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def validate_time(time_str):
    """Validate time string format (HH:MM)."""
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def admin_interface():
    """Administrator interface for managing movies, screenings, and reservations."""
    while True:
        print("\nAdmin Menu")
        print("1. Add Movie")
        print("2. Add Screening")
        print("3. Browse Reservations")
        print("4. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            title = input("Enter movie title: ")
            while True:
                try:
                    duration = int(input("Enter movie duration (in minutes): "))
                    if duration <= 0:
                        raise ValueError
                    break
                except ValueError:
                    print("Invalid input. Please enter a positive integer for duration.")
            add_movie(title, duration)

        elif choice == '2':
            movie_title = input("Enter movie title: ")
            hall = input("Enter hall name: ")
            while True:
                time = input("Enter screening time (HH:MM): ")
                if validate_time(time):
                    break
                print("Invalid time format. Please use HH:MM format.")
            add_screening(movie_title, hall, time)

        elif choice == '3':
            browse_reservations()

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

def customer_interface():
    """Customer interface for reserving seats."""
    while True:
        print("\nCustomer Menu")
        print("1. Reserve Seat")
        print("2. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            movie_title = input("Enter movie title: ")
            while True:
                time = input("Enter screening time (HH:MM): ")
                if validate_time(time):
                    break
                print("Invalid time format. Please use HH:MM format.")
            customer_name = input("Enter your name: ")
            reserve_seat(movie_title, time, customer_name)

        elif choice == '2':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    db_path = os.path.abspath(DB_FILE)
    print(f"Using database: {db_path}")
    print(f"Note: To reset the system, delete the file: {db_path}")
    
    create_tables()
    while True:
        print("\nMain Menu")
        print("1. Admin Interface")
        print("2. Customer Interface")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == '1':
            admin_interface()
        elif choice == '2':
            customer_interface()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")