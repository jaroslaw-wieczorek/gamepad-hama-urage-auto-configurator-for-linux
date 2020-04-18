#!/usr/bin/python3.8
import usb
import threading
import logging
import pyudev
import time
import subprocess



class USBDetector():
    ''' Monitor udev for detection of usb '''
 
    def __init__(self):
        ''' Initiate the object '''
        thread = threading.Thread(target=self._work)
        thread.daemon = False
        thread.start()
 
    def _work(self):
        ''' Runs the actual loop to detect the events '''
        
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='input')
        pass

        # this is module level logger, can be ignored
        #LOGGER.info("Starting to monitor for usb")
        self.monitor.start()

        for device in iter(self.monitor.poll, None):
            #LOGGER.info("Got USB event: %s", device.action)
            if device.action == 'add':
                if device.sys_name.startswith('event'):
                    dev = usb.core.find(idVendor=0x045e, idProduct=0x028e)

                    if dev is not None:
                        print("Init Gamepad")
                        dev.ctrl_transfer(0xc1, 0x01, 0x0100, 0x00, 0x14)

                        time.sleep(1)
                        print("Mapping and calibrate Gamepad")
                        subprocess.call("/bin/xbox_gamepad_calibrate.sh")

                
                # some function to run on insertion of usb

                    self.on_attached()

            if device.action == 'remove':
                
                # some function to run on removal of usb
                self.on_deleted()

	
    def on_attached(self):
        print("Gamepad attached")


    def on_deleted(self):
        print("Gamepad dettached")

if __name__ == '__main__':
        USBDetector()