"""Shared pytest fixtures and hardware stubs.

Adafruit_PCA9685 and smbus talk to real I2C hardware that isn't present
on CI runners, so stub them in sys.modules before any project module
that imports them is loaded. setup_swagger is also neutralized because
the bundled api.yaml path is resolved relative to the installed package
layout and isn't available in the test environment.
"""
import sys
from unittest.mock import MagicMock

for _name in ('Adafruit_PCA9685', 'smbus', 'smbus2', 'Adafruit_GPIO',
              'Adafruit_GPIO.I2C'):
    sys.modules.setdefault(_name, MagicMock())

import openapi_servo_control.http_service as _http_service  # noqa: E402

_http_service.setup_swagger = lambda *a, **kw: None
