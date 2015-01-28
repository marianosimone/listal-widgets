import os

from bottle import app as bottle_app
from bottle import response, request, route, template, static_file, error, run

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


@app.route('/user/:user/reading:is_json#(\.json)?#')
def make_request(user, is_json):
    items = listal.reading(user)
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
