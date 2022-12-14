from psycopg2.errors import UniqueViolation

from skyportal_mma_facility.handlers.api import BaseHandler
from skyportal_mma_facility.utils.access import auth_or_token

from skyportal_mma_facility.models import Telescope, Instrument


class TelescopeHandler(BaseHandler):
    def get(self, telescope_id=None):
        try:
            with self.Session() as session:
                if telescope_id is not None:
                    telescope = session.query(Telescope).get(telescope_id)
                    if telescope is None:
                        return self.error(
                            f"Could not find telescope with ID {telescope_id}"
                        )
                    # return the telescope with the instruments
                    telescope.instruments
                    return self.success(data=telescope)

                else:
                    telescopes = session.query(Telescope).all()
                    for telescope in telescopes:
                        telescope.instruments
                    return self.success(data=telescopes)
        except Exception as e:
            print(e)
            return self.error("Error retrieving telescope(s)")

    @auth_or_token
    def post(self):
        data = self.get_json()

        try:
            with self.Session() as session:
                telescope = Telescope(**data)
                session.add(telescope)
                session.commit()

                return self.success(data={"id": telescope.id})

        except Exception as e:
            if isinstance(e.orig, UniqueViolation):
                return self.error("A telescope with this name already exists")
            else:
                return self.error("Error adding telescope")


class InstrumentHandler(BaseHandler):
    def get(self, instrument_id=None):
        try:
            with self.Session() as session:
                if instrument_id is not None:
                    instrument = session.query(Instrument).get(instrument_id)
                    if instrument is None:
                        return self.error(
                            f"Could not find instrument with ID {instrument_id}"
                        )
                    return self.success(data=instrument.to_dict())

                else:
                    instruments = session.query(Instrument).all()

                    return self.success(data=instruments)
        except Exception as e:
            return self.error("Error retrieving instrument(s)")

    @auth_or_token
    def post(self):
        data = self.get_json()

        # lets fake the data for now
        data = {
            "name": "fake instrument",
            "type": "imager",
            "band": "Optical",
            "telescope_id": 1,
            "filters": ["ztfr", "ztfg", "ztfi"],
        }
        try:
            with self.Session() as session:
                instrument = Instrument(**data)
                session.add(instrument)
                session.commit()

                return self.success(data={"id": instrument.id})

        except Exception as e:
            print(e)
            if isinstance(e.orig, UniqueViolation):
                return self.error("An instrument with this name already exists")
            else:
                return self.error("Error adding instrument")
