import os
import bottle
from bottle import request

app = bottle.Bottle()


@app.hook('before_request')
def auth_hook():
    if request.auth == ('gimmi', 'secret'):
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


if __name__ == '__main__':
    app.run()
