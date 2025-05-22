from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import io
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", ping_interval=25, ping_timeout=10)

clients = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@socketio.on('message')
def handle_message(message):
    if isinstance(message, str) and message == "start_demo":
        for client in clients:
            emit('message', "start_demo", room=client)
    else:
        try:
            for client in clients:
                emit('image', message, room=client)
        except Exception as e:
            print("❌ Error mostrando imagen:", e)

@socketio.on('drone_command')
def handle_drone_command(data):
    action = data.get('action')
    state = data.get('state')  # 'start' o 'stop'
    print(f"🛸 Comando de dron: {action} - {state}")

    for client in clients:
        emit('drone_command', data, room=client)

@socketio.on('connect')
def handle_connect():
    print(f"📡 Cliente WebSocket conectado: {request.sid}")
    clients.append(request.sid)
    print("Clientes activos:", clients)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Cliente WebSocket desconectado: {request.sid}")
    if request.sid in clients:
        clients.remove(request.sid)

if __name__ == "__main__":
    print("🚀 Servidor Flask WebSocket corriendo en ws://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True)
