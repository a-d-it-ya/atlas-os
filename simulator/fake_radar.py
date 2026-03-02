import asyncio
import json
import math
import random
import websockets

# Simulated border sector — Depsang Plains, Ladakh
SECTOR_CENTER = {"lat": 34.1526, "lon": 77.5771}

class SimulatedObject:
    def __init__(self):
        # Start north of the post, random position
        self.lat = SECTOR_CENTER["lat"] + random.uniform(0.01, 0.05)
        self.lon = SECTOR_CENTER["lon"] + random.uniform(-0.02, 0.02)

        # Moving slowly southward (toward the post)
        self.speed_lat = -random.uniform(0.0001, 0.0003)
        self.speed_lon =  random.uniform(-0.00005, 0.00005)

        # What kind of object — radar can't tell, so all UNKNOWN
        self.object_type = random.choice([
            "HUMAN", "HUMAN", "HUMAN",
            "ANIMAL",
            "VEHICLE"
        ])

    def update(self):
        self.lat += self.speed_lat
        self.lon += self.speed_lon

    def to_packet(self):
        dlat = self.lat - SECTOR_CENTER["lat"]
        dlon = self.lon - SECTOR_CENTER["lon"]
        range_m   = math.sqrt(dlat**2 + dlon**2) * 111000
        azimuth   = math.degrees(math.atan2(dlon, dlat))
        velocity  = self.speed_lat * 111000 / 0.5  # m/s

        return {
            "range_m":  round(range_m, 1),
            "azimuth":  round(azimuth, 1),
            "velocity": round(velocity, 2),
            "raw_lat":  round(self.lat, 6),
            "raw_lon":  round(self.lon, 6),
        }

# 3 objects moving across the sector
objects = [SimulatedObject() for _ in range(3)]

async def stream_radar(websocket):
    print("[RADAR] Client connected")
    try:
        while True:
            for obj in objects:
                obj.update()
                packet = obj.to_packet()
                await websocket.send(json.dumps(packet))
                print(f"[RADAR] Sent → range:{packet['range_m']}m  az:{packet['azimuth']}°  vel:{packet['velocity']}m/s")
            await asyncio.sleep(0.5)
    except websockets.exceptions.ConnectionClosed:
        print("[RADAR] Client disconnected")

async def main():
    print("[RADAR] Fake radar starting on ws://localhost:5005")
    async with websockets.serve(stream_radar, "localhost", 5005):
        await asyncio.Future()  # run forever

asyncio.run(main())