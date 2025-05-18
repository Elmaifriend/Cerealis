import socketio
import cv2
import asyncio
from dronekit import connect, VehicleMode, LocationGlobalRelative

# Conexión a la Pixhawk
connection_string = 'COM6'  # Cambia a '/dev/ttyAMA0' o UDP si estás en Linux
vehicle = connect(connection_string, wait_ready=True)
vehicle.parameters['ARMING_CHECK'] = 0

sio = socketio.Client()

@sio.event
def connect():
    print("✅ Conectado al servidor Flask WebSocket.")

@sio.event
def disconnect():
    print("❌ Desconectado del servidor Flask WebSocket.")

@sio.event
def message(data):
    print(f"📩 Mensaje recibido: {data}")
    if data == "start_demo":
        asyncio.run(start_demo())

@sio.on('drone_command')
def handle_remote_drone_command(data):
    action = data.get('action')
    state = data.get('state')

    if state == 'start':
        print(f"🟢 Iniciar {action}")
    elif state == 'stop':
        # Detener movimiento
        print(f"🔴 Detener {action}")
        # Aquí detienes los motores

async def send_camera_frames():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cámara no detectada.")
        return
    
    print("📷 Cámara activada. Enviando frames...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Error al capturar frame.")
            break

        _, jpeg = cv2.imencode('.jpg', frame)
        frame_data = jpeg.tobytes()
        sio.emit('message', frame_data)
        await asyncio.sleep(0.1)

async def start_demo():
    print("🚁 Iniciando vuelo de demostración...")
    vehicle.mode = VehicleMode("STABILIZE")
    vehicle.armed = True

    while not vehicle.armed:
        print("⏳ Esperando armado...")
        await asyncio.sleep(1)

    print("🛫 Subiendo...")
    vehicle.simple_takeoff(10)

    while vehicle.location.global_relative_frame.alt < 9:
        print(f"Altura actual: {vehicle.location.global_relative_frame.alt} m")
        await asyncio.sleep(1)

    print("➡️ Moviendo hacia adelante...")
    vehicle.simple_goto(LocationGlobalRelative(
        vehicle.location.global_relative_frame.lat + 0.0001,
        vehicle.location.global_relative_frame.lon,
        vehicle.location.global_relative_frame.alt
    ))
    await asyncio.sleep(5)

    print("🛬 Aterrizando...")
    vehicle.mode = VehicleMode("LAND")
    await asyncio.sleep(5)
    vehicle.armed = False
    print("✅ Vuelo de demostración completado.")

def main():
    sio.connect('http://localhost:5000')  # Cambia la IP si usas red local
    asyncio.run(send_camera_frames())

if __name__ == "__main__":
    main()
