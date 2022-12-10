import asyncio
import tornado.web
from tornado.ioloop import IOLoop
import time
from tornado import gen
from collections import deque

__name__ = "facilityqueue"

class _FacilityQueue(asyncio.Queue):
    async def load_from_db(self):
        # Load items from a database into the queue
        pass
    
    @gen.coroutine
    def service(self):
        while True:

            # Get the next item from the queue
            item = yield self.get()
            #print(f"Processing {item['queue_name']} with priority {item['priority']}")
            print(f"Processing {item['queue_name']}")

            # Process the item
            item, keep = yield self.processing(item)

            if keep:
                self.put_nowait(item)

            # Reorganize the queue based on priority if there is any need to do so
            #yield self.reorganize()

            yield gen.sleep(2)

            self.task_done()

    def reorganize(self):
        # reorganize the queue based on the "priority" of the item
        # sort the queue based on the priority, which is an integer from 1 to 5
        # 1 is the highest priority
        # 5 is the lowest priority
        self._queue = deque(sorted(self._queue, key=lambda k: int(k["priority"])))

    async def processing(self, item):
        # trigger the obs on the facility, ...
        # return the updated item and a boolean to keep the item in the queue
        return item, True

    async def remove(self, queue_name):
        # remove an item from the queue, based on the queue_name
        # loop over the queue and remove the item
        removed = False
        for i, item in enumerate(self._queue):
            if item["queue_name"] == queue_name:
                del self._queue[i]
                removed = True
                break
        return removed
        
# based on a singleton pattern, create a single instance of the queue

class FacilityQueue(_FacilityQueue):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FacilityQueue, cls).__new__(cls)
        return cls._instance