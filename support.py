import psycopg2.pool
import os
from urllib.parse import urlparse
import bottle


def create_conn_pool():
    url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/hrp')
    url = urlparse(url)
    return psycopg2.pool.ThreadedConnectionPool(1, 20, **dict(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        user=url.username,
        password=url.password
    ))


class DbPlugin(object):
    name = 'db'
    api = 2

    def __init__(self, conn_pool):
        self._conn_pool = conn_pool

    def apply(self, callback, route):
        if 'db' not in route.get_callback_args():
            return callback

        def wrapper(*args, **kwargs):
            kwargs['db'] = self._conn_pool.getconn()
            try:
                return callback(*args, **kwargs)
            finally:
                self._conn_pool.putconn(kwargs['db'])

        return wrapper


class AuthPlugin(object):
    name = 'auth'
    api = 2

    def __init__(self, conn_pool):
        self._conn_pool = conn_pool

    def apply(self, callback, route):
        if 'user' not in route.get_callback_args():
            return callback

        def wrapper(*args, **kwargs):
            auth = bottle.request.auth
            if auth and self._auth_user(*auth):
                kwargs['user'] = auth[0]
                return callback(*args, **kwargs)
            else:
                return bottle.HTTPResponse(status=401, headers={'WWW-Authenticate': 'Basic realm="Please Login"'})

        return wrapper

    def _auth_user(self, name, password):
        conn = self._conn_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute('select id, name, password from users where name = %s and password = %s', (name, password))
                row = cur.fetchone()
                return bool(row)
        finally:
            self._conn_pool.putconn(conn)
