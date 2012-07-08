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
import urllib

# function found on the net to create nested url encoding, urllib doesn't do
# that by default, which makes Rails very sad
def recursive_urlencode(d):
    def recursion(d, base=None):
        pairs = []

        for key, value in d.items():
            if hasattr(value, 'values'):
                pairs += recursion(value, key)
            else:
                new_pair = None
                if base:
                    new_pair = "%s[%s]=%s" % (base, urllib.quote(unicode(key)), urllib.quote(unicode(value)))
                else:
                    new_pair = "%s=%s" % (urllib.quote(unicode(key)), urllib.quote(unicode(value)))
                pairs.append(new_pair)
        return pairs

    return '&'.join(recursion(d))

# Calls out to the website to get a list of all sensors and makes sure their
# switch status is the same as marked on the site
def check_switch_status():
    conn = httplib.HTTPConnection(url)
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
      try:
          # post the kwh reading to the website
          post_kwh_reading(c)
      except plugwise.exceptions.TimeoutException:
          print "Could not get kwh reading from %s", mac

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

def post_kwh_reading(circle):
    kwh_as_string = str(int(circle.get_power_usage()))
    headers = {"Content-type": "application/x-www-form-urlencoded"}
    params = recursive_urlencode({'sensor_reading': {'mac_address': '000D6F0000B81AB9', 'watthours': kwh_as_string}})
    conn = httplib.HTTPConnection(url)
    conn.request("POST", "/sensor_readings", params, headers)
    # at this point, not checking the result of the operation
    # not much we can do right now if the post doesn't go through

# =====================================================================
# Script start
# =====================================================================

# logging setup
logging.basicConfig(filename='polarmeter-client.log', level=logging.INFO)

# default location of the usb-to-serial-port usb device on a linux machine
device = "/dev/ttyUSB0"
url = "localhost:3000"

# known dictionary of sensors to be
# without this list we would not know the latest state and thus be forced to
# reset state every x seconds (which is NOT an NOP, it actually makes the
# Plugwise click)
# The state will only be forcefully every time the script starts
sensors = {}

sleep_time_in_seconds = 5

while True:
    check_switch_status()

    # print "Sleeping for 5 seconds"
    logging.debug("Sleeping for %s", sleep_time_in_seconds)
    time.sleep(sleep_time_in_seconds)
