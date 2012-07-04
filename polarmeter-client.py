# =====================================================================
# PolarMeter client script
#
# Note: to run in debug mode --log=DEBUG
# =====================================================================

from plugwise import *
import plugwise.util
import time
import httplib
import json
import logging

# logging setup
logging.basicConfig(filename='polarmeter-client.log', level=logging.INFO)

# default location of the usb-to-serial-port usb device on a linux machine
device = "/dev/ttyUSB0"

# known dictionary of sensors to be
# without this list we would not know the latest state and thus be forced to
# reset state every x seconds (which is NOT an NOP, it actually makes the
# Plugwise click)
# The state will only be forcefully every time the script starts
sensors = {}

sleep_time_in_seconds = 5

while True:
    conn = httplib.HTTPConnection("localhost:3000")
    conn.request("GET", "/sensors.json")
    r1 = conn.getresponse()

    logging.info('%s, %s', r1.status, r1.reason)
    data1 = r1.read()

    logging.debug(data1)

    for sensor in json.loads(data1)['sensors']:

      # utf8 or ascii won't matter as far as MACs are concerned
      mac = sensor['mac_address'].encode('utf8')
      enabled = sensor['enabled']

      # brute force approach, will change once we have authentication:
      # 1. get all of the sensors known to the system
      # 2. If known, check if state changed, if so, change state
      # 3. If not known, change state and add to known list

      # initialize connection to circle
      stick = Stick(device)
      c = Circle(mac, stick)

      if (mac in sensors and sensors[mac] != enabled) or (mac not in sensors):

          # disable/enable circle
          if enabled == True:
              logging.info("Switching %s on", mac)
              c.switch_on()
          else:
              logging.info("Switching %s off", mac)
              c.switch_off()

          # update local list of sensors
          sensors[mac] = enabled

    # we should eventually keep the connection open if there isn't a good
    # reason to shut it down
    conn.close()

    # print "Sleeping for 5 seconds"
    logging.debug("Sleeping for %s", sleep_time_in_seconds)
    time.sleep(sleep_time_in_seconds)
