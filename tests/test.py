import requests
import json
import uuid
from skyportal_mma_facility.models import init_db
from skyportal_mma_facility.utils import load_env, drop_tables, create_tables

env, cfg = load_env()

telescope_id = None
instrument_id = None
obsplan_id = None


def get_telescope():
    url = "http://localhost:8080/api/telescopes/1"
    headers = {"Authorization": "token 123"}

    response = requests.get(url, headers=headers)
    print(f"get_telescope: {response.status_code}")


def post_telescope():
    url = "http://localhost:8080/api/telescopes"
    headers = {"Authorization": "token 123"}

    data = {
        "name": str(uuid.uuid4()),
        "nickname": str(uuid.uuid4()),
        "lat": 0,
        "lon": 0,
        "elevation": 0,
        "diameter": 1,
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"post_telescope: {response.status_code}")
    return response.json()["data"]["id"]


def get_instrument():
    url = "http://localhost:8080/api/instruments/1"
    headers = {"Authorization": "token 123"}

    response = requests.get(url, headers=headers)
    print(f"get_instrument: {response.status_code}")


def post_instrument(telescope_id):
    url = "http://localhost:8080/api/instruments"
    headers = {"Authorization": "token 123"}

    data = {
        "name": str(uuid.uuid4()),
        "type": "imager",
        "band": "Optical",
        "telescope_id": telescope_id,
        "filters": ["ztfr", "ztfg", "ztfi"],
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.json())
    print(f"post_instrument: {response.status_code}")
    return response.json()["data"]["id"]


def post_obsplan(instrument_id):
    url = "http://localhost:8080/api/obsplans"
    headers = {"Authorization": "token 123"}

    data = {
        "queue_name": str(uuid.uuid4()),
        "status": "pending",
        "instrument_id": instrument_id,
        "payload": {
            "start_date": "2021-01-01T00:00:00",
            "end_date": "2021-01-01T00:00:00",
            "exposure_time": 30,
            "exposure_count": 1,
            "maximum_airmass": 2.0,
            "minimum_lunar_distance": 30.0,
            "target_id": 1,
            "observations": [
                {
                    "exposure_time": 30,
                    "filter": "ztfr",
                    "status": "pending",
                    "ra": 0,
                    "dec": 0,
                },
                {
                    "exposure_time": 30,
                    "filter": "ztfg",
                    "status": "pending",
                    "ra": 0,
                    "dec": 0,
                },
                {
                    "exposure_time": 30,
                    "filter": "ztfi",
                    "status": "pending",
                    "ra": 0,
                    "dec": 0,
                },
            ],
        },
    }

    response = requests.post(url, headers=headers, json=data)
    print(f"post_obsplan: {response.status_code}")
    return response.json()["data"]["id"]


if __name__ == "__main__":

    init_db(
        **cfg["database"],
        autoflush=False,
        engine_args={"pool_size": 10, "max_overflow": 15, "pool_recycle": 3600},
    )
    drop_tables()
    create_tables(add=True)

    print("\n")
    telescope_id = post_telescope()

    get_telescope()

    instrument_id = post_instrument(telescope_id)

    get_instrument()

    obsplan_id = post_obsplan(instrument_id)
