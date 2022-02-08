import board
import digitalio
import time
import busio
import analogio

from adafruit_wiznet5k.adafruit_wiznet5k import * #active WIZnet chip library
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket #open socket from WIZnet library

from adafruit_io.adafruit_io import IO_MQTT
import adafruit_minimqtt.adafruit_minimqtt as MQTT

from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

secrets = {
    'aio_username' : 'XXXXXXXXXXXXXX',   ### Wirte Username here ###
    'aio_key' : 'XXXXXXXXXXXXXX'  ### Write Active Key here ###
    }

# Set your Adafruit IO Username and Key in secrets.py
# (visit io.adafruit.com if you need to create an account,
# or if you need your Adafruit IO key.)
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]

# Activate GPIO pins for SPI communication
SPI0_SCK = board.GP18
SPI0_TX = board.GP19
SPI0_RX = board.GP16
SPI0_CSn = board.GP17

# Activate Reset pin for communication with W5500 chip
W5x00_RSTn = board.GP20

#A0 for PH input
PH  = analogio.AnalogIn(board.A0)
#A1 for OPR input
ORP = analogio.AnalogIn(board.A1)

# Initialize one-wire bus on board pin GP0.
ow_bus = OneWireBus(board.GP0)

# Scan for sensors and grab the first one found.
ds18 = DS18X20(ow_bus, ow_bus.scan()[0])

# Set LED for checking the network system  working
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

#Both sensor used the same ADC module, therefore used a Class to manage all data from PH and ORP signal
class data_manage:
    data = list()
    average = 0 
    total = 0
    ph_min = 0 #error value from the module
    orp_min = 10
    sample = 200 # Sample size
    mid = 1670 # middle value for calculate ORP result
    # Collect data only
    def collection (self,choice):
        for i in range(self.sample):
            if choice == 'PH':
                temp = int(PH.value)
            elif choice == 'ORP':
                temp = int(ORP.value)
            else:
                print("error")
            self.data.append(temp)
            time.sleep(0.02)
    #Calculate the actual value from the sensor     
    def calculation (self,choice):
        if len(self.data) == self.sample:
            self.total = sum(self.data)
            self.average = int(self.total/len(self.data)/64)
            if choice == 'PH':
                value = ((self.average*3300/1024)+self.ph_min)/1000
                actual = -5.741*value +16.654
                print(value)
            elif choice == 'ORP':
                value = int(((self.average*3.3*1000/1024)+self.orp_min))
                actual = (value-self.mid) /2.9
                print(value)
            self.average = 0
            self.total = 0
            self.data.clear()
            return actual

print("Wiznet5k Adafruit Up&Down Link Test (DHCP)")

# Setup your network configuration below
# random MAC, later should change this value on your vendor ID
MY_MAC = (0x00, 0x01, 0x02, 0x03, 0x04, 0x05)
IP_ADDRESS = (192, 168, 0, 111)
SUBNET_MASK = (255, 255, 0, 0)
GATEWAY_ADDRESS = (192, 168, 0, 1)
DNS_SERVER = (8, 8, 8, 8)

# Set reset function
ethernetRst = digitalio.DigitalInOut(W5x00_RSTn)
ethernetRst.direction = digitalio.Direction.OUTPUT

# Set this SPI for selecting the correct chip
cs = digitalio.DigitalInOut(SPI0_CSn)

# Set the GPIO pins for SPI communication
spi_bus = busio.SPI(SPI0_SCK, MOSI=SPI0_TX, MISO=SPI0_RX)

# Reset WIZnet's chip first
ethernetRst.value = False
time.sleep(1)
ethernetRst.value = True

# Initialize ethernet interface with DHCP
eth = WIZNET5K(spi_bus, cs, is_dhcp=True, mac=MY_MAC, debug=True)

# Show all information
print("Chip Version:", eth.chip)
print("MAC Address:", [hex(i) for i in eth.mac_address])
print("My IP address is:", eth.pretty_ip(eth.ip_address))

### Topic Setup ###
# Adafruit IO-style Topic
# Use this topic if you'd like to connect to io.adafruit.com
# mqtt_topic = secrets["aio_username"] + '/feeds/test'

### Code ###
# Define callback methods which are called when events occur
# pylint: disable=unused-argument, redefined-outer-name
def connected(clinet):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to Adafruit IO!")
    
    # Subscribe to Group
    io.subscribe(group_key=group_name)

def disconnected(clinet):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from Adafruit IO!")

def subscribe(client, userdata, topic, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))
    
def message(client, topic, message):
    # Method callled when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))

def on_led_msg(client, topic, message):
    # Method callled when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))
    if message == "1":
        led.value = True
    elif message == "0":
        led.value = False
    else:
        print("Unexpected message on LED feed")

# Initialize MQTT interface with the ethernet interface
MQTT.set_socket(socket, eth)

# Initialize a new MQTT Client object
mqtt_client = MQTT.MQTT(
    broker="io.adafruit.com",
    username=secrets["aio_username"],
    password=secrets["aio_key"],
    is_ssl=False,
)

# Initialize an Adafruit IO MQTT Client
io = IO_MQTT(mqtt_client)

# Setup the callback methods above
io.on_connect = connected
io.on_disconnect = disconnected
io.on_message = message
io.on_subscribe = subscribe

# Set up a callback for the led feed
io.add_feed_callback("led", on_led_msg)

# Group name
group_name = "aquacontrol"

# Feeds within the group
temp_feed = "aquacontrol.temperature"
PH_feed = "aquacontrol.ph"
ORP_feed = "aquacontrol.orp"

# Connect to Adafruit IO
print("Connecting to Adafruit IO...")
io.connect()

PH_read = data_manage()
ORP_read = data_manage()

# Main loop to print the temperature every second.
while True:
    io.loop()
    temp = int(ds18.temperature)
    print("Publishing value {0} to feed: {1}".format(temp, temp_feed))
    io.publish(temp_feed, temp)
    
    PH_read.collection('PH')
    PH_result = PH_read.calculation('PH')
    print("Publishing value {0} to feed: {1}".format(PH_result, PH_feed))
    io.publish(PH_feed, PH_result)
    
    ORP_read.collection('ORP')
    ORP_result = int(ORP_read.calculation('ORP'))
    print("Publishing value {0} to feed: {1}".format(ORP_result, ORP_feed))
    io.publish(ORP_feed, ORP_result)
    time.sleep(2)
            
            

