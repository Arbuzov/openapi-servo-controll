import asyncio
import logging
import pathlib
import signal

from .axis_container import AxisContainer
from .http_service import HttpService
from .servo_controller import Servocontroller


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():

    loop = asyncio.get_event_loop()
    axis = AxisContainer(15)
    servo_controler = Servocontroller(axis)
    http_service = HttpService(axis)
    signals = [signal.SIGHUP, signal.SIGTERM, signal.SIGINT]

    async def kill_loop():
        '''Watches tasks and stops the loop then all tasks are done'''
        loop = asyncio.get_event_loop()
        servo_controler.stop()
        await http_service.stop()
        while len([t for t in asyncio.all_tasks() if t is not
                   asyncio.current_task()]) > 0:
            logger.debug(asyncio.all_tasks())
            await asyncio.sleep(1)
        loop.stop()

    def shutdown_handler():
        ''''Graceful shutdown'''
        loop = asyncio.get_event_loop()
        loop.create_task(kill_loop())

    try:
        for _signal in signals:
            loop.add_signal_handler(_signal, shutdown_handler)
    except NotImplementedError:
        logging.warning('Not implemented signal')

    logger.info('Launching startup sequence')
    loop.create_task(servo_controler.start())
    loop.create_task(http_service.start())
    logger.info('Launching main loop')
    loop.run_forever()


if __name__ == '__main__':
    main()
