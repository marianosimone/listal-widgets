import os

from bottle import app as bottle_app
from bottle import abort, response, request, template, static_file, run

import listal


class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

app = bottle_app()
app.install(EnableCors())

@app.route('/')
def handle_root_url():
    return static_file('index.html', root='views')

ACTIONS = {
    'reading': listal.reading,
    'read': listal.read
}

@app.route('/user/<user>/<action:re:[\w]+><is_json:re:(\.json)?>')
def serve(user, action, is_json):
    if action in ACTIONS:
        items = ACTIONS[action](user)
        if is_json:
            return {'items': items}
        return template('items.tpl', items=items)
    abort(404)

@app.route('/list/<name:re:[\w-]+><is_json:re:(\.json)?>')
def list_details(name, is_json):
    items = listal.list_details(name)
    if is_json:
        return {'items': items}
    return template('items.tpl', items=items)

@app.error(404)
def error404(error):
    return template('error', error_msg='404 error. Nothing to see here')

if os.environ.get('APP_LOCATION') == 'heroku':
    run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(app, host='localhost', port=8080, debug=True, reloader=True)
