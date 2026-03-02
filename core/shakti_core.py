import asyncio
import json
import uuid
import websockets
from datetime import datetime

TOWER_CONFIG = {
    "tower_id": "TOWER_01_DEPSANG",
    "lat":      34.1526,
    "lon":      77.5771,
}

# All connected operator map screens
connected_operators = set()

def create_entity(packet):
    """Convert a raw radar packet into a Shakti Entity."""
    return {
        "entity_id":   str(uuid.uuid4()),
        "entity_type": "TRACK",
        "location": {
            "navic_lat":    packet["raw_lat"],
            "navic_lon":    packet["raw_lon"],
            "uncertainty_m": 15.0
        },
        "classification": {
            "category":   "UNKNOWN",
            "confidence": 0.6,
            "sensors":    ["RADAR"]
        },
        "disposition": "HOSTILE",
        "kinematics": {
            "speed_kmh": round(abs(packet["velocity"]) * 3.6, 1),
            "is_moving": abs(packet["velocity"]) > 0.3
        },
        "provenance": {
            "source_tower":  TOWER_CONFIG["tower_id"],
            "source_sensor": "RADAR_SIM_01",
            "detected_at":   int(datetime.now().timestamp() * 1000),
            "algorithm_ver": "v0.1.0"
        }
    }

async def receive_from_radar():
    """Connect to radar stream and forward entities to operators."""
    print("[CORE] Connecting to radar on ws://localhost:5005 ...")
    async with websockets.connect("ws://localhost:5005") as radar_ws:
        print("[CORE] Radar connected. Waiting for detections...")
        async for message in radar_ws:
            packet = json.loads(message)
            entity = create_entity(packet)

            print(f"[CORE] Entity created → {entity['entity_id'][:8]}  "
                  f"lat:{entity['location']['navic_lat']}  "
                  f"lon:{entity['location']['navic_lon']}  "
                  f"moving:{entity['kinematics']['is_moving']}")

            # Broadcast to all connected operator screens
            if connected_operators:
                await asyncio.gather(*[
                    op.send(json.dumps(entity))
                    for op in connected_operators
                ])

async def operator_handler(websocket):
    """Handle a connected C2 map screen."""
    connected_operators.add(websocket)
    print(f"[CORE] Operator connected. Total screens: {len(connected_operators)}")
    try:
        await websocket.wait_closed()
    finally:
        connected_operators.remove(websocket)
        print(f"[CORE] Operator disconnected. Total screens: {len(connected_operators)}")

async def main():
    print("[CORE] Shakti OS v0.1 starting...")
    print("[CORE] C2 WebSocket on ws://localhost:8000")

    async with websockets.serve(operator_handler, "localhost", 8000):
        await receive_from_radar()

asyncio.run(main())