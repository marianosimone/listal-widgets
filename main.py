import os

from bottle import route, template, static_file, error, run

import listal


@route('/')
def handle_root_url():
    return static_file('index.html', root='views')


@route('/user/:user/reading:is_json#(\.json)?#')
def make_request(user, is_json):
    items = listal.reading(user)
    if is_json:
        return {'items': items}
    return template('items.tpl', items=items)


@error(404)
def error404(error):
    return template('error', error_msg='404 error. Nothing to see here')


if os.environ.get('APP_LOCATION') == 'heroku':
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=8080, debug=True, reloader=True)
