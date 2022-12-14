from contextlib import contextmanager
import tornado
from tornado.web import RequestHandler
from skyportal_mma_facility.models import VerifiedSession, DBSession, session_context_id

import uuid
import time
from json.decoder import JSONDecodeError
from skyportal_mma_facility.utils.env import load_env
from skyportal_mma_facility.utils.json_util import to_json

env, cfg = load_env()


class NoValue:
    pass


class BaseHandler(RequestHandler):
    @contextmanager
    def Session(self):
        """
        Generate a scoped session that also has knowledge
        of the current user, so when commit() is called on it
        it will also verify that all rows being committed
        are accessible to the user.
        The current user is taken from the handler's `current_user`.
        This is a shortcut method to `models.Session`
        that saves the need to manually input the user object.

        Parameters
        ----------
        verify : boolean
            if True (default), will call the functions
            `verify()` and whenever `commit()` is called.

        Returns
        -------
        A scoped session object that can be used in a context
        manager to access the database. If auto verify is enabled,
        will use the current user given to apply verification
        before every commit.

        """
        with VerifiedSession() as session:
            # must merge the user object with the current session
            # ref: https://docs.sqlalchemy.org/en/14/orm/session_basics.html#adding-new-or-existing-items
            # session.add(self.current_user) # TODO: reimplement when adding user concepts
            yield session

    def on_finish(self):
        DBSession.remove()

    def prepare(self):
        self.cfg = self.application.cfg
        # self.flow = Flow()
        session_context_id.set(uuid.uuid4().hex)

        # Remove slash prefixes from arguments
        if self.path_args:
            self.path_args = [
                arg.lstrip("/") if arg is not None else None for arg in self.path_args
            ]
            self.path_args = [arg if (arg != "") else None for arg in self.path_args]

        # If there are no arguments, make it explicit, otherwise
        # get / post / put / delete all have to accept an optional kwd argument
        if len(self.path_args) == 1 and self.path_args[0] is None:
            self.path_args = []

        # TODO Refactor to be a context manager or utility function
        N = 5
        for i in range(1, N + 1):
            try:
                assert DBSession.session_factory.kw["bind"] is not None
            except Exception as e:
                if i == N:
                    raise e
                else:
                    print("Error connecting to database, sleeping for a while")
                    time.sleep(5)

        return super().prepare()

    def verify_and_commit(self):
        DBSession().commit()

    def get_json(self):
        if len(self.request.body) == 0:
            return {}
        try:
            json = tornado.escape.json_decode(self.request.body)
            if not isinstance(json, dict):
                raise Exception("Please ensure posted data is of type application/json")
            return json
        except JSONDecodeError:
            raise Exception(
                f"JSON decode of request body failed on {self.request.uri}."
                " Please ensure all requests are of type application/json."
            )

    def error(self, message, data={}, status=400, extra={}):
        """Push an error message to the frontend via WebSocket connection.

        The return JSON has the following format::

          {
            "status": "error",
            "data": ...,
            ...extra...
          }

        Parameters
        ----------
        message : str
            Description of the error.
        data : dict, optional
            Any data to be included with error message.
        status : int, optional
            HTTP status code.  Defaults to 400 (bad request).
            See https://www.restapitutorial.com/httpstatuscodes.html for a full
            list.
        extra : dict
            Extra fields to be included in the response.
        """
        self.set_header("Content-Type", "application/json")
        self.set_status(status)
        self.write({"status": "error", "message": message, "data": data, **extra})

    def success(self, data={}, action=None, payload={}, status=200, extra={}):
        """Write data and send actions on API success.

        The return JSON has the following format::

          {
            "status": "success",
            "data": ...,
            ...extra...
          }

        Parameters
        ----------
        data : dict, optional
            The JSON returned by the API call in the `data` field.
        action : str, optional
            Name of frontend action to perform after API success.  This action
            is sent to the frontend over WebSocket.
        payload : dict, optional
            Action payload.  This data accompanies the action string
            to the frontend.
        status : int, optional
            HTTP status code.  Defaults to 200 (OK).
            See https://www.restapitutorial.com/httpstatuscodes.html for a full
            list.
        extra : dict
            Extra fields to be included in the response.
        """
        if action is not None:
            self.action(action, payload)

        self.set_header("Content-Type", "application/json")
        self.set_status(status)
        self.write(to_json({"status": "success", "data": data, **extra}))

    def get_query_argument(self, value, default=NoValue, **kwargs):
        if default != NoValue:
            kwargs["default"] = default
        arg = super().get_query_argument(value, **kwargs)
        if type(kwargs.get("default", None)) == bool:
            arg = str(arg).lower() in ["true", "yes", "t", "1"]
        return arg
