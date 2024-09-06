import json

# Define file paths
MOVIES_FILE = 'movies.json'
SCREENINGS_FILE = 'screenings.json'
RESERVATIONS_FILE = 'reservations.json'

def load_data(file_path):
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_data(file_path, data):
    """Save data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def add_movie(movies, title, duration):
    """Add a movie to the list of movies."""
    movies[title] = {
        'title': title,
        'duration': duration
    }
    save_data(MOVIES_FILE, movies)

def add_screening(screenings, movie_title, hall, time):
    """Add a screening to the list of screenings."""
    # Check for scheduling conflicts
    for existing_movie, times in screenings.items():
        for screening in times:
            if screening['hall'] == hall and screening['time'] == time:
                print(f"Conflict: The hall '{hall}' is already booked at '{time}' for movie '{existing_movie}'.")
                return

    if movie_title not in screenings:
        screenings[movie_title] = []
    screenings[movie_title].append({
        'hall': hall,
        'time': time
    })
    save_data(SCREENINGS_FILE, screenings)

def reserve_seat(reservations, movie_title, screening_time, customer_name):
    """Reserve a seat for a specific movie and screening."""
    if movie_title not in reservations:
        reservations[movie_title] = {}
    if screening_time not in reservations[movie_title]:
        reservations[movie_title][screening_time] = []
    reservations[movie_title][screening_time].append(customer_name)
    save_data(RESERVATIONS_FILE, reservations)

def browse_reservations(reservations):
    """Display all reservations."""
    for movie, screenings in reservations.items():
        print(f"Movie: {movie}")
        for time, customers in screenings.items():
            print(f"  Screening at {time}: {', '.join(customers)}")

def admin_interface():
    """Administrator interface for managing movies, screenings, and reservations."""
    movies = load_data(MOVIES_FILE)
    screenings = load_data(SCREENINGS_FILE)
    reservations = load_data(RESERVATIONS_FILE)

    while True:
        print("\nAdmin Menu")
        print("1. Add Movie")
        print("2. Add Screening")
        print("3. Browse Reservations")
        print("4. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            title = input("Enter movie title: ")
            duration = input("Enter movie duration (in minutes): ")
            add_movie(movies, title, duration)

        elif choice == '2':
            movie_title = input("Enter movie title: ")
            hall = input("Enter hall name: ")
            time = input("Enter screening time (HH:MM): ")
            add_screening(screenings, movie_title, hall, time)

        elif choice == '3':
            browse_reservations(reservations)

        elif choice == '4':
            break

        else:
            print("Invalid choice. Please try again.")

def customer_interface():
    """Customer interface for reserving seats."""
    screenings = load_data(SCREENINGS_FILE)
    reservations = load_data(RESERVATIONS_FILE)

    while True:
        print("\nCustomer Menu")
        print("1. Reserve Seat")
        print("2. Exit")
        
        choice = input("Enter choice: ")

        if choice == '1':
            movie_title = input("Enter movie title: ")
            if movie_title not in screenings:
                print("Movie not found.")
                continue
            time = input("Enter screening time (HH:MM): ")
            # Check if screening time exists for the movie
            if not any(screening['time'] == time for screening in screenings[movie_title]):
                print("Screening not found.")
                continue
            customer_name = input("Enter your name: ")
            reserve_seat(reservations, movie_title, time, customer_name)

        elif choice == '2':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
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