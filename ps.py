from mavsdk import System
from math import cos, radians
import asyncio
import time

# Chuyển đổi tọa độ ENU sang GPS
def enu_to_gps(lat_origin, lon_origin, alt_origin, x, y, z):
    delta_lat = y / 111111
    delta_lon = x / (111111 * cos(radians(lat_origin)))
    return lat_origin + delta_lat, lon_origin + delta_lon, alt_origin + z

class SinglePointMission:
    def __init__(self):
        self.drone = System()

    async def connect(self):
        await self.drone.connect(system_address="udp://:14540")
        print("Waiting for drone connection...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print("Drone connected!")
                break

    async def set_maximum_speed(self, speed):
        await self.drone.action.set_maximum_speed(speed)
        print(f"Maximum speed set to {speed} m/s")

    async def fly_to_point(self, x, y, altitude, roll, pitch, yaw, speed):
        lat_origin, lon_origin, alt_origin = 15.976415520094767, 108.25092250516339, 0
        lat, lon, alt = enu_to_gps(lat_origin, lon_origin, alt_origin, x, y, altitude)

        print(f"Flying to point: ({lat}, {lon}, {alt})")
        print(f"Orientation: Roll={roll}°, Pitch={pitch}°, Yaw={yaw}°")

        await self.set_maximum_speed(speed)
        await self.drone.action.goto_location(lat, lon, alt, yaw)

        # Modified position monitoring loop
        while True:
            async for position in self.drone.telemetry.position():
                current_lat = position.latitude_deg
                current_lon = position.longitude_deg
                current_alt = position.absolute_altitude_m

                if abs(current_lat - lat) < 0.00001 and abs(current_lon - lon) < 0.00001 and abs(current_alt - alt) < 1:
                    print("Reached waypoint.")
                    return
                
                # Only check position once per second
                await asyncio.sleep(1)
                break  # Break the inner loop to get fresh position updates

    async def execute_path(self, waypoints, speed):
        for waypoint in waypoints:
            x, y, z, roll, pitch, yaw = waypoint
            await self.fly_to_point(x, y, z, roll, pitch, yaw, speed)
        print("Returning to start position...")
        await self.fly_to_point(-30, -30, 4, 0, 0, 0.9, speed)

def main():
    mission = SinglePointMission()

    waypoints = [
        (25, -25, 4, 0, 0, 0),
        (25, 45, 4, 0, 0, 0),
        (5, 45, 4, 0, 0, -90),
        (5, 45, 4, 0, 0, -180),
        (5, 45, 4, 0, 0, -90),
        (5, -25, 4, 0, 0, -180)
    ]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(mission.connect())
    loop.run_until_complete(mission.execute_path(waypoints, speed=3))  # Set speed here

if __name__ == "__main__":
    main()