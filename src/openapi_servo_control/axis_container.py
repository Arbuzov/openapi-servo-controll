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
        self.target_position = None  # Целевая позиция для плавного движения
        self.velocity = None
        self.movement = None
        self.tilt_angle = Axis.tilt_angle
        self.max_step = 2.0  # Максимальный шаг за одно обновление для плавности

    def to_json(self):
        logger.info('dictify')
        return {
            'name': self.name,
            'velocity': self.velocity,
            'position': self.position,
            'target_position': self.target_position,
            'movement': self.movement,
            'max_step': self.max_step,
        }

    def __str__(self):
        logger.info('stringify')
        return (
            f'Name: "{self.name}", '
            f'Velocity "{self.velocity}", '
            f'Position "{self.position}"'
        )

    def set_position(self, position):
        self.target_position = position
        if self.position is None:
            self.position = position  # Мгновенная установка если позиция не задана
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

    def set_swing(self, angle=None):
        self.movement = 'SWING'
        self.position = Axis.tilt_base
        if angle is not None:
            self.tilt_angle = angle
        self.velocity = 1

    def tilt_axis(self):
        self.position = Axis.tilt_base - self.tilt_angle + \
            round(self.tilt_angle * random.random())

    def swing_axis(self):
        # Более плавное swing движение
        if (self.position > Axis.tilt_base + self.tilt_angle / 2):
            self.velocity = -min(1.0, self.max_step)
        elif (self.position < Axis.tilt_base - self.tilt_angle / 2):
            self.velocity = min(1.0, self.max_step)
        self.move_axis()

    def move_axis(self):
        # Плавное движение с ограничением шага
        if self.velocity != 0:
            step = min(abs(self.velocity), self.max_step)
            if self.velocity > 0:
                self.position = self.position + step
            else:
                self.position = self.position - step
        
        # Плавное движение к целевой позиции
        if self.target_position is not None and self.velocity == 0:
            diff = self.target_position - self.position
            if abs(diff) > 0.1:  # Небольшая зона нечувствительности
                step = min(abs(diff), self.max_step)
                if diff > 0:
                    self.position = self.position + step
                else:
                    self.position = self.position - step
            else:
                self.position = self.target_position
                self.target_position = None


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
            axis_obj = self.axises.get(axis)
            if axis_obj.movement == 'TILT':
                axis_obj.tilt_axis()
            elif axis_obj.movement == 'SWING':
                axis_obj.swing_axis()
            elif axis_obj.velocity is not None or axis_obj.target_position is not None:
                axis_obj.move_axis()

    def set_axis_value(self, axis_id, value):
        self.axises.get(axis_id).position = value

    def to_json(self):
        logger.info('dictify')
        result = []
        for axis in self.axises:
            result.append(self.axises.get(axis).to_json())
        return result
