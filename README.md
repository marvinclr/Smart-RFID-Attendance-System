# Smart RFID Attendance System

A smart RFID-based attendance system built with Arduino, Flask, and SQLite.  
The system automatically detects entry and exit events and calculates presence duration.

---

## Overview

This project combines hardware and software to create a complete access control and attendance tracking system.  
It processes RFID scans in real time, determines whether the user is entering or leaving, and logs all events in a database.

---

## Features

- RFID badge authentication  
- Automatic entry/exit detection  
- Presence duration calculation  
- REST API built with Flask  
- SQLite database for logging  
- API key protection  
- LED feedback (access granted / denied)

---

## Architecture

RFID Reader → Arduino → Python (Serial) → Flask API → SQLite Database → Response → Arduino

---

## Tech Stack

- Arduino (RFID RC522)
- Python
- Flask
- SQLite
- PySerial

---

## Installation

Clone the repository:

bash git clone https://github.com/your-username/smart-rfid-attendance-system.git cd smart-rfid-attendance-system 

Install dependencies:

bash pip install -r requirements.txt 

Run the server:

bash python app.py 

---

## API

### Endpoint

POST /scan

### Request

json {   "badge_id": "A1B2C3D4",   "api_key": "your_api_key" } 

### Response

json {   "action": "exit",   "status": "granted",   "message": "Sortie d'eleve",   "duration_minutes": 42.5 } 

---

## Database

### students

- id  
- badge_hash  
- nom  
- prenom  
- groupe  
- actif  

### access_logs

- id  
- badge_hash  
- action  
- timestamp  
- status  
- ip_source  
- duration_minutes  

---

## Security

- Badge UID hashing (SHA-256)  
- API key validation  
- Input sanitization  

---

## Future Improvements

- Web dashboard  
- Attendance export (CSV/Excel)  

---

## Author

Marvin
https://github.com/marvinclr
