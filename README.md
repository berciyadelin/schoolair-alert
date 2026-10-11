# SchoolAir Alert

Hourly air quality checks for schools, with plain-language alerts when it's unsafe for students to be outside.

**Track:** 01, Air | **Team:** Solo, Berciya Delin G

## Problem
On high-pollution days, many schools don't find out in time to cancel outdoor activities, so children keep breathing unsafe air.

## Solution
Every hour, SchoolAir Alert fetches the US AQI near each school and stores it. If AQI is above 200 it sends a WARNING, and above 300 a SEVERE alert, with simple advice such as "keep students indoors and cancel outdoor PE". A dashboard shows each school as green, yellow, or red.

## Architecture
```
EventBridge (hourly) -> Lambda (fetcher) -> Open-Meteo AQI API
                             |-> RDS PostgreSQL (readings, alerts)
                             |-> SNS (email alerts)

S3 (static dashboard) -> API Gateway -> Lambda (api) -> RDS PostgreSQL
```

## Where AWS fits
| Service | Role |
|---|---|
| EventBridge | Triggers the hourly check |
| Lambda | Fetcher (AQI + alert rules) and dashboard API |
| RDS PostgreSQL | Stores schools, AQI readings, alerts sent |
| SNS | Sends alert emails |
| API Gateway | Exposes `GET /schools` |
| S3 | Hosts the dashboard page |

## Alert rules
- AQI 200 or below: OK
- 201 to 300: WARNING
- Above 300: SEVERE
- No repeat alert for the same school and level within 6 hours

## Project structure
```
schema.sql            database tables
seed/schools.sql      5 sample schools
lambdas/fetcher/      hourly AQI check and alerts
lambdas/api/          dashboard API
frontend/index.html   status dashboard
template.yaml         SAM deploy template
docs/architecture.md  architecture notes
```

## Setup
1. Create an RDS PostgreSQL instance (Free Tier) and note its endpoint.
2. Run `schema.sql`, then `seed/schools.sql`, with `psql`.
3. `sam build` then `sam deploy --guided` (enter DB details and your alert email).
4. Confirm the SNS subscription email from AWS.
5. Put the `ApiUrl` output into `API_URL` in `frontend/index.html`.
6. Upload it: `aws s3 cp frontend/index.html s3://<BucketName>/`
7. Open the `WebsiteUrl` output.

## Tech
Python 3.12, pg8000, PostgreSQL, AWS SAM, plain HTML/JS.
Data source: [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api).

## AI tools used
[List every AI coding tool you used, e.g. Claude]

## Limitations and future work
- One SNS topic for all schools; per-school delivery is next
- DB password in Lambda environment variables; move to Secrets Manager
- AQI comes from modeled data, not on-site sensors
## License
MIT
