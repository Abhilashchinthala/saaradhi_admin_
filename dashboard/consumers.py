import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode('utf-8')
        try:
            self.driver_id = query_string.split('token=')[1].split('&')[0]
        except (IndexError, ValueError):
            self.driver_id = "unknown"
            
        self.group_name = 'drivers'

        # Join drivers group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Driver {self.driver_id} connected'
        }))

    async def disconnect(self, close_code):
        # Leave drivers group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        lat = data.get('lat')
        lng = data.get('lng')

        # Broadcast location to the drivers group (which Admin God View will listen to)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'driver_location_update',
                'driver_id': self.driver_id,
                'lat': lat,
                'lng': lng
            }
        )

    async def driver_location_update(self, event):
        await self.send(text_data=json.dumps(event))


class AdminDashboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for the Admin Dashboard to receive real-time updates.
    """
    async def connect(self):
        self.group_name = 'admin_dashboard'
        
        # Join groups to listen for everything
        await self.channel_layer.group_add('drivers', self.channel_name)
        await self.channel_layer.group_add('trips', self.channel_name)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('drivers', self.channel_name)
        await self.channel_layer.group_discard('trips', self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def driver_location_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def trip_status_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def ride_request(self, event):
        await self.send(text_data=json.dumps(event))


class RideRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle ride request logic...
        # For now, just broadcast to admin
        await self.channel_layer.group_send(
            'admin_dashboard',
            {
                'type': 'ride_request',
                'data': data
            }
        )


class TripStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.trip_id = self.scope['url_route']['kwargs']['trip_id']
        self.group_name = f'trip_{self.trip_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.channel_layer.group_add('trips', self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard('trips', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle trip status transitions...
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'trip_status_update',
                'trip_id': self.trip_id,
                'data': data
            }
        )
        # Also notify admin
        await self.channel_layer.group_send(
            'trips',
            {
                'type': 'trip_status_update',
                'trip_id': self.trip_id,
                'data': data
            }
        )

    async def trip_status_update(self, event):
        await self.send(text_data=json.dumps(event))
