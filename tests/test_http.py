from aiohttp.test_utils import AioHTTPTestCase

from openapi_servo_control.axis_container import Axis, AxisContainer
from openapi_servo_control.http_service import HttpService


class FakeServoController:
    def __init__(self):
        self.update_delay = 0.02

    def set_delay(self, delay):
        self.update_delay = float(delay)


class HttpServiceTestCase(AioHTTPTestCase):
    async def get_application(self):
        self.container = AxisContainer(3)
        self.controller = FakeServoController()
        self.service = HttpService(self.container, self.controller)
        return self.service.app

    async def test_set_position(self):
        resp = await self.client.post('/api/servo/0/position/45')
        assert resp.status == 200
        body = await resp.json()
        assert body['status'] == 200
        assert self.container.axises[0].target_position == 45
        assert self.container.axises[0].position == 45

    async def test_set_position_negative(self):
        resp = await self.client.post('/api/servo/1/position/-30')
        assert resp.status == 200
        assert self.container.axises[1].target_position == -30

    async def test_set_velocity_float(self):
        resp = await self.client.post('/api/servo/0/velocity/1.25')
        assert resp.status == 200
        assert self.container.axises[0].velocity == 1.25
        assert self.container.axises[0].position == 0

    async def test_set_velocity_negative(self):
        resp = await self.client.post('/api/servo/0/velocity/-0.5')
        assert resp.status == 200
        assert self.container.axises[0].velocity == -0.5

    async def test_set_tilt_default_angle(self):
        resp = await self.client.post('/api/servo/2/tilt')
        assert resp.status == 200
        axis = self.container.axises[2]
        assert axis.movement == 'TILT'
        assert axis.tilt_angle == Axis.tilt_angle

    async def test_set_tilt_custom_angle(self):
        resp = await self.client.post('/api/servo/2/tilt/55')
        assert resp.status == 200
        axis = self.container.axises[2]
        assert axis.movement == 'TILT'
        assert axis.tilt_angle == 55

    async def test_set_swing_valid_angle(self):
        resp = await self.client.post('/api/servo/0/swing/40')
        assert resp.status == 200
        axis = self.container.axises[0]
        assert axis.movement == 'SWING'
        assert axis.tilt_angle == 40
        assert axis.velocity == 1

    async def test_set_swing_rejects_out_of_range(self):
        resp = await self.client.post('/api/servo/0/swing/181')
        # Route regex \d+ accepts 181; handler validates and rejects.
        assert resp.status == 400

    async def test_set_swing_unknown_axis(self):
        # Axis 99 is outside the 3-axis container; axises.get returns None.
        resp = await self.client.post('/api/servo/99/swing/30')
        assert resp.status == 404

    async def test_set_position_unknown_axis(self):
        resp = await self.client.post('/api/servo/99/position/45')
        assert resp.status == 404

    async def test_set_velocity_unknown_axis(self):
        resp = await self.client.post('/api/servo/99/velocity/1.0')
        assert resp.status == 404

    async def test_set_tilt_unknown_axis(self):
        resp = await self.client.post('/api/servo/99/tilt/30')
        assert resp.status == 404

    async def test_get_axis_status(self):
        self.container.axises[0].set_position(60)
        resp = await self.client.get('/api/servo/0/status')
        assert resp.status == 200
        data = await resp.json()
        assert data['name'] == 'Axis 0'
        assert data['position'] == 60

    async def test_get_axis_status_unknown_axis(self):
        resp = await self.client.get('/api/servo/99/status')
        assert resp.status == 404

    async def test_get_status_returns_list(self):
        resp = await self.client.get('/api/servo/status')
        assert resp.status == 200
        data = await resp.json()
        assert isinstance(data, list)
        assert len(data) == 3

    async def test_set_delay_updates_controller(self):
        resp = await self.client.post('/api/servo/delay/0.1')
        assert resp.status == 200
        assert self.controller.update_delay == 0.1

    async def test_set_smoothness_updates_all_axises(self):
        resp = await self.client.post('/api/servo/smoothness/3.5')
        assert resp.status == 200
        for axis in self.container.axises.values():
            assert axis.max_step == 3.5
