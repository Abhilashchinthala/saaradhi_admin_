import asyncio
import json
import websockets

async def simulate_admin():
    uri = "ws://127.0.0.1:8000/ws/admin/dashboard/"
    try:
        async with websockets.connect(uri) as websocket:
            print("Admin Dashboard connected successfully!")
            while True:
                message = await websocket.recv()
                print(f"Admin received: {message}")
    except Exception as e:
        print(f"Admin connection error: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_admin())
