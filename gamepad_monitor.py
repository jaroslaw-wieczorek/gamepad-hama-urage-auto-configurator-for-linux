import shlex
import usb
import threading
import logging
import pyudev
import time
import subprocess
from pathlib import Path


class USBDetector:
    ''' Monitor udev for detection of USB '''

    def __init__(self, logger=None):
        ''' Initiate the object '''
        self.logger = logger or self._create_default_logger()
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='input')

        # Start monitoring thread
        self.thread = threading.Thread(target=self._work)
        self.thread.daemon = True
        self.thread.start()

    def _create_default_logger(self):
        ''' Create a default logger '''
        logger = logging.getLogger('USBDetector')
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger

    def _work(self):
        ''' Runs the actual loop to detect the events '''
        self.logger.info("Starting to monitor for USB devices.")
        self.monitor.start()

        for device in iter(self.monitor.poll, None):
            if device.action == 'add' and device.sys_name.startswith('event'):
                self.on_attached(device)
            elif device.action == 'remove':
                self.on_deleted()

    def on_attached(self, device):
        self.logger.info("USB device attached")
        try:
            dev = usb.core.find(idVendor=0x045e, idProduct=0x028e)
            if dev:
                event_device_path = Path(f"/sys/class/input/{device.sys_name}/device").resolve()
                dev_input = self._get_inputx_name_for_dev(dev, event_device_path.name)

                if dev_input:
                    self.logger.info("Initializing Gamepad.")
                    dev.ctrl_transfer(0xc1, 0x01, 0x0100, 0x00, 0x14)
                    time.sleep(1)
                    
                    js_device = self._find_js_device(device.device_node)
                    self._calibrate_device(js_device)

        except usb.core.USBError as e:
            self.logger.error(f"USB Error during initialization: {e}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Calibration script failed: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")

    def on_deleted(self):
        self.logger.info("USB device detached")

    def _find_js_device(self, event_device):
        ''' Find the correct js device associated with the given event device '''
        self.logger.info(f"Looking for js device for {event_device}")
        event_name = Path(event_device).name

        # Look through the /dev/input/ to map event device to js device
        for js in Path('/dev/input/').glob('js*'):
            js_phys_path = Path(f'/sys/class/input/{js.name}/device').resolve()
            event_phys_path = Path(f'/sys/class/input/{event_name}/device').resolve()

            if js_phys_path == event_phys_path:
                self.logger.info(f"Found matching js device: {js}")
                return js

        self.logger.error("No matching js device found.")
        return None

    def _get_inputx_name_for_dev(self, dev, device_input):
        '''Get the name of the first input device in the given base path using glob.'''
        base_path = Path(f'/sys/bus/usb/devices/{dev.bus}-{dev.port_number}:1.0/input/')
        return next((input_x.name for input_x in base_path.glob('input*') if device_input == input_x.name), None)

    def _calibrate_device(self, js_device):
        '''Calibrate the given js device'''
        if js_device:
            command = shlex.split(f"./calibrate.sh {js_device}")
        else:
            self.logger.warning("Could not find js device associated with event. Trying default js0.")
            command = shlex.split(f"./calibrate.sh")

        self.logger.info("Mapping and calibrating Gamepad.")
        result = subprocess.run(command, check=True)
        self.logger.info(f"Calibration script finished with return code {result.returncode}.")



if __name__ == '__main__':
    logger = logging.getLogger('USBDetector')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

    detector = USBDetector(logger=logger)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.logger.info("Program terminated by user.")
