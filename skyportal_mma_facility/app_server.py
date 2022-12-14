import tornado.web
from tornado.ioloop import IOLoop

from skyportal_mma_facility.models import init_db
from skyportal_mma_facility.utils.env import load_env
from skyportal_mma_facility.utils.model_util import create_tables, drop_tables

env, cfg = load_env()

from skyportal_mma_facility.handlers.api import (
    TelescopeHandler,
    InstrumentHandler,
    ObservationPlanHandler,
)

handlers = [
    (r"/api/telescopes(/[0-9]+)?", TelescopeHandler),
    (r"/api/instruments(/[0-9]+)?", InstrumentHandler),
    (r"/api/obsplans(/[0-9]+)?", ObservationPlanHandler),
]

settings = {
    "debug": env.debug,
    "autoreload": env.debug,
}


def make_app(cfg):
    app = tornado.web.Application(handlers, **settings)

    init_db(
        **cfg["database"],
        autoflush=False,
        engine_args={"pool_size": 10, "max_overflow": 15, "pool_recycle": 3600},
    )
    if env.debug:
        drop_tables()
    create_tables(add=env.debug)

    app.cfg = cfg

    return app


if __name__ == "__main__":
    app = make_app(cfg)

    app.listen(8080)
    print("Listening on port 8080")

    loop = IOLoop.current()
    # loop.add_callback(queue.load_from_db)
    # loop.add_callback(queue.service)
    loop.start()
