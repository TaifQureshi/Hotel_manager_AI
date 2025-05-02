# Hotel_manager_AI
## Room Booking Automation Agent
### Overview
This project is a launch-tool-based AI agent designed to automate the room booking process. It leverages Mistral Instruct, running locally via Ollama, and utilizes MySQL as the database for managing room and booking details.

## Features
1. Automated Booking: The agent efficiently handles room reservations.
2. Database Integration: Stores and retrieves room & booking details using MySQL.
3. Local AI Processing: Powered by Mistral Instruct, running locally with Ollama.
4. Scalable & Fast: Optimized for seamless execution.

## Tech Stack
1. AI Model: Mistral Instruct (via Ollama)
1. Database: MySQL
1. Backend: Python
1. Agent framework: Lanchang, LangGraph


### SQL Query

`
CREATE TABLE Rooms (
    room_id INT PRIMARY KEY,          -- Unique identifier for each room
    room_number VARCHAR(10) NOT NULL, -- Room number
    type VARCHAR(50) NOT NULL,        -- Type of room (e.g., Single, Double, Suite)
    capacity INT NOT NULL,            -- Maximum number of occupants
    price DECIMAL(10,2) NOT NULL,     -- Price per night
    availability BOOLEAN NOT NULL     -- Room availability status
);


CREATE TABLE Bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT, -- Unique identifier for the booking
    room_id INT NOT NULL,                      -- Room ID referencing the Rooms table
    check_in_date DATE NOT NULL,               -- Check-in date for the booking
    check_out_date DATE NOT NULL,              -- Check-out date for the booking
    total_price DECIMAL(10,2) NOT NULL,        -- Total price for the stay
    booking_status VARCHAR(50) NOT NULL,       -- Booking status (e.g., Confirmed, Canceled),
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(10) NOT NULL,
    FOREIGN KEY (room_id) REFERENCES Rooms(room_id) -- Foreign key constraint
);


INSERT INTO Rooms (room_id, room_number, type, capacity, price, availability)
VALUES
    (101, '101', 'Single', 1, 2000.00, TRUE),
    (102, '102', 'Double', 2, 3000.00, TRUE),
    (103, '103', 'Suite', 4, 5000.00, TRUE),
    (104, '104', 'Single', 1, 2200.00, TRUE),
    (105, '105', 'Double', 2, 2800.00, TRUE),
    (106, '106', 'Suite', 4, 5200.00, TRUE),
    (107, '107', 'Single', 1, 2100.00, TRUE),
    (108, '108', 'Double', 2, 3100.00, TRUE),
    (109, '109', 'Suite', 4, 4900.00, TRUE),
    (110, '110', 'Single', 1, 2300.00, TRUE);
`
