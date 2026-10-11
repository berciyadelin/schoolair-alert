# lambdas/fetcher/app.py: runs every hour via EventBridge
import json
import os
import urllib.request

import boto3
import pg8000.native

sns = boto3.client("sns")
TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]


def get_conn():
    return pg8000.native.Connection(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def fetch_aqi(lat, lon):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}&current=us_aqi"
    )
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)
    return int(data["current"]["us_aqi"])


def classify(aqi):
    if aqi > 300:
        return "SEVERE"
    if aqi > 200:
        return "WARNING"
    return "OK"


def build_message(name, aqi, level):
    if level == "SEVERE":
        return (f"SEVERE: AQI {aqi} near {name}. Keep students indoors, "
                "cancel all outdoor activities, and keep windows closed.")
    return (f"WARNING: AQI {aqi} near {name}. Keep students indoors "
            "and cancel outdoor PE.")


def already_alerted(conn, school_id, level):
    rows = conn.run(
        "SELECT 1 FROM alerts WHERE school_id = :s AND level = :l "
        "AND sent_at > NOW() - INTERVAL '6 hours' LIMIT 1",
        s=school_id, l=level,
    )
    return len(rows) > 0


def lambda_handler(event, context):
    conn = get_conn()
    results = []
    try:
        schools = conn.run("SELECT id, name, lat, lon FROM schools")
        for school_id, name, lat, lon in schools:
            try:
                aqi = fetch_aqi(float(lat), float(lon))
            except Exception as e:
                print(f"AQI fetch failed for {name}: {e}")
                continue

            conn.run(
                "INSERT INTO aqi_readings (school_id, aqi) VALUES (:s, :a)",
                s=school_id, a=aqi,
            )

            level = classify(aqi)
            if level != "OK" and not already_alerted(conn, school_id, level):
                msg = build_message(name, aqi, level)
                sns.publish(
                    TopicArn=TOPIC_ARN,
                    Subject=f"SchoolAir {level}: {name}"[:100],
                    Message=msg,
                )
                conn.run(
                    "INSERT INTO alerts (school_id, level, message) "
                    "VALUES (:s, :l, :m)",
                    s=school_id, l=level, m=msg,
                )
            results.append({"school": name, "aqi": aqi, "level": level})
    finally:
        conn.close()

    print(json.dumps(results))
    return {"statusCode": 200, "body": json.dumps(results)}
