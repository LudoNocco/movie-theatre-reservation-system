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

# KEY IMPROVEMENTS - STAGE 3 - 29/09/2024:
* The database now stores information about the five halls with their capacities. More specifically, I created 5 halls:
   * 1 small one with only 50 seats, named Oak
   * 2 medium ones with 150 seats, named Birch and Maple
   * 2 large ones with 300 seats, named Pine and Cedar
* Administrators can add screenings with dates and specific halls.
* Administrators can view the daily schedule for the theater (i.e., what's on where).
* Customers can reserve multiple seats (up to 10) for a screening (fair usage policy, need to contact administrator for large group bookings).
* The system checks for seat availability before allowing reservations.
