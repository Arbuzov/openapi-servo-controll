'''
Created on 9 Oct 2020

@author: info
'''
import logging
import random


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Axis(dict):
    '''
    classdocs
    '''

    tilt_base = 90
    tilt_angle = 30

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.name = ''
        self.position = None
        self.velocity = None
        self.movement = None
        self.tilt_angle = Axis.tilt_angle

    def to_json(self):
        logger.info('dictify')
        return {
            'name': self.name,
            'velocity': self.velocity,
            'position': self.position,
            'movement': self.movement,
        }

    def __str__(self):
        logger.info('stringify')
        return (
            f'Name: "{self.name}", '
            f'Velocity "{self.velocity}", '
            f'Position "{self.position}"'
        )

    def set_position(self, position):
        self.position = position
        self.velocity = 0
        self.movement = None

    def set_velocity(self, velocity):
        self.velocity = velocity
        if self.position is None:
            self.position = 0
        self.movement = None

    def set_tilt(self, angle=None):
        self.movement = 'TILT'
        self.position = Axis.tilt_base
        if angle is not None:
            self.tilt_angle = angle

    def set_swing(self):
        self.movement = 'SWING'
        self.position = Axis.tilt_base
        self.velocity = 1

    def tilt_axis(self):
        self.position = Axis.tilt_base - self.tilt_angle + \
            round(self.tilt_angle * random.random())

    def swing_axis(self):
        if (self.position > Axis.tilt_base + Axis.tilt_angle / 2):
            self.velocity = -1
        elif (self.position < Axis.tilt_base - Axis.tilt_angle / 2):
            self.velocity = 1
        self.move_axis()

    def move_axis(self):
        self.position = self.position + self.velocity


class AxisContainer(object):
    '''
    classdocs
    '''

    def __init__(self, axis_number=15):
        '''
        Constructor
        '''
        self.axises = {}
        for key in range(0, axis_number):
            axis = Axis()
            axis.name = 'Axis ' + str(key)
            self.axises.setdefault(key, axis)

    def apply_velocity(self):
        for axis in self.axises:
            if self.axises.get(axis).movement == 'TILT':
                self.axises.get(axis).tilt_axis()
            elif self.axises.get(axis).movement == 'SWING':
                self.axises.get(axis).swing_axis()
            elif self.axises.get(axis).velocity is not None:
                self.axises.get(axis).move_axis()

    def set_axis_value(self, axis_id, value):
        self.axises.get(axis_id).position = value

    def to_json(self):
        logger.info('dictify')
        result = []
        for axis in self.axises:
            result.append(self.axises.get(axis).to_json())
        return result
