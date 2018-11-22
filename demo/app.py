#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option gased on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()



@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my_broadcast_event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': session['usuario'] + ': ' + message['data'], 'count': session['receive_count']},
         broadcast=True)



@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': session['usuario'] + ' se ha desconectado!', 'count': session['receive_count']}, broadcast=True)
    disconnect()

@socketio.on('connect', namespace='/test')
def test_connect():
    print("Cliente conectado")
    session['usuario'] = 'Sin nombre'
    emit('my_response', {'data': 'Conectado', 'count': 0})

@socketio.on('my_user', namespace='/test')
def connect_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    session['usuario'] = message['data']
    print(message)
    emit('my_response',
         {'data': (session['usuario'] + ' se ha conectado'), 'count': session['receive_count']}, broadcast=True)



@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app, debug=True)
