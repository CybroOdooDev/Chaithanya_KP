
    @http.route('/fleet_traccar/sync_now', type='json', auth='user')
    def sync_now(self, connection_id=None):
        '''
        Manually trigger sync of devices from Traccar

        URL: POST /fleet_traccar/sync_now

        Parameters:
            connection_id (optional): ID of specific connection to sync
                                    If not provided, syncs all active connections

        Returns:
            - status: 'success' or 'error'
            - message: Result message
            - count: Number of connections synced
        '''
        try:
            _logger.info('Starting sync')

            if connection_id:
                # Sync specific connection
                connection = request.env['traccar.connection'].browse(connection_id)

                if not connection.exists():
                    return {
                        'status': 'error',
                        'message': f'Connection {connection_id} not found'
                    }

                connection.sync_devices()

                return {
                    'status': 'success',
                    'message': 'Sync completed for 1 connection',
                    'count': 1
                }
            else:
                # Sync all active connections
                connections = request.env['traccar.connection'].search([
                    ('is_active', '=', True)
                ])

                for conn in connections:
                    try:
                        conn.sync_devices()
                    except Exception as e:
                        _logger.error(f'Error syncing {conn.server_url}: {str(e)}')

                return {
                    'status': 'success',
                    'message': f'Synced {len(connections)} connections',
                    'count': len(connections)
                }

        except Exception as e:
            _logger.error(f'Error in sync_now: {str(e)}')
            return {
                'status': 'error',
                'message': str(e),
                'count': 0
            }

    # ─────────────────────────────────────────────────────────────────────────────
    # ENDPOINT 3: GET DEVICE LOCATION HISTORY
    # ─────────────────────────────────────────────────────────────────────────────

    @http.route('/fleet_traccar/device/<int:device_id>/locations',
                type='json', auth='user')
    def get_device_locations(self, device_id):
        '''
        Get location history for a specific device

        URL: POST /fleet_traccar/device/<device_id>/locations

        Parameters:
            device_id: Device ID (in URL)

        Returns:
            List of locations with:
            - latitude: Latitude
            - longitude: Longitude
            - speed: Speed at this location
            - timestamp: Time of location
            - address: Address (if available)
        '''
        try:
            _logger.info(f'Getting locations for device {device_id}')

            # Search for locations
            locations = request.env['traccar.location'].search([
                ('device_id', '=', device_id)
            ], order='timestamp desc', limit=100)

            result = []

            # Process each location
            for loc in locations:
                location_dict = {
                    'latitude': loc.latitude,
                    'longitude': loc.longitude,
                    'speed': loc.speed or 0,
                    'timestamp': loc.timestamp.isoformat() if loc.timestamp else '',
                    'address': loc.address or 'Unknown',
                }
                result.append(location_dict)

            _logger.info(f'Returned {len(result)} locations for device {device_id}')
            return result

        except Exception as e:
            _logger.error(f'Error in get_device_locations: {str(e)}')
            return {
                'error': str(e),
                'message': 'Failed to get locations'
            }
"""
