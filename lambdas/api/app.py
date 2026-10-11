# lambdas/api/app.py: GET /schools, called by the dashboard
import json
import os

import pg8000.native

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",  # lets the S3 page call this API
}


def get_conn():
    return pg8000.native.Connection(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def status_for(aqi):
    if aqi is None:
        return "unknown"
    if aqi > 200:
        return "red"
    if aqi > 100:
        return "yellow"
    return "green"


def lambda_handler(event, context):
    conn = get_conn()
    try:
        rows = conn.run(
            "SELECT s.id, s.name, s.city, r.aqi, r.fetched_at "
            "FROM schools s "
            "LEFT JOIN LATERAL ("
            "  SELECT aqi, fetched_at FROM aqi_readings "
            "  WHERE school_id = s.id "
            "  ORDER BY fetched_at DESC LIMIT 1"
            ") r ON TRUE "
            "ORDER BY s.name"
        )
    finally:
        conn.close()

    schools = [
        {
            "id": sid,
            "name": name,
            "city": city,
            "aqi": aqi,
            "status": status_for(aqi),
            "updated_at": fetched.isoformat() if fetched else None,
        }
        for sid, name, city, aqi, fetched in rows
    ]
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps({"schools": schools}),
  }
