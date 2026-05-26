import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from dashboard.models import Driver

@database_sync_to_async
def get_driver_id_from_token(token):
    if not token:
        return None
    # For simulation support: "dummy_token_<driver_id>"
    if token.startswith("dummy_token_"):
        driver_id_str = token.replace("dummy_token_", "")
        try:
            driver_id = int(driver_id_str)
            if Driver.objects.filter(id=driver_id).exists():
                return str(driver_id)
        except ValueError:
            pass
    # Otherwise check if it's a numeric driver id directly
    try:
        driver_id = int(token)
        if Driver.objects.filter(id=driver_id).exists():
            return str(driver_id)
    except ValueError:
        pass
    return None

class DriverLocationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        token = None
        if 'token=' in query_string:
            try:
                token = query_string.split('token=')[1].split('&')[0]
            except IndexError:
                pass
                
        self.driver_id = await get_driver_id_from_token(token)
        if not self.driver_id:
            # Reject connection if not authenticated
            await self.close()
            return
            
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
        if hasattr(self, 'group_name'):
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
        user = self.scope.get('user')
        if not user or not user.is_authenticated or not user.is_staff:
            # Close connection for unauthenticated or non-staff users
            await self.close()
            return

        self.group_name = 'admin_dashboard'
        
        # Join groups to listen for everything
        await self.channel_layer.group_add('drivers', self.channel_name)
        await self.channel_layer.group_add('trips', self.channel_name)
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
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
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        token = None
        if 'token=' in query_string:
            try:
                token = query_string.split('token=')[1].split('&')[0]
            except IndexError:
                pass
                
        user = self.scope.get('user')
        driver_id = await get_driver_id_from_token(token) if token else None
        
        # Allow connection if user is authenticated OR is a valid driver
        if not ((user and user.is_authenticated) or driver_id):
            await self.close()
            return

        # Join the ride_requests group
        self.group_name = 'ride_requests'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Handle ride request logic...
        # Broadcast to admin_dashboard group
        await self.channel_layer.group_send(
            'admin_dashboard',
            {
                'type': 'ride_request',
                'data': data
            }
        )
        
    async def ride_request(self, event):
        await self.send(text_data=json.dumps(event))


class TripStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        token = None
        if 'token=' in query_string:
            try:
                token = query_string.split('token=')[1].split('&')[0]
            except IndexError:
                pass
                
        user = self.scope.get('user')
        driver_id = await get_driver_id_from_token(token) if token else None
        
        # Allow connection if user is authenticated OR is a valid driver
        if not ((user and user.is_authenticated) or driver_id):
            await self.close()
            return

        self.trip_id = self.scope['url_route']['kwargs']['trip_id']
        self.group_name = f'trip_{self.trip_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.channel_layer.group_add('trips', self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
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
