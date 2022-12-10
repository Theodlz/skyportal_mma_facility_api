import functools
import tornado
def auth_or_token(method):
    """Ensure that a user is signed in.

    This is a decorator for Tornado handler `get`, `put`, etc. methods.

    Signing in happens via the login page, or by using an auth token.
    To use an auth token, the `Authorization` header has to be
    provided, and has to be of the form `token 123efghj`.  E.g.:

      $ curl -v -H "Authorization: token 123efghj" http://localhost:5000/api/endpoint

    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        token_header = self.request.headers.get("Authorization", None)
        if token_header is not None and token_header.startswith("token "):
            token = token_header.replace("token", "").strip()

            #### TODO: verify if token is correct in your database
            
            if token is not None:
                self.current_user = token
                if token not in ["123"]: # fake list of tokens
                    raise tornado.web.HTTPError(401)
            else:
                raise tornado.web.HTTPError(401)
            return method(self, *args, **kwargs)
        else:
            raise tornado.web.HTTPError(401)

    return wrapper