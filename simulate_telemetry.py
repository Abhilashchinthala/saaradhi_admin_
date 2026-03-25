import asyncio
import json
import websockets
import random
import time

async def simulate_driver(driver_id):
    uri = f"ws://127.0.0.1:8000/ws/driver/location/?token=dummy_token_{driver_id}"
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Driver {driver_id} connected")
            
            # Initial position
            lat = 17.3 + (random.random() * 0.1)
            lng = 78.4 + (random.random() * 0.1)
            
            while True:
                # Move slightly
                lat += (random.random() - 0.5) * 0.001
                lng += (random.random() - 0.5) * 0.001
                
                payload = {
                    "lat": lat,
                    "lng": lng
                }
                await websocket.send(json.dumps(payload))
                # print(f"Driver {driver_id} sent location: {lat}, {lng}")
                
                await asyncio.sleep(2)
    except Exception as e:
        print(f"Driver {driver_id} error: {e}")

async def main():
    # Simulate 5 drivers
    print("DEBUG: Starting 5 simulation tasks...")
    tasks = [simulate_driver(i) for i in range(1, 6)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("Starting driver telemetry simulation...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Simulation stopped.")
    except Exception as e:
        print(f"DEBUG: Simulation crash: {e}")
