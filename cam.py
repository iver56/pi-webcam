import picamera
import time
import datetime
import ftplib
from astral import Astral
from pytz import timezone
import traceback
import base64
import requests
import settings

def isItNight():
    a = Astral()
    city_name = 'Oslo'
    city = a[city_name]
    sun = city.sun(local=True)
    sunrise = sun['sunrise']
    dusk = sun['dusk']
    now = datetime.datetime.now(timezone('CET'))
    return (now < sunrise or now > dusk)

def restart():
    command = '/usr/bin/sudo /sbin/shutdown -r now'
    import subprocess
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    print(output)

filepath = '/run/shm/cam.jpg'
counter = 0
try:
    while True:
        with picamera.PiCamera() as camera:
            camera.resolution = (2592, 1944)
            camera.led = False
            if isItNight():
                camera.exposure_mode = 'night'
            camera.start_preview()
            time.sleep(2)
            camera.capture(filepath, resize=(1024, 768), quality=12)
            camera.stop_preview()

        if counter == 300: #reboot every now and then
            time.sleep(40)
            restart()
        
        with open(filepath, 'rb') as file:
            encoded_string = base64.b64encode(file.read())
        url = settings.ENDPOINT_URL
        payload = {
            'base64': encoded_string,
            'hub_password': settings.HUB_PASSWORD
        }
        response = requests.post(url, payload)
        time.sleep(360)
        counter += 1
except:
    traceback.print_exc()
    time.sleep(1200)
    restart()

