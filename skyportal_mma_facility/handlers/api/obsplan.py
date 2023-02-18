from psycopg2.errors import UniqueViolation
from astropy.time import Time

from skyportal_mma_facility.handlers.api import BaseHandler
from skyportal_mma_facility.utils.access import auth_or_token
from skyportal_mma_facility.utils import make_log, load_env

from skyportal_mma_facility.models import (
    Telescope,
    Instrument,
    Observation,
    ObservationPlan,
)

log = make_log("obsplan")

env, cfg = load_env()


class ObservationPlanHandler(BaseHandler):
    # @auth_or_token
    def put(self):
        data = self.get_json()

        with self.Session() as session:
            try:
                data["status"] = "pending"
                observations = data["targets"]

                observation_plan = ObservationPlan(
                    queue_name=data["queue_name"],
                    user=data["user"],
                    status=data["status"],
                    instrument_id=1,  # fake for now, until skyportal provides the instrument name
                    validity_window_start=Time(
                        data["validity_window_mjd"][0], format="mjd"
                    ).datetime,
                    validity_window_end=Time(
                        data["validity_window_mjd"][1], format="mjd"
                    ).datetime,
                    payload=data,
                )
                session.add(observation_plan)
                session.commit()

                for observation in observations:
                    # create the observation
                    obs = Observation(
                        request_id=observation["request_id"],
                        field_id=observation["field_id"],
                        ra=observation["ra"],
                        dec=observation["dec"],
                        filter=observation["filter"],
                        exposure_time=observation["exposure_time"],
                        program_pi=observation["program_pi"],
                        observation_plan_id=observation_plan.id,
                        instrument_id=1,  # fake for now, until skyportal provides the instrument name
                    )
                    session.add(obs)
                session.commit()

                return self.success(data={"id": observation_plan.id})

            except Exception as e:
                print(e)
                # print the attrivutes of the exception
                session.rollback()
                if isinstance(e.orig, UniqueViolation):
                    return self.error(
                        "An observation plan with this name already exists"
                    )
                else:
                    print(e)
                    return self.error("Error adding observation plan")

    def get(self, observation_plan_id=None):
        try:
            with self.Session() as session:
                # get the inquery parameters
                status = self.get_query_argument("status", None)
                if status is not None:
                    status = status.lower()
                    if status not in ["pending", "processing", "done", "failed"]:
                        return self.error(
                            "Status must be one of pending, processing, done, or failed"
                        )

                if status is not None and observation_plan_id is not None:
                    return self.error(
                        "Cannot specify both status and observation plan ID"
                    )

                if observation_plan_id is not None:
                    observation_plan = session.query(ObservationPlan).get(
                        observation_plan_id
                    )
                    if observation_plan is None:
                        return self.error(
                            f"Could not find observation plan with ID {observation_plan_id}"
                        )
                    # return the observation plan with the observations
                    observation_plan.observations
                    return self.success(data=observation_plan)
                elif status is not None:
                    observation_plans = (
                        session.query(ObservationPlan)
                        .filter(ObservationPlan.status == status)
                        .all()
                    )
                    return self.success(data=observation_plans)
                else:
                    observation_plans = session.query(ObservationPlan).all()
                    return self.success(data=observation_plans)
        except Exception as e:
            print(e)
            return self.error("Error retrieving observation plan(s)")
