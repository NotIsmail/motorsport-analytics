# Motorsport Analytics Dashboard

An interactive Formula 1 analytics dashboard for exploring race performance, championship standings, driver consistency, constructor performance, and multi-season trends.

The project retrieves Formula 1 data from the Jolpica F1 API, processes it using Python, stores it in SQLite, exposes analytics through FastAPI, and presents the results through an interactive web dashboard.

---

## Features

- Multi-season Formula 1 analysis
- Driver championship standings
- Constructor championship standings
- Driver performance analysis
- Driver vs driver comparison
- Team vs team comparison
- Race-by-race performance
- Driver consistency analysis
- Biggest race comebacks
- DNF analysis
- Constructor championship progression
- Dynamic season loading through the dashboard

---

## Architecture

    Jolpica F1 API
           |
           v
    Python Data Ingestion
           |
           v
    SQLite Database
           |
           v
    FastAPI REST API
           |
           v
    HTML / JavaScript Dashboard
           |
           v
    Chart.js Visualizations

---

## Technology Stack

- **Python** — data ingestion and processing
- **Requests** — REST API communication
- **SQLite** — local analytical database
- **FastAPI** — REST API backend
- **JavaScript** — dashboard logic
- **HTML/CSS** — dashboard interface
- **Chart.js** — data visualization
- **REST APIs** — data communication

---

## Project Structure

    motorsports-analytics/
    │
    ├── main.py
    ├── api.py
    ├── index.htm
    ├── requirements.txt
    ├── README.md
    └── .gitignore

---

## How It Works

### 1. Data Ingestion

The Python data loader retrieves Formula 1 race data from the Jolpica F1 API.

Run:

    python main.py

The program asks for the F1 season to load and retrieves the available race results.

The dashboard can also request a new season through the FastAPI backend.

---

### 2. Database

The project uses SQLite to store Formula 1 race-result data.

The database contains information including:

- Season
- Race round
- Race name
- Driver
- Constructor
- Starting grid position
- Finishing position
- Points
- Laps
- Race status

The SQLite database is generated locally and excluded from Git using `.gitignore`.

---

### 3. FastAPI Backend

FastAPI exposes the stored data through REST API endpoints.

#### Season and Championship Endpoints

    GET /seasons
    GET /standings?season=2025
    GET /team-standings?season=2025
    GET /drivers?season=2025
    GET /teams?season=2025

#### Driver Analysis

    GET /drivers/{driver_id}?season=2025
    GET /drivers/{driver_id}/races?season=2025
    GET /drivers/{driver_id}/qualifying-vs-race?season=2025

#### Team Analysis

    GET /teams/{team_name}?season=2025
    GET /teams/{team_name}/races?season=2025

#### Comparisons

    GET /compare-drivers/{driver_a}/{driver_b}?season=2025
    GET /compare-teams/{team_a}/{team_b}?season=2025

#### Additional Analytics

    GET /consistency?season=2025
    GET /comebacks?season=2025
    GET /dnfs?season=2025

#### Season Ingestion

A new season can be loaded through:

    POST /load-season/{season}

FastAPI also provides interactive API documentation through Swagger UI.

---

## Dashboard

The frontend communicates with the FastAPI backend and presents the results through interactive tables, metrics, and charts.

The dashboard supports:

- Switching between available seasons
- Loading additional seasons
- Selecting individual drivers
- Selecting individual constructors
- Comparing drivers
- Comparing constructors
- Viewing race-by-race performance
- Exploring consistency statistics
- Exploring comeback statistics
- Exploring DNF statistics
- Viewing championship progression

---

## Data Pipeline

The project follows an ETL-style data pipeline:

    Extract
       |
       v
    Jolpica F1 API
       |
       v
    Transform
       |
       v
    Python
       |
       v
    Load
       |
       v
    SQLite
       |
       v
    Serve
       |
       v
    FastAPI
       |
       v
    Visualize
       |
       v
    JavaScript + Chart.js

---

## Running Locally

### 1. Clone the Repository

    git clone https://github.com/NotIsmail/motorsports-analytics.git
    cd motorsports-analytics



---

### 2. Install Dependencies

    pip install -r requirements.txt

---

### 3. Start the FastAPI Backend

    python -m uvicorn api:app --reload

The API will be available at:

    http://127.0.0.1:8000

---

### 4. Open the API Documentation

FastAPI automatically provides interactive Swagger UI documentation at:

    http://127.0.0.1:8000/docs

This allows the available API endpoints to be tested directly from the browser.

---

### 5. Start the Dashboard

Open another terminal in the project folder and run:

    python -m http.server 5500 --bind 127.0.0.1

Then open:

    http://127.0.0.1:5500

---

## Loading a New Season

A new Formula 1 season can be loaded from the dashboard using the **Add Season** control.

The process is:

    Dashboard
        |
        v
    POST /load-season/{season}
        |
        v
    FastAPI
        |
        v
    Python Data Loader
        |
        v
    Jolpica F1 API
        |
        v
    SQLite Database
        |
        v
    Dashboard refresh

A season that already exists in the database is not downloaded again.

---

## Example Analytics

The dashboard can be used to investigate questions such as:

- Who led the championship in a particular season?
- Which drivers scored the most wins?
- Which drivers achieved the most podiums?
- Which drivers were the most consistent?
- Which drivers gained the most positions during races?
- Which constructors scored the most points?
- How did two drivers compare during a season?
- How did two constructors compare?
- Which drivers experienced the most retirements?
- How did a constructor's points accumulate throughout a season?

---

## Data Source

Formula 1 race data is retrieved from the Jolpica F1 API.

The API provides structured Formula 1 data that is consumed by the Python ingestion pipeline and stored locally for analysis.

---

## Project Goals

This project was built to combine:

- Data ingestion
- REST API consumption
- Python data processing
- SQL-based analytics
- Backend API development
- Data visualization
- Interactive dashboard development

It also serves as a practical application of data engineering and analytics concepts using real-world motorsport data.

---

## Future Improvements

Potential future extensions include:

- Lap-time analysis
- Pit-stop analysis
- Tyre strategy analysis
- Sprint-race analysis
- Advanced race pace analysis
- Visual overhaul with a richer motorsport-focused interface
- Expanded motorsport coverage beyond Formula 1
- Support for analytics across multiple racing series and disciplines
- Additional motorsport datasets
- Public cloud deployment

---

## Author

**Mohammed Ismail**

Computer Science & Engineering student interested in cybersecurity, data analytics, cloud computing, and motorsport.