import os
import bottle
import support


conn_pool = support.create_conn_pool()
app = bottle.Bottle()
app.install(support.DbPlugin(conn_pool))
app.install(support.AuthPlugin(conn_pool))


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
