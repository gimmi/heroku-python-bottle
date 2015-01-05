import decimal
import os
import bottle
import support
from bottle import request
import uuid
from datetime import date
import isodate
from decimal import Decimal
import itertools
import urllib.parse

conn_pool = support.create_conn_pool()
app = bottle.Bottle()
app.install(support.DbPlugin(conn_pool))
app.install(support.AuthPlugin(conn_pool))


@app.get('/')
def index(user):
    return static('index.html')


@app.get('/<filepath:path>')
def static(filepath, user):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    response = bottle.static_file(filepath, root=root)
    response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.set_header('Pragma', 'no-cache')
    response.set_header('Expires', '0')
    return response


@app.get('/api/expenses/<expense_id>')
def get_expense(user, db, expense_id):
    with db.cursor() as cur:
        cur.execute('SELECT * FROM expenses WHERE id = %s', [expense_id])
        row = cur.fetchone()
        if not row:
            return bottle.HTTPResponse(status=404)
        return expense_row_to_json(row)


@app.get('/api/expenses')
def get_expenses(user, db):
    return build_paginated_result(db, 'SELECT * FROM expenses ORDER BY date', dict(), expense_row_to_json)


@app.post('/api/expenses')
def add_expense(user, db):
    json = request.json
    params = dict(
        id=json.get('id') or str(uuid.uuid4()),
        date=isodate.parse_date(json.get('date') or isodate.date_isoformat(date.today())),
        gimmi_amount=Decimal(json.get('gimmiAmount') or 0),
        elena_amount=Decimal(json.get('elenaAmount') or 0),
        gimmi_debt=Decimal(json.get('gimmiDebt') or 0),
        elena_debt=Decimal(json.get('elenaDebt') or 0),
        description=json.get('description') or None,
        tags=json.get('tags') or None
    )
    with db.cursor() as cur:
        cur.execute('SELECT id FROM expenses WHERE id = %(id)s', params)
        if cur.fetchone():
            cur.execute("""
            UPDATE expenses SET
              id = %(id)s,
              date = %(date)s,
              gimmi_amount = %(gimmi_amount)s,
              elena_amount = %(elena_amount)s,
              gimmi_debt = %(gimmi_debt)s,
              elena_debt = %(elena_debt)s,
              description = %(description)s,
              tags = %(tags)s
            """, params)
        else:
            cur.execute("""
            INSERT INTO expenses(id, date, gimmi_amount, elena_amount, gimmi_debt, elena_debt, description, tags)
            VALUES(%(id)s, %(date)s, %(gimmi_amount)s, %(elena_amount)s, %(gimmi_debt)s, %(elena_debt)s, %(description)s, %(tags)s)
            """, params)

    db.commit()

    return get_expense(user, db, params['id'])


def expense_row_to_json(row):
    return dict(
        id=str(row['id']),
        date=isodate.date_isoformat(row['date']),
        gimmiAmount=float(row['gimmi_amount']),
        elenaAmount=float(row['elena_amount']),
        gimmiDebt=float(row['gimmi_debt']),
        elenaDebt=float(row['elena_debt']),
        description=row['description'],
        tags=row['tags']
    )


def build_paginated_result(db, sql, params, row_transform_fn):
    params.update(dict(
        skip=int(request.query.get('skip', '0')),
        page_size=int(request.query.get('page_size', '10'))
    ))
    with db.cursor() as cur:
        cur.execute(sql + ' LIMIT %(page_size)s + 1 OFFSET %(skip)s', params)
        ret = dict(
            items=list(map(row_transform_fn, itertools.islice(cur, params['page_size'])))
        )
        if cur.rowcount > params['page_size']:
            ret['next'] = get_updated_utl(request.url, dict(skip=params['skip'] + params['page_size']))
        if params['skip'] > 0:
            ret['prev'] = get_updated_utl(request.url, dict(skip=max(params['skip'] - params['page_size'], 0)))
        return ret


def get_updated_utl(url, params):
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qs(url_parts[4]))
    query.update(params)

    url_parts[4] = urllib.parse.urlencode(query, doseq=True)

    return urllib.parse.urlunparse(url_parts)


if __name__ == '__main__':
    app.run()
