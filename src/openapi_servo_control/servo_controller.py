'''
Created on 9 Oct 2020

@author: whitediver
'''
import asyncio
import logging

import Adafruit_PCA9685

from .axis_container import AxisContainer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Servocontroller(object):
    '''
    This class manages servodrivers
    '''
    frequency = 60
    zero_position = 90

    def __init__(self, axis_container: AxisContainer):
        '''
        Constructor
        '''
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.pwm.set_pwm_freq(Servocontroller.frequency)
        self.started = False
        self.axis_container = axis_container
        self.update_delay = 0.02  # 50 FPS для более плавного движения

    async def start(self):
        self.started = True
        '''
        for key in self.axis_container.axises:
            self.axis_container.axises.get(key).set_position(
                Servocontroller.zero_position)
            await asyncio.sleep(3)
        '''
        while self.started:
            self.axis_container.apply_velocity()
            for key in self.axis_container.axises:
                if self.axis_container.axises.get(key).position is not None:
                    pulse_len = int(
                        float(
                            self.axis_container.axises.get(key).position
                        ) * 500.0 / 180.0
                    ) + 110
                    self.pwm.set_pwm(key, 0, pulse_len)
                    # logger.debug(self.axis_container.axises.get(key))
            await asyncio.sleep(self.update_delay)

    def stop(self):
        self.started = False

    def set_delay(self, delay: float):
        """Set update delay between coordinate refreshes."""
        try:
            self.update_delay = float(delay)
        except (ValueError, TypeError):
            logger.warning('Incorrect delay value: %s', delay)
