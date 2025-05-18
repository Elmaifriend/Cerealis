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

@socketio.on('message')
def handle_message(message):
    print("💬 Comando recibido:", type(message))
    
    if isinstance(message, str) and message == "start_demo":
        for client in clients:
            emit('message', "start_demo", room=client)
    else:
        try:
            #print(f"📸 Bytes recibidos: {len(message)}")
            # Guardar temporalmente para debug
            with open("frame.jpg", "wb") as f:
                f.write(message)

            image = Image.open(io.BytesIO(message))
            img_io = io.BytesIO()
            image.save(img_io, 'PNG')
            img_io.seek(0)

            for client in clients:
                emit('image', img_io.read(), room=client)
        except Exception as e:
            print("❌ Error mostrando imagen:", e)

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
    socketio.run(app, host='0.0.0.0', port=5000)
