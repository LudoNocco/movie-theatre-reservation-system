# movie-theatre-reservation-system
Assignment for the course "Basics of Programming - Exercise" 2 ECTS from UTU University of Turku

# KEY IMPROVEMENTS - STAGE 2 - 07/09/2024:
* Replaced JSON file storage with SQLite database for better data management. The SQLite database provides better data consistency and allows for more complex queries if needed in the future.
* Added constraints to the database schema (e.g., UNIQUE for movie titles).
* Added error handling using try-except blocks throughout the code.
* Implemented input validation, especially for time input (HH:MM format).
* Conflict checking: 
    * Improved conflict checking for screenings.
    * Preventing the same customer from booking the same screening more than once.
    * Enhanced the browse_reservations function to display information more clearly.
