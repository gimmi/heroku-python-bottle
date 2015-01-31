import psycopg2.pool
import psycopg2.extras
import os
from urllib.parse import urlparse
import bottle
from bottle import response
import logging
import json
from decimal import Decimal
from datetime import date
import isodate


def create_conn_pool():
    url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/hrp')
    url = urlparse(url)
    return psycopg2.pool.ThreadedConnectionPool(1, 20, **dict(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        cursor_factory=psycopg2.extras.RealDictCursor
    ))


def init_logging():
    fmt = logging.Formatter(logging.BASIC_FORMAT, None)

    shdlr = logging.StreamHandler()
    shdlr.setFormatter(fmt)
    shdlr.setLevel(logging.DEBUG)
    logging.root.addHandler(shdlr)

    logging.root.setLevel(logging.DEBUG)


def import_from_xl(file_path):
    import uuid, xlrd

    processed_rows = 0
    imported_rows = 0

    wb = xlrd.open_workbook(file_path)
    ws = wb.sheet_by_index(0)

    pool = create_conn_pool()
    db = pool.getconn()

    with db.cursor() as cur:
        for rowx in range(1, ws.nrows):
            expense_date = date(*xlrd.xldate_as_tuple(ws.cell(rowx, 0).value, wb.datemode)[:3])
            amount = Decimal(ws.cell(rowx, 1).value)
            gimmi_debt = Decimal(ws.cell(rowx, 2).value or 0)
            elena_debt = Decimal(ws.cell(rowx, 3).value or 0)
            description = ws.cell(rowx, 4).value
            category = ws.cell(rowx, 5).value

            cur.execute("SELECT 1 FROM expenses WHERE description LIKE concat('%%#xl', %s)", [rowx])
            if not cur.fetchone():
                cur.execute("""
                        INSERT INTO expenses(id, date, due_month, month_spread, gimmi_amount, elena_amount, gimmi_debt, elena_debt, description, category_id)
                        VALUES(%(id)s, %(date)s, %(due_month)s, %(month_spread)s, %(gimmi_amount)s, %(elena_amount)s, %(gimmi_debt)s, %(elena_debt)s, %(description)s, %(category_id)s)
                    """, dict(
                    id=str(uuid.uuid4()),
                    date=expense_date,
                    due_month=date(expense_date.year, expense_date.month, 1),
                    month_spread=1,
                    gimmi_amount=amount if elena_debt else Decimal(0),
                    elena_amount=amount if gimmi_debt else Decimal(0),
                    gimmi_debt=gimmi_debt,
                    elena_debt=elena_debt,
                    description=description + ' #xl' + str(rowx),
                    category_id='e6a55731-bfb3-4c07-a69a-34134428e409'
                ))
                imported_rows += 1
            processed_rows += 1

    db.commit()
    pool.putconn(db)
    print('%s rows processed, %s imported' % (processed_rows, imported_rows))


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


class JSONPlugin(object):
    name = 'json'
    api = 2

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            try:
                ret = callback(*args, **kwargs)
            except bottle.HTTPError as err:
                ret = err

            if isinstance(ret, dict) or isinstance(ret, list):
                response.content_type = 'application/json'
                return json.dumps(ret, default=self.custom_serialize)
            elif isinstance(ret, bottle.HTTPResponse) and (isinstance(ret.body, dict) or isinstance(ret.body, list)):
                ret.content_type = 'application/json'
                ret.body = json.dumps(ret, default=self.custom_serialize)
            return ret

        return wrapper

    @staticmethod
    def custom_serialize(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return isodate.date_isoformat(obj)
        raise TypeError

if __name__ == '__main__':
    file_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'Spese.xlsx')
    print('Importing from %s...' % file_path)
    import_from_xl(file_path)