import os
import bottle
from urllib.parse import urlparse
import psycopg2
from bottle import request

app = bottle.Bottle()


@app.hook('before_request')
def auth_hook():
    if request.auth and auth_user(*request.auth):
        request['app.user'] = request.auth[0]
    else:
        raise bottle.HTTPResponse(status=401, headers={'WWW-Authenticate': 'Basic realm="Please Login"'})


@app.get('/')
def index():
    return static('index.html')


@app.get('/<filepath:path>')
def static(filepath):
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    response = bottle.static_file(filepath, root=root)
    response.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.set_header('Pragma', 'no-cache')
    response.set_header('Expires', '0')
    return response


def auth_user(name, password):
    url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost/hrp')
    url = urlparse(url)
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        database=url.path[1:],
        user=url.username,
        password=url.password
    )
    cur = conn.cursor()
    cur.execute('select id, name, password from users where name = %s and password = %s', (name, password))
    row = cur.fetchone()
    return bool(row)


if __name__ == '__main__':
    app.run()
