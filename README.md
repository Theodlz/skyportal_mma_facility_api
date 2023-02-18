1. Install PostgreSQL 14, and configure it as in the [Skyportal documentation](https://skyportal.io/docs/setup.html#installation-debian-based-linux-and-wsl).
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip install -r requirements.txt`
5. `make run`
6. In a separate terminal, run `source env/bin/activate` and then `make log` to see the logs.
7. In your browser, go to `localhost:8080/api/demo` to upload the demo data.
8. You can now look at the logs, or the different API endpoints to get a feel for how this works.
9. Feel free to upload real data.
10. For instance, you can post real observations plans from SkyPortal by creating an allocation with altdata=`'{"protocol": "http", "host": "localhost", "port": "8080", "access_token": "1234567890"}'` on an instrument using the MMAAPI.

Thanks!
