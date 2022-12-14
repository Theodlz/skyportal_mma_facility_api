# this is a microservice that is used to run the app

import tornado.web
from tornado.ioloop import IOLoop
from skyportal_mma_facility.utils.env import load_env
from skyportal_mma_facility.app_server import make_app

env, cfg = load_env()

app = make_app(cfg)

port = cfg["server.port"]

address = "127.0.0.1"

app.listen(port, xheaders=True, address=address)

print(f"Listening on {address}:{port}")
tornado.ioloop.IOLoop.current().start()
