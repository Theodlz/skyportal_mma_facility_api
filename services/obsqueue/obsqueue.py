import os
import time
from datetime import datetime
import asyncio
from collections import deque
from skyportal_mma_facility.models import DBSession, ObservationPlan, Observation

from skyportal_mma_facility.models import init_db
from skyportal_mma_facility.utils.env import load_env
from skyportal_mma_facility.utils.log import make_log

log = make_log("obsqueue")

env, cfg = load_env()

init_db(
    **cfg["database"],
    autoflush=False,
    engine_args={"pool_size": 10, "max_overflow": 15, "pool_recycle": 3600},
)

# if it does not exist, create a permanent folder for the observation plans images to be stored
# it should be at the root of the project

root = cfg.get("observation_data_directory", "observations_data")

if not os.path.exists(root):
    os.makedirs(root)


class ObservationPlanQueue(asyncio.Queue):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._queue = deque()
        self._obsplan_id = None

    async def load_plan(self, session):
        loaded_new_plan = False
        timeout = 0
        if len(self._queue) == 0 and self._obsplan_id is not None:
            # label the current plan as done
            obsplan = (
                session.query(ObservationPlan)
                .filter(ObservationPlan.id == self._obsplan_id)
                .first()
            )
            obsplan.status = "done"
            session.commit()
            # set the current plan to None
            self._obsplan_id = None

        if self._obsplan_id is None:
            log("Loading observation plan")
            # get the oldest observation plan that is still pending
            observation_plan = (
                session.query(ObservationPlan)
                .filter(
                    (ObservationPlan.status == "pending")
                    | (ObservationPlan.status == "processing")
                )
                .filter(ObservationPlan.validity_window_start < datetime.utcnow())
                .order_by(ObservationPlan.created_at)
                .first()
            )
            if observation_plan is not None:
                if observation_plan.validity_window_end < datetime.utcnow():
                    # the observation plan is not valid anymore, skip it
                    observation_plan.status = "missed"
                    session.commit()
                    timeout = 15
                else:
                    # set the observation plan to processing
                    observation_plan.status = "processing"
                    session.commit()
                    # add the observation plan to the queue
                    self._obsplan_id = observation_plan.id
                    log(f"Added {observation_plan.queue_name} to the queue")
                    loaded_new_plan = True
            else:
                # wait 5 seconds and try again
                timeout = 15

        return loaded_new_plan, timeout

    async def load_queue(self, session):
        # get all the observation that are still pending for the current observation plan
        observations = (
            session.query(Observation)
            .filter(
                (Observation.observation_plan_id == self._obsplan_id)
                & (
                    (Observation.status == "pending")
                    | (Observation.status == "processing")
                )
            )
            .all()
        )
        for observation in observations:
            await self.put(observation.id)

    async def service(self):
        while True:
            # if the queue is empty, load the oldest observation plan that is still pending
            try:
                with DBSession() as session:

                    loaded_new_plan, timeout = await self.load_plan(session)

                    if loaded_new_plan:
                        await self.load_queue(session)

                    if timeout > 0:
                        await asyncio.sleep(timeout)

                    if len(self._queue) > 0:
                        item = await self.get()
                        log(f"Got {item} from the queue")
                        await self.processing(item, session)
                        self.task_done()
            except Exception as e:
                await asyncio.sleep(5)

    async def processing(self, item, session):
        # trigger the obs on the facility, ...
        # return the updated item and a boolean to keep the item in the queue
        obs = session.query(Observation).get(item)
        obs.status = "processing"
        session.commit()

        log(f"Processing {obs.id}")
        ### TODO: trigger the observation on the facility, and update the status of the observation along with the result
        ### For now, we fake that part

        ### FAKE PROCESSING
        await asyncio.sleep(10)
        path = os.path.join(root, f"{obs.id}.fits")
        with open(path, "w") as f:
            f.write("This is a fake image")
        ### END FAKE PROCESSING

        obs.save(path)
        obs.status = "done"
        session.commit()


queue = ObservationPlanQueue()

log("Waiting for the database to be ready")
db_connected = 0
while db_connected < 10:
    try:
        with DBSession() as session:
            obsplan = session.query(ObservationPlan).first()
            db_connected += 1
            time.sleep(1)
    except Exception as e:
        log(f"Coud not connect to the database, retrying in 5 seconds")
        time.sleep(1)

log("Starting the queue service")

loop = asyncio.get_event_loop()
loop.create_task(queue.service())
loop.run_forever()
