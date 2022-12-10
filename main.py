import tornado.web
from tornado.ioloop import IOLoop

from facilityqueue import FacilityQueue

from handlers import (
    FacilityHandler,
    ObsPlanHandler
)
queue = FacilityQueue()
    
def make_app():
    return tornado.web.Application([
        (r"/api/facility", FacilityHandler),
        (r"/api/obsplans", ObsPlanHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    print("Listening on port 8080")
    
    loop = IOLoop.current()
    #loop.add_callback(queue.load_from_db)
    loop.add_callback(queue.service)
    loop.start()