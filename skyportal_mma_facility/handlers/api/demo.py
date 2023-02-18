# import Session from sqlalchemy stuff

from sqlalchemy.orm.session import Session
from astropy.time import Time
import uuid

from skyportal_mma_facility.handlers.api import BaseHandler
from skyportal_mma_facility.utils.access import auth_or_token

from skyportal_mma_facility.models import (
    Telescope,
    Instrument,
    ObservationPlan,
    Observation,
)


def post_demo(session: Session) -> int:
    name = str(uuid.uuid4())
    telescope = Telescope(
        name=name, nickname=name, diameter=1.0, robotic=True, fixed_location=True
    )
    session.add(telescope)
    session.commit()

    instrument = Instrument(
        name=name,
        type="imager",
        band="optical",
        filters=["ztfg", "ztfr", "ztfi"],
        telescope_id=telescope.id,
    )
    session.add(instrument)
    session.commit()

    data = {
        "targets": [
            {
                "request_id": 1,
                "field_id": 247,
                "ra": 15.94654,
                "dec": -24.25,
                "filter": "g",
                "exposure_time": 300,
                "program_pi": "provisioned-admin",
            },
            {
                "request_id": 2,
                "field_id": 247,
                "ra": 15.94654,
                "dec": -24.25,
                "filter": "r",
                "exposure_time": 300,
                "program_pi": "provisioned-admin",
            },
            {
                "request_id": 3,
                "field_id": 247,
                "ra": 15.94654,
                "dec": -24.25,
                "filter": "g",
                "exposure_time": 300,
                "program_pi": "provisioned-admin",
            },
            {
                "request_id": 4,
                "field_id": 246,
                "ra": 8.55346,
                "dec": -24.25,
                "filter": "g",
                "exposure_time": 300,
                "program_pi": "provisioned-admin",
            },
            {
                "request_id": 5,
                "field_id": 246,
                "ra": 8.55346,
                "dec": -24.25,
                "filter": "r",
                "exposure_time": 300,
                "program_pi": "provisioned-admin",
            },
            {
                "request_id": 6,
                "field_id": 246,
                "ra": 8.55346,
                "dec": -24.25,
                "filter": "g",
                "exposure_time": 300,
                "program_pi": "provisioned-admin",
            },
        ],
        "queue_name": f"{name}",
        "validity_window_mjd": [59992.897391105056, 59999.605079270834],
        "queue_type": "list",
        "user": "provisioned-admin",
        "status": "pending",
    }

    observation_plan = ObservationPlan(
        queue_name=data["queue_name"],
        user=data["user"],
        status=data["status"],
        instrument_id=instrument.id,
        validity_window_start=Time(
            data["validity_window_mjd"][0], format="mjd"
        ).datetime,
        validity_window_end=Time(data["validity_window_mjd"][1], format="mjd").datetime,
        payload=data,
    )
    session.add(observation_plan)
    session.commit()

    for observation in data["targets"]:
        obs = Observation(
            request_id=observation["request_id"],
            field_id=observation["field_id"],
            ra=observation["ra"],
            dec=observation["dec"],
            filter=observation["filter"],
            exposure_time=observation["exposure_time"],
            program_pi=observation["program_pi"],
            observation_plan_id=observation_plan.id,
            instrument_id=instrument.id,
        )
        session.add(obs)
        session.commit()

    return observation_plan.id


class DemoHandler(BaseHandler):
    def get(self):
        with self.Session() as session:
            observation_plan_id = post_demo(session)
            return self.success(data={"id": observation_plan_id})

    def post(self):
        with self.Session() as session:
            observation_plan_id = post_demo(session)
            return self.success(data={"id": observation_plan_id})
