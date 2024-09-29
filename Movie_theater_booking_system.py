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
        CREATE TABLE IF NOT EXISTS halls (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            capacity INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY,
            movie_id INTEGER,
            hall_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            seats_available INTEGER NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            FOREIGN KEY (hall_id) REFERENCES halls (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            screening_id INTEGER,
            customer_name TEXT NOT NULL,
            seats_reserved INTEGER NOT NULL,
            FOREIGN KEY (screening_id) REFERENCES screenings (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def initialize_halls():
    """Initialize the halls in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    halls = [
        ("Oak", 50),
        ("Birch", 150),
        ("Maple", 150),
        ("Pine", 300),
        ("Cedar", 300)
    ]
    
    for hall_name, capacity in halls:
        cursor.execute("INSERT OR IGNORE INTO halls (name, capacity) VALUES (?, ?)", (hall_name, capacity))
    
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

def add_screening(movie_title, hall_name, date, time):
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

        # Check if the hall exists
        cursor.execute("SELECT id, capacity FROM halls WHERE name = ?", (hall_name,))
        hall = cursor.fetchone()
        if not hall:
            print(f"Error: Hall '{hall_name}' not found.")
            return

        # Check for scheduling conflicts
        cursor.execute("SELECT m.title FROM screenings s JOIN movies m ON s.movie_id = m.id WHERE s.hall_id = ? AND s.date = ? AND s.time = ?", (hall[0], date, time))
        conflict = cursor.fetchone()
        if conflict:
            print(f"Conflict: The hall '{hall_name}' is already booked on {date} at {time} for movie '{conflict[0]}'.")
            return

        cursor.execute("INSERT INTO screenings (movie_id, hall_id, date, time, seats_available) VALUES (?, ?, ?, ?, ?)", (movie[0], hall[0], date, time, hall[1]))
        conn.commit()
        print(f"Screening for '{movie_title}' added successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def reserve_seats(movie_title, screening_date, screening_time, customer_name, num_seats):
    """Reserve seats for a specific movie and screening."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.id, s.seats_available FROM screenings s
            JOIN movies m ON s.movie_id = m.id
            WHERE m.title = ? AND s.date = ? AND s.time = ?
        """, (movie_title, screening_date, screening_time))
        screening = cursor.fetchone()
        
        if not screening:
            print(f"Error: No screening found for '{movie_title}' on {screening_date} at {screening_time}.")
            return

        if num_seats > 10:
            print("Error: Maximum 10 seats can be reserved at once. For larger groups, please contact the administrator.")
            return

        if num_seats > screening[1]:
            print(f"Error: Only {screening[1]} seats available for this screening.")
            return

        cursor.execute("INSERT INTO reservations (screening_id, customer_name, seats_reserved) VALUES (?, ?, ?)", (screening[0], customer_name, num_seats))
        cursor.execute("UPDATE screenings SET seats_available = seats_available - ? WHERE id = ?", (num_seats, screening[0]))
        conn.commit()
        print(f"{num_seats} seat(s) reserved for {customer_name} for '{movie_title}' on {screening_date} at {screening_time}.")
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
            SELECT m.title, s.date, s.time, h.name, r.customer_name, r.seats_reserved
            FROM reservations r
            JOIN screenings s ON r.screening_id = s.id
            JOIN movies m ON s.movie_id = m.id
            JOIN halls h ON s.hall_id = h.id
            ORDER BY s.date, s.time
        """)
        reservations = cursor.fetchall()
        
        if not reservations:
            print("No reservations found.")
            return

        current_date = None
        for movie, date, time, hall, customer, seats in reservations:
            if date != current_date:
                print(f"\nDate: {date}")
                current_date = date
            print(f"  Movie: {movie}, Time: {time}, Hall: {hall}")
            print(f"    {customer}: {seats} seat(s)")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def print_daily_schedule(date):
    """Print the schedule for a specific date."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT m.title, h.name, s.time, s.seats_available
            FROM screenings s
            JOIN movies m ON s.movie_id = m.id
            JOIN halls h ON s.hall_id = h.id
            WHERE s.date = ?
            ORDER BY s.time
        """, (date,))
        screenings = cursor.fetchall()
        
        if not screenings:
            print(f"No screenings scheduled for {date}.")
            return

        print(f"\nSchedule for {date}:")
        for movie, hall, time, seats in screenings:
            print(f"  {time} - {movie} in {hall} ({seats} seats available)")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def validate_date(date_str):
    """Validate date string format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

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
        print("4. Print Daily Schedule")
        print("5. Exit")
        
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
            hall_name = input("Enter hall name: ")
            while True:
                date = input("Enter screening date (YYYY-MM-DD): ")
                if validate_date(date):
                    break
                print("Invalid date format. Please use YYYY-MM-DD format.")
            while True:
                time = input("Enter screening time (HH:MM): ")
                if validate_time(time):
                    break
                print("Invalid time format. Please use HH:MM format.")
            add_screening(movie_title, hall_name, date, time)

        elif choice == '3':
            browse_reservations()

        elif choice == '4':
            while True:
                date = input("Enter date to view schedule (YYYY-MM-DD): ")
                if validate_date(date):
                    break
                print("Invalid date format. Please use YYYY-MM-DD format.")
            print_daily_schedule(date)

        elif choice == '5':
            break

        else:
            print("Invalid choice. Please try again.")

def customer_interface():
    """Customer interface for reserving seats."""
    while True:
        print("\nCustomer Menu")
        print("1. Reserve Seats")
        print("2. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            movie_title = input("Enter movie title: ")
            while True:
                date = input("Enter screening date (YYYY-MM-DD): ")
                if validate_date(date):
                    break
                print("Invalid date format. Please use YYYY-MM-DD format.")
            while True:
                time = input("Enter screening time (HH:MM): ")
                if validate_time(time):
                    break
                print("Invalid time format. Please use HH:MM format.")
            customer_name = input("Enter your name: ")
            while True:
                try:
                    num_seats = int(input("Enter number of seats to reserve (max 10): "))
                    if 1 <= num_seats <= 10:
                        break
                    print("Please enter a number between 1 and 10.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
            reserve_seats(movie_title, date, time, customer_name, num_seats)

        elif choice == '2':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    db_path = os.path.abspath(DB_FILE)
    print(f"Using database: {db_path}")
    print(f"Note: To reset the system, delete the file: {db_path}")
    
    create_tables()
    initialize_halls()
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
