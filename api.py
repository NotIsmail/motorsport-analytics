from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

from main import load_season, create_database


DB_NAME = "f1_data.db"

app = FastAPI(
    title="Motorsport Analytics API",
    description="F1 season analytics powered by Jolpica and SQLite",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return sqlite3.connect(DB_NAME)


def is_dnf(status):
    """
    Returns True when a race status represents a genuine DNF.

    Finished and classified/lapped finishes are not DNFs.
    """
    if not status:
        return False

    status = status.strip().lower()

    non_dnf_statuses = [
        "finished",
        "lapped",
        "+1 lap",
        "+2 laps",
        "+3 laps",
        "+4 laps",
        "+5 laps",
        "+6 laps",
        "+7 laps",
        "+8 laps",
        "+9 laps",
        "+10 laps"
    ]

    if status in non_dnf_statuses:
        return False

    if status.startswith("+"):
        return False

    return True


def season_clause(season):
    return "WHERE season = ?", [season]


@app.get("/")
def home():
    return {
        "message": "Motorsport Analytics API",
        "status": "online"
    }


@app.get("/seasons")
def get_seasons():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT season
        FROM results
        ORDER BY season DESC
    """)

    seasons = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return seasons


# =========================================================
# STANDINGS
# =========================================================

@app.get("/standings")
def standings(season: int = 2025):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            driver_id,
            driver_name,
            SUM(points) AS points,
            SUM(
                CASE
                    WHEN position = 1 THEN 1
                    ELSE 0
                END
            ) AS wins,
            SUM(
                CASE
                    WHEN position BETWEEN 1 AND 3 THEN 1
                    ELSE 0
                END
            ) AS podiums,
            COUNT(*) AS races
        FROM results
        WHERE season = ?
        GROUP BY driver_id, driver_name
        ORDER BY points DESC
    """, (season,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "driver_id": row[0],
            "driver_name": row[1],
            "points": row[2],
            "wins": row[3],
            "podiums": row[4],
            "races": row[5]
        }
        for row in rows
    ]


# =========================================================
# DRIVERS
# =========================================================

@app.get("/drivers")
def drivers(season: int = 2025):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT
            driver_id,
            driver_name
        FROM results
        WHERE season = ?
        ORDER BY driver_name
    """, (season,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "driver_id": row[0],
            "driver_name": row[1]
        }
        for row in rows
    ]


@app.get("/drivers/{driver_id}")
def driver_profile(
    driver_id: str,
    season: int = 2025
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            driver_name,
            SUM(points),
            SUM(
                CASE
                    WHEN position = 1 THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN position BETWEEN 1 AND 3 THEN 1
                    ELSE 0
                END
            ),
            COUNT(*),
            AVG(position)
        FROM results
        WHERE driver_id = ?
        AND season = ?
        GROUP BY driver_id, driver_name
    """, (driver_id, season))

    row = cursor.fetchone()

    if not row:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Driver not found for this season."
        )

    cursor.execute("""
        SELECT status
        FROM results
        WHERE driver_id = ?
        AND season = ?
    """, (driver_id, season))

    statuses = [
        row[0]
        for row in cursor.fetchall()
    ]

    dnfs = sum(
        1
        for status in statuses
        if is_dnf(status)
    )

    conn.close()

    return {
        "driver_name": row[0],
        "points": row[1],
        "wins": row[2],
        "podiums": row[3],
        "races": row[4],
        "average_position": round(row[5], 2),
        "dnfs": dnfs
    }


@app.get("/drivers/{driver_id}/races")
def driver_races(
    driver_id: str,
    season: int = 2025
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            round,
            race_name,
            grid,
            position,
            points,
            laps,
            status
        FROM results
        WHERE driver_id = ?
        AND season = ?
        ORDER BY round
    """, (driver_id, season))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "round": row[0],
            "race_name": row[1],
            "grid": row[2],
            "position": row[3],
            "points": row[4],
            "laps": row[5],
            "status": row[6]
        }
        for row in rows
    ]


# =========================================================
# TEAMS
# =========================================================

@app.get("/teams")
def teams(season: int = 2025):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT team
        FROM results
        WHERE season = ?
        ORDER BY team
    """, (season,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {"team": row[0]}
        for row in rows
    ]


@app.get("/teams/{team_name}")
def team_profile(
    team_name: str,
    season: int = 2025
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(points),
            SUM(
                CASE
                    WHEN position = 1 THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN position BETWEEN 1 AND 3 THEN 1
                    ELSE 0
                END
            ),
            COUNT(*),
            AVG(position)
        FROM results
        WHERE team = ?
        AND season = ?
    """, (team_name, season))

    row = cursor.fetchone()

    if not row or row[3] == 0:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Team not found for this season."
        )

    cursor.execute("""
        SELECT status
        FROM results
        WHERE team = ?
        AND season = ?
    """, (team_name, season))

    statuses = [
        row[0]
        for row in cursor.fetchall()
    ]

    dnfs = sum(
        1
        for status in statuses
        if is_dnf(status)
    )

    conn.close()

    return {
        "team": team_name,
        "points": row[0],
        "wins": row[1],
        "podiums": row[2],
        "entries": row[3],
        "average_position": round(row[4], 2),
        "dnfs": dnfs
    }


@app.get("/teams/{team_name}/races")
def team_races(
    team_name: str,
    season: int = 2025
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            round,
            race_name,
            SUM(points) AS points
        FROM results
        WHERE team = ?
        AND season = ?
        GROUP BY round, race_name
        ORDER BY round
    """, (team_name, season))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "round": row[0],
            "race_name": row[1],
            "points": row[2]
        }
        for row in rows
    ]


# =========================================================
# TEAM STANDINGS
# =========================================================

@app.get("/team-standings")
def team_standings(season: int = 2025):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            team,
            SUM(points) AS points,
            SUM(
                CASE
                    WHEN position = 1 THEN 1
                    ELSE 0
                END
            ) AS wins,
            SUM(
                CASE
                    WHEN position BETWEEN 1 AND 3 THEN 1
                    ELSE 0
                END
            ) AS podiums
        FROM results
        WHERE season = ?
        GROUP BY team
        ORDER BY points DESC
    """, (season,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "team": row[0],
            "points": row[1],
            "wins": row[2],
            "podiums": row[3]
        }
        for row in rows
    ]


# =========================================================
# DRIVER COMPARISON
# =========================================================

@app.get("/compare-drivers/{driver_a}/{driver_b}")
def compare_drivers(
    driver_a: str,
    driver_b: str,
    season: int = 2025
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            driver_id,
            driver_name,
            SUM(points),
            SUM(
                CASE
                    WHEN position = 1 THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN position BETWEEN 1 AND 3 THEN 1
                    ELSE 0
                END
            ),
            AVG(position)
        FROM results
        WHERE season = ?
        AND driver_id IN (?, ?)
        GROUP BY driver_id, driver_name
    """, (
        season,
        driver_a,
        driver_b
    ))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "driver_id": row[0],
            "driver_name": row[1],
            "points": row[2],
            "wins": row[3],
            "podiums": row[4],
            "average_position": round(row[5], 2)
        }
        for row in rows
    ]


# =========================================================
# TEAM COMPARISON
# =========================================================

@app.get("/compare-teams/{team_a}/{team_b}")
def compare_teams(
    team_a: str,
    team_b: str,
    season: int = 2025
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            team,
            SUM(points),
            SUM(
                CASE
                    WHEN position = 1 THEN 1
                    ELSE 0
                END
            ),
            SUM(
                CASE
                    WHEN position BETWEEN 1 AND 3 THEN 1
                    ELSE 0
                END
            )
        FROM results
        WHERE season = ?
        AND team IN (?, ?)
        GROUP BY team
    """, (
        season,
        team_a,
        team_b
    ))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "team": row[0],
            "points": row[1],
            "wins": row[2],
            "podiums": row[3]
        }
        for row in rows
    ]


# =========================================================
# QUALIFYING VS RACE
# =========================================================

@app.get("/drivers/{driver_id}/qualifying-vs-race")
def qualifying_vs_race(
    driver_id: str,
    season: int = 2025
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            round,
            race_name,
            grid,
            position
        FROM results
        WHERE driver_id = ?
        AND season = ?
        ORDER BY round
    """, (driver_id, season))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "round": row[0],
            "race_name": row[1],
            "grid": row[2],
            "race_position": row[3]
        }
        for row in rows
    ]


# =========================================================
# CONSISTENCY
# =========================================================

@app.get("/consistency")
def consistency(season: int = 2025):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            driver_id,
            driver_name,
            AVG(position),
            COUNT(*)
        FROM results
        WHERE season = ?
        AND position > 0
        GROUP BY driver_id, driver_name
        HAVING COUNT(*) >= 3
        ORDER BY AVG(position)
    """, (season,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "driver_id": row[0],
            "driver_name": row[1],
            "average_position": round(row[2], 2),
            "races": row[3]
        }
        for row in rows
    ]


# =========================================================
# COMEBACKS
# =========================================================

@app.get("/comebacks")
def comebacks(season: int = 2025):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            driver_name,
            race_name,
            grid,
            position,
            (grid - position) AS positions_gained
        FROM results
        WHERE season = ?
        AND grid > 0
        AND position > 0
        AND grid > position
        ORDER BY positions_gained DESC
        LIMIT 20
    """, (season,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "driver_name": row[0],
            "race_name": row[1],
            "grid": row[2],
            "position": row[3],
            "positions_gained": row[4]
        }
        for row in rows
    ]


# =========================================================
# DNF ANALYSIS
# =========================================================

@app.get("/dnfs")
def dnfs(season: int = 2025):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            driver_id,
            driver_name,
            status
        FROM results
        WHERE season = ?
    """, (season,))

    rows = cursor.fetchall()

    conn.close()

    dnf_counts = {}

    for driver_id, driver_name, status in rows:

        if is_dnf(status):

            if driver_id not in dnf_counts:

                dnf_counts[driver_id] = {
                    "driver_id": driver_id,
                    "driver_name": driver_name,
                    "dnfs": 0
                }

            dnf_counts[driver_id]["dnfs"] += 1

    return sorted(
        dnf_counts.values(),
        key=lambda x: x["dnfs"],
        reverse=True
    )


# =========================================================
# SEASON LOADER
# =========================================================

@app.post("/load-season/{season}")
def load_new_season(season: int):

    if season < 1950:
        raise HTTPException(
            status_code=400,
            detail="Invalid F1 season."
        )

    try:

        create_database()

        result = load_season(season)

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )