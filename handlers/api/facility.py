import tornado.web
from facilityqueue import FacilityQueue
from handlers.access import auth_or_token

queue = FacilityQueue()

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
  