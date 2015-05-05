from bottle import route, run, template, static_file

@route('/')
def index():
    return template('index')

#todo: add static to fonts, etc.
@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root = 'static')

run(host = 'localhost', port = 8000, debug = True)
