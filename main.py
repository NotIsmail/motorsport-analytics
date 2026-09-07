import requests
import sqlite3
import time


DB_NAME = "f1_data.db"

BASE_URL = "https://api.jolpi.ca/ergast/f1"


# ==================================================
# DATABASE
# ==================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def create_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            season INTEGER,
            round INTEGER,
            race_name TEXT,

            driver_id TEXT,
            driver_name TEXT,

            team TEXT,

            grid INTEGER,
            position INTEGER,

            points REAL,
            laps INTEGER,

            status TEXT
        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# CHECK IF SEASON EXISTS
# ==================================================

def season_exists(season):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM results
        WHERE season = ?
    """, (season,))

    count = cursor.fetchone()[0]

    conn.close()

    return count > 0


# ==================================================
# GET RACES
# ==================================================

def get_races(season):

    url = f"{BASE_URL}/{season}/races/"

    response = requests.get(url)

    response.raise_for_status()

    data = response.json()

    return data["MRData"]["RaceTable"]["Races"]


# ==================================================
# GET RESULTS
# ==================================================

def get_results(season, round_number):

    url = (
        f"{BASE_URL}/"
        f"{season}/"
        f"{round_number}/"
        f"results/"
    )

    while True:

        response = requests.get(url)

        if response.status_code == 429:

            print(
                "Rate limited by API. "
                "Waiting 5 seconds..."
            )

            time.sleep(5)

            continue

        response.raise_for_status()

        break

    data = response.json()

    races = data["MRData"]["RaceTable"]["Races"]

    if not races:
        return []

    return races[0]["Results"]


# ==================================================
# LOAD SEASON
# ==================================================

def load_season(season):

    print()
    print("=" * 50)
    print(f"Loading {season} season")
    print("=" * 50)


    # ----------------------------------------------
    # DUPLICATE CHECK
    # ----------------------------------------------

    if season_exists(season):

        print(
            f"{season} is already in the database."
        )

        return {
            "success": False,
            "message": f"{season} is already in the database.",
            "season": season,
            "results_inserted": 0
        }


    # ----------------------------------------------
    # GET RACES
    # ----------------------------------------------

    print(
        f"Fetching {season} race calendar..."
    )

    races = get_races(season)

    print(
        f"Found {len(races)} races."
    )


    conn = get_connection()
    cursor = conn.cursor()


    total_results = 0


    # ----------------------------------------------
    # FETCH EACH RACE
    # ----------------------------------------------

    for race in races:

        round_number = int(
            race["round"]
        )

        race_name = race["raceName"]


        print(
            f"Fetching Round "
            f"{round_number}: "
            f"{race_name}"
        )


        results = get_results(
            season,
            round_number
        )


        # ------------------------------------------
        # STORE RESULTS
        # ------------------------------------------

        for result in results:

            driver = result["Driver"]

            constructor = result["Constructor"]


            driver_id = driver["driverId"]


            driver_name = (
                driver["givenName"]
                + " "
                + driver["familyName"]
            )


            team = constructor["name"]


            grid = int(
                result.get("grid", 0)
            )


            try:

                position = int(
                    result.get("position", 0)
                )

            except ValueError:

                position = 0


            points = float(
                result.get("points", 0)
            )


            laps = int(
                result.get("laps", 0)
            )


            status = result.get(
                "status",
                "Unknown"
            )


            cursor.execute("""
                INSERT INTO results (

                    season,
                    round,
                    race_name,

                    driver_id,
                    driver_name,

                    team,

                    grid,
                    position,

                    points,
                    laps,

                    status

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            """, (

                season,
                round_number,
                race_name,

                driver_id,
                driver_name,

                team,

                grid,
                position,

                points,
                laps,

                status

            ))


            total_results += 1


        # Save after every race

        conn.commit()


        # Avoid API rate limiting

        time.sleep(1)


    conn.close()


    print()
    print(
        f"Finished loading {season}."
    )

    print(
        f"Inserted {total_results} results."
    )


    return {
        "success": True,
        "message": f"{season} loaded successfully.",
        "season": season,
        "results_inserted": total_results
    }


# ==================================================
# COMMAND LINE MODE
# ==================================================

def command_line_loader():

    create_database()


    print()
    print("Motorsport Analytics Data Loader")
    print("--------------------------------")


    season_input = input(
        "Enter F1 season to load: "
    )


    try:

        season = int(
            season_input
        )

    except ValueError:

        print(
            "Please enter a valid year."
        )

        return


    load_season(season)


# ==================================================
# RUN DIRECTLY
# ==================================================

if __name__ == "__main__":

    command_line_loader()