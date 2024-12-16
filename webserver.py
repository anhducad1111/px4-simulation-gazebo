import asyncio
import random
from mavsdk import System
import KeyPressModule as kp
import paho.mqtt.client as mqtt

# Test set of manual inputs. Format: [roll, pitch, throttle, yaw]

kp.init()
drone = System()

# MQTT setup
broker = "test.mosquitto.org"
port = 1883
topic_data = "drone/position"
topic_control = "drone/control"

client = mqtt.Client()
loop = asyncio.get_event_loop()
roll, pitch, throttle, yaw = 0, 0, 0.5, 0

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_control)

def on_message(client, userdata, msg):
    global roll, pitch, throttle, yaw
    command = msg.payload.decode()
    print(f"Received control command: {command}")
    value = 0.5
    if command == "LEFT":
        pitch = -value
    elif command == "RIGHT":
        pitch = value
    elif command == "UP":
        roll = value
    elif command == "DOWN":
        roll = -value
    elif command == "w":
        throttle = 1
    elif command == "s":
        throttle = 0
    elif command == "a":
        yaw = -value
    elif command == "d":
        yaw = value
    elif command == "i":
        asyncio.run_coroutine_threadsafe(print_flight_mode(drone), loop)
    elif command == "r":
        asyncio.run_coroutine_threadsafe(arm_drone(drone), loop)
    elif command == "l":
        asyncio.run_coroutine_threadsafe(land_drone(drone), loop)
    print(f"Updated control values: roll={roll}, pitch={pitch}, throttle={throttle}, yaw={yaw}")
    asyncio.run_coroutine_threadsafe(manual_control_drone(drone), loop)

client.on_connect = on_connect
client.on_message = on_message
client.connect(broker, port, 60)
client.loop_start()

async def getKeyboardInput(my_drone):
    global roll, pitch, throttle, yaw
    while True:
        roll, pitch, throttle, yaw = 0, 0, 0.5, 0
        value = 0.5
        if kp.getKey("LEFT"):
            pitch = -value
        elif kp.getKey("RIGHT"):
            pitch = value
        if kp.getKey("UP"):
            roll = value
        elif kp.getKey("DOWN"):
            roll = -value
        if kp.getKey("w"):
            throttle = 1
        elif kp.getKey("s"):
            throttle = 0
        if kp.getKey("a"):
            yaw = -value
        elif kp.getKey("d"):
            yaw = value
        elif kp.getKey("i"):
            asyncio.ensure_future(print_flight_mode(my_drone))
        elif kp.getKey("r") and my_drone.telemetry.landed_state():
            await my_drone.action.arm()
        elif kp.getKey("l") and my_drone.telemetry.in_air():
            await my_drone.action.land()
        await asyncio.sleep(0.1)

async def print_flight_mode(my_drone):
    async for flight_mode in my_drone.telemetry.flight_mode():
        print("FlightMode:", flight_mode)

async def arm_drone(my_drone):
    if await my_drone.telemetry.landed_state():
        await my_drone.action.arm()

async def land_drone(my_drone):
    if await my_drone.telemetry.in_air():
        await my_drone.action.land()

async def manual_control_drone(my_drone):
    global roll, pitch, throttle, yaw
    counter = 0
    position_stream = my_drone.telemetry.position()
    attitude_stream = my_drone.telemetry.attitude_euler()
    
    try:
        async for position in position_stream:
            attitude = await anext(attitude_stream)
            if counter % 30 == 0:
                data = f"{position.latitude_deg:.6f},{position.longitude_deg:.6f},{position.relative_altitude_m:.2f},{attitude.roll_deg:.2f},{attitude.pitch_deg:.2f},{attitude.yaw_deg:.2f}"
                # print(data)
                client.publish(topic_data, data)
            await my_drone.manual_control.set_manual_control_input(roll, pitch, throttle, yaw)
            await asyncio.sleep(0.1)
            counter += 1
    finally:
        await position_stream.cancel()
        await attitude_stream.cancel()
        client.disconnect()

async def run_drone():
    asyncio.ensure_future(getKeyboardInput(drone))
    await drone.connect(system_address="udp://:14540")
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position state is good enough for flying.")
            break
    asyncio.ensure_future(manual_control_drone(drone))

async def run():
    global roll, pitch, throttle, yaw
    await asyncio.gather(run_drone())

if __name__ == "__main__":
    asyncio.ensure_future(run())
    client.loop_start()
    asyncio.get_event_loop().run_forever()