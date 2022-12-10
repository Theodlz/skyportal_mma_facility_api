import tornado.web
from facilityqueue import FacilityQueue
from handlers.access import auth_or_token
import asyncio

queue = FacilityQueue()

class ObsPlanHandler(tornado.web.RequestHandler):
    @auth_or_token
    async def put(self):
        if not self.request.body:
            self.set_status(400)
            self.finish()
            return
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        try:
            queue.put_nowait(data)
            self.set_status(200)
            self.finish()
            return

        except asyncio.QueueFull:
            self.set_status(400)
            self.finish()
            return
    @auth_or_token
    def get(self):
        # return the current queue
        queued = list(queue._queue)
        return self.write({"queued": queued})

    @auth_or_token
    async def delete(self):
        # delete an item from the queue, based on the queue_name
        queue_name = self.get_argument("queue_name")
        print("Removing", queue_name)
        removed = queue.remove(queue_name)
        if removed:
            self.set_status(200)
        else:
            self.set_status(400)
