from bottle import route, run, template

@route('/')
@route('/hello/<name>')
def greet(name='sta'):
    return template('hi {{name}}, how?', name = name)

run(host = 'localhost', port = 8000, debug = True)
