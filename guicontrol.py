from mavsdk import System
from math import cos, radians
import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading

# Chuyển đổi tọa độ ENU sang GPS
def enu_to_gps(lat_origin, lon_origin, alt_origin, x, y, z):
    delta_lat = y / 111111
    delta_lon = x / (111111 * cos(radians(lat_origin)))
    return lat_origin + delta_lat, lon_origin + delta_lon, alt_origin + z

class DroneGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Control")
        self.mission = SinglePointMission()
        self.loop = asyncio.new_event_loop()
        
        # Tạo các thành phần GUI
        self._create_widgets()
        
        # Chạy asyncio loop trong một luồng riêng
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()

    def _create_widgets(self):
        # Tạo các ô nhập liệu và nhãn
        fields = [
            ("X Coordinate (m):", 0),
            ("Y Coordinate (m):", 1),
            ("Altitude (m):", 2),
            ("Roll (\u00b0):", 3),
            ("Pitch (\u00b0):", 4),
            ("Yaw (\u00b0):", 5)
        ]
        self.entries = {}

        for label, row in fields:
            ttk.Label(self.root, text=label).grid(row=row, column=0, padx=5, pady=5)
            entry = ttk.Entry(self.root)
            entry.grid(row=row, column=1, padx=5, pady=5)
            self.entries[label] = entry

        # Nút bấm và nhãn trạng thái
        self.connect_button = ttk.Button(self.root, text="Connect Drone", command=self.connect_drone)
        self.connect_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.fly_button = ttk.Button(self.root, text="Fly to Point", command=self.fly_to_point, state='disabled')
        self.fly_button.grid(row=7, column=0, columnspan=2, pady=5)

        self.status_label = ttk.Label(self.root, text="Status: Not Connected")
        self.status_label.grid(row=8, column=0, columnspan=2, pady=5)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def connect_drone(self):
        asyncio.run_coroutine_threadsafe(self._connect(), self.loop)

    def fly_to_point(self):
        try:
            # Lấy dữ liệu từ ô nhập liệu
            x = float(self.entries["X Coordinate (m):"].get())
            y = float(self.entries["Y Coordinate (m):"].get())
            alt = float(self.entries["Altitude (m):"].get())
            roll = float(self.entries["Roll (\u00b0):"].get())
            pitch = float(self.entries["Pitch (\u00b0):"].get())
            yaw = float(self.entries["Yaw (\u00b0):"].get())

            asyncio.run_coroutine_threadsafe(
                self.mission.fly_to_point(x, y, alt, roll, pitch, yaw), 
                self.loop
            )
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")

    async def _connect(self):
        try:
            await self.mission.connect()
            self.root.after(0, lambda: self.status_label.config(text="Status: Connected"))
            self.root.after(0, lambda: self.fly_button.config(state='normal'))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Connection failed: {str(e)}"))

    def __del__(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.loop_thread.join()

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

    async def fly_to_point(self, x, y, altitude, roll, pitch, yaw):
        lat_origin, lon_origin, alt_origin = 15.976415520094767, 108.25092250516339, 0
        lat, lon, alt = enu_to_gps(lat_origin, lon_origin, alt_origin, x, y, altitude)

        print(f"Flying to point: ({lat}, {lon}, {alt})")
        print(f"Orientation: Roll={roll}°, Pitch={pitch}°, Yaw={yaw}°")

        await self.drone.action.goto_location(lat, lon, alt, yaw)

def main():
    root = tk.Tk()
    app = DroneGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
