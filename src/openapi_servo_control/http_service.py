'''This module contains http server class'''
import logging
import os

from aiohttp import web
import aiohttp_cors
from aiohttp_swagger import setup_swagger

from .axis_container import AxisContainer, Axis


logger = logging.getLogger(__name__)

STATIC_FOLDER = '/var/www/html/'


class HttpService:
    '''
    ---
    Creates http server. Process unconditional redirects to the secure
    server
    '''

    def __init__(self, axis_container: AxisContainer):
        self.app = web.Application()
        self.runner = None
        self.axis_container = axis_container
        self.app.router.add_route(
            'POST',
            r'/api/servo/{axis:\d+}/position/{position:-?\d+}',
            self.set_position,
        )
        self.app.router.add_route(
            'POST',
            r'/api/servo/{axis:\d+}/velocity/{velocity:-?\d+}',
            self.set_velocity,
        )
        self.app.router.add_route(
            'POST',
            r'/api/servo/{axis:\d+}/speed/{speed:-?\d+}',
            self.set_speed,
        )
        self.app.router.add_route(
            'GET',
            r'/api/servo/{axis:\d+}/speed',
            self.get_speed,
        )
        self.app.router.add_route(
            'POST',
            r'/api/servo/{axis:\d+}/tilt',
            self.set_tilt,
        )
        self.app.router.add_route(
            'POST',
            r'/api/servo/{axis:\d+}/tilt/{angle:\d+}',
            self.set_tilt,
        )
        self.app.router.add_route(
            'POST',
            r'/api/servo/{axis:\d+}/swing',
            self.set_swing,
        )
        self.app.router.add_route(
            'GET',
            r'/api/servo/{axis:\d+}/status',
            self.get_axis_status,
        )
        self.app.router.add_route(
            'GET',
            '/api/servo/status',
            self.get_status,
        )
        swagger_file = os.path.join(
            os.path.dirname(__file__), '../../data/api.yaml')

        if not os.path.exists(swagger_file):
            swagger_file = '/etc/openapi_servo_control/api.yaml'

        setup_swagger(
            self.app,
            api_version='0.0.0',
            swagger_url='/api/docs',
            swagger_from_file=swagger_file
        )

        static_routes = [
            ('GET', '/', self.static_handler),
            (
                'GET',
                r'/{filename:(\w|\-|\.)*\.(js|css|html|ttf|woff|woff2|ico)=?}',
                self.static_handler,
            ),
            (
                'GET',
                r'/{filename:assets\/.*=?}',
                self.static_handler,
            ),
        ]

        for route in static_routes:
            self.app.router.add_route(route[0], route[1], route[2])

        cors = aiohttp_cors.setup(self.app, defaults={
            '*': aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers='*',
                allow_headers='*',
                allow_methods='*',
                max_age=3600
            )
        })

        for route in list(self.app.router.routes()):
            if not isinstance(route.resource, web.StaticResource):
                cors.add(route)

    async def start(self):
        '''
        ---
        Starts http service
        '''
        logger.info('Internal web server enabled')
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '0.0.0.0', 3001)
        logger.info('worker started')
        await site.start()

    async def stop(self):
        '''
        ---
        Stops http service
        '''
        await self.runner.cleanup()

    @staticmethod
    async def static_handler(request):
        """
        ---
        Serves static files. Manual implementation to support
        index.html in case of the blank file name
        """
        try:
            filename = request.match_info['filename']
            if not filename:
                filename = 'index.html'
            if filename.endswith('/'):
                filename += 'index.html'
            request.match_info['filename'] = filename
        except KeyError as error:
            filename = 'index.html'
            logging.info('error while serve static %s', error)
        return web.FileResponse(STATIC_FOLDER + filename)

    async def set_position(self, request):
        '''
        ---
        Sets the position for the required axis
        '''
        axis_id = int(request.match_info['axis'])
        position = int(request.match_info['position'])
        self.axis_container.axises.get(axis_id).set_position(position)
        return web.json_response(
            {'status': 200, 'message': 'Request executed'}
        )

    async def set_velocity(self, request):
        '''
        ---
        Sets the velocity for the required axis
        '''
        axis_id = int(request.match_info['axis'])
        velocity = int(request.match_info['velocity'])
        self.axis_container.axises.get(axis_id).set_velocity(velocity)
        return web.json_response(
            {'status': 200, 'message': 'Request executed'}
        )

    async def set_speed(self, request):
        '''
        ---
        Sets the speed for the required axis
        '''
        axis_id = int(request.match_info['axis'])
        speed = int(request.match_info['speed'])
        self.axis_container.axises.get(axis_id).set_speed(speed)
        return web.json_response(
            {'status': 200, 'message': 'Request executed'}
        )

    async def set_tilt(self, request):
        '''
        ---
        Starts tilt for the required axis
        '''
        axis_id = int(request.match_info['axis'])
        angle = int(request.match_info.get('angle', Axis.tilt_angle))
        if angle is not None:
            self.axis_container.axises.get(axis_id).set_tilt(angle)
        else:
            self.axis_container.axises.get(axis_id).set_tilt()
        print(self.axis_container.axises.get(axis_id))
        return web.json_response(
            {'status': 200, 'message': 'Request executed'}
        )

    async def set_swing(self, request):
        '''
        ---
        Starts swing for the required axis
        '''
        axis_id = int(request.match_info['axis'])
        self.axis_container.axises.get(axis_id).set_swing()
        return web.json_response(
            {'status': 200, 'message': 'Request executed'}
        )

    async def get_speed(self, request):
        '''
        ---
        Returns current speed for the required axis
        '''
        axis_id = int(request.match_info['axis'])
        speed = self.axis_container.axises.get(axis_id).speed
        return web.json_response({'speed': speed})

    async def get_status(self, request):
        '''
        ---
        Implements url redirect from http to https
        '''
        logger.info(self.axis_container.axises)
        return web.json_response(
            self.axis_container.to_json()
        )

    async def get_axis_status(self, request):
        '''
        ---
        Implements url redirect from http to https
        '''
        axis_id = int(request.match_info['axis'])
        logger.info(self.axis_container.axises.get(axis_id))
        return web.json_response(
            self.axis_container.axises.get(axis_id).to_json()
        )
