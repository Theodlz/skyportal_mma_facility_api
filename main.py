# create an API using tornado
import asyncio
import tornado.web
from tornado.ioloop import IOLoop
import time

class FacilityQueue(asyncio.Queue):
    async def load_from_db(self):
        # Load items from a database into the queue
        pass

    async def service(self):
        while True:

            # Get the next item from the queue
            item = await self.get()

            # Process the item TODO: implement this
            print("Processing", item)
            updated_item, keep = self.processing(item)

            # If the item should be kept, put it back in the queue
            if keep:
                self.put_nowait(updated_item)

            # Notify the queue that the item has been processed
            self.task_done()

            # reorganize the queue based on the "priority" of the item
            self.reorganize()

            time.sleep(10)

    def reorganize(self):
        # reorganize the queue based on the "priority" of the item
        pass

    def processing(self, item):
        # trigger the obs on the facility, ...
        # return the updated item and a boolean to keep the item in the queue
        return item, True

    def remove(self, queue_name):
        # remove an item from the queue, based on the queue_name
        # loop over the queue and remove the item
        removed = False
        for i, item in enumerate(self._queue):
            if item["queue_name"] == queue_name:
                del self._queue[i]
                removed = True
                break
        return removed
        

queue = FacilityQueue()

class ObsPlanHandler(tornado.web.RequestHandler):
    def put(self):
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        try:
            queue.put_nowait(data)
            self.set_status(200)
        except asyncio.QueueFull:
            self.set_status(400)

    def get(self):
        # return the current queue
        queued = list(queue._queue)
        return self.write({"queued": queued})

    def delete(self):
        # delete an item from the queue, based on the queue_name
        queue_name = self.get_argument("queue_name")
        removed = queue.remove(queue_name)
        if removed:
            self.set_status(200)
        else:
            self.set_status(400)

### TODO BONUS: add a facility handler to return info about the facility
class FacilityHandler(tornado.web.RequestHandler):
    def get(self):
        # return info about the facility, so a list of telescopes with:
        # - telescope:
        #       - name
        #       - status
        #       - location (lat, lon)
        #       - robotic (true or false)
        #       - fixed_location
        #       - instruments:
        #               - name
        #               - type
        #               - filters (list of sncosmo bandpasses)
        #               - gain
        #                - status

        # first you get that from your DB or anywhere that information is stored
        # here, lets put some fake data just to show how it would look like

        telescopes = [
            {
                "name": "cool_telescope_70cm",
                "status": "active",
                "location": {
                    "lat": 0.0,
                    "lon": 0.0
                },
                "robotic": True,
                "fixed_location": True,
                "instruments": [
                    {
                        "name": "cool_camera",
                        "type": "imager",
                        "filters": ["sdssr"],
                        "gain": 1.0,
                        "status": "active"
                    }
                ]
            },
        ]

        return self.write({"telescopes": telescopes})
        
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
    loop.add_callback(queue.load_from_db)
    loop.add_callback(queue.service)
    loop.start()