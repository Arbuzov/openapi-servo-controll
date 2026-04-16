"""Smoke test: the package imports and main entry points are reachable."""
import openapi_servo_control
from openapi_servo_control.axis_container import Axis, AxisContainer
from openapi_servo_control.http_service import HttpService
from openapi_servo_control.servo_controller import Servocontroller


def test_package_exposes_main():
    assert callable(openapi_servo_control.main)


def test_core_classes_importable():
    assert Axis is not None
    assert AxisContainer is not None
    assert HttpService is not None
    assert Servocontroller is not None
