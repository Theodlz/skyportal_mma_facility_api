from psycopg2.errors import UniqueViolation

from skyportal_mma_facility.handlers.api import BaseHandler
from skyportal_mma_facility.utils.access import auth_or_token

from skyportal_mma_facility.models import (
    Telescope,
    Instrument,
    Observation,
    ObservationPlan,
)


class ObservationPlanHandler(BaseHandler):
    # @auth_or_token
    def post(self):
        data = self.get_json()

        try:
            with self.Session() as session:
                data["status"] = "pending"

                observations = data["payload"]["observations"]
                del data["payload"]["observations"]

                observation_plan = ObservationPlan(**data)
                session.add(observation_plan)
                session.commit()

                instrument_id = data["instrument_id"]

                for observation in observations:
                    # create the observation
                    obs = Observation(
                        exposure_time=observation["exposure_time"],
                        filter=observation["filter"],
                        status="pending",
                        instrument_id=1,
                        observation_plan_id=observation_plan.id,
                    )
                    session.add(obs)
                session.commit()

                return self.success(data={"id": observation_plan.id})

        except Exception as e:
            print(e)
            # print the attrivutes of the exception
            if isinstance(e.orig, UniqueViolation):

                return self.error("An observation plan with this name already exists")
            else:
                print(e)
                return self.error("Error adding observation plan")
