# Aquaponic system
By using WIZNet's W5100S-EVB-PICO, this aquaponic system has used circuitpython coding with adafruit's and WIZnet reference code to develop.

Most of the monitoring procedure and controls could be handle throguh adafruit IO 

### 🟥 [Youtube][link-aquaponic youtube]

Reference code:
1. [WIZnet][link-WIZnet circuitpython]
2. [Adafruit][link-adafruit]
3. [Circuitpython][link-circuitpython]

![][link-aquaimg]

## Why use circuitpython and how to setup
The reason for using circuitpython is adafruit and circuitpython provided a lot of reference source code that I could easily to implement.

It also could easily changed to different MCU with the same platform (It required to use WIZnet's [IO module][link-iomodule] on other MCU solutions)

For how to setup circuitpython to W5100S-EVB-PICO, please refer the links below.

1. [Setup link 1][link-setup from plant]
2. [Setup link 2][link-setup from general] 

## Communication Method
The communication method fo this aquaponic system has used Adafruit IO for monitoring and control purpose.

The protocol that has been used in this system is using MQTT protocol. 

For more information, please refer to the link below.

1. [Adafruit IO communication link][link-setup from plant]

## System design diagram
THe aquaponic system is using few monitor features with a simple physic on fluid flow
![][link-flow diagram]

### Main flow
1. Pumping water up to the plantation section to provide water and food (Nitrate)
2. Plantation will absorb the water and drop back to the plantation tank
3. PH and ORP sensors will record the water values. (This section is could collect stable result - without vibration)
4. By using platsic tubes, Water will flow from the plantation section back to the fish tank

### Others
1. LED is providing the best lightwave for the plants to grow
2. Temperature sensor is to ensure the temperature of the fish tank is suitable for fish to live

### Error Prevention
1. Water level sensor is preventing the water on the plantation section has overflow

## Connection Diagram

![][link-connection diagram]

### Digital IO
1. Water Temperature sensor (DS18S20) - Powered by PH sensor (GP0)
2. Water level sensor (GP1)
3. Pump - Using [MOSFET relay][link-mosfet] to control the pump (GP2)
4. LED light control - Using [MOSFET relay][link-mosfet]  to act as switch (GP3) 

### Analogue IO
1. PH - Reads the PH level (A0)
2. ORP - Reads the ORP level (A1)

## Monitoring
There are few important values required to monitor. These varibales is ensuring the fish tank and plants could have a good environment to live.

1. PH values - Measure the PH values from 0 - 14 ([Product link][link-PH])
2. ORP values - Measire the ORP values from -2000mV - 2000mV ([Product link][link-ORP])
3. Temperature - Measure the Temperature by using DS18S20 onebus module ([Product link][link-PH])

## Control
Simple controls for ensuring the system could work normally

1. Pump - special for fish tanks (USB power) ([Product link][link-fishpump])
2. LED light - found a specific for plantation purpose LED light (Purple) ([Product link][link-led])
      1. If you want to upgraded into a neopixel version, please go to the ([Neopixel link][link-neopixel])

## Error prevention
Error May accor:
1. Water pump will still provide power pumping after the software section shows error
2. Plastic tubes for returning water back to fish tank may have a chance to have blockage

Solution:
1. Water level sensor to detect the water level to prevent overflow ([Product link][link-waterlevel])
2. If there are software error created, turn off the water pump


## Software
### Bundles:
1. [Circuit Python 7.0][link-circuit python] (it required to use 1 MB from the flash) 
2. [Adafruit circuit python bundle][link-adafruitbundle] - Use the latest version from adafruit bundle page
3. [WIZnet's circuit python bundle][link-wiznet] - Use the latest version from WIZnet bundle page

### Required Libraries from adafruit bundle:
1. adafruit_bus_services folder
2. adafruit_io folder
3. adafruit_minimqtt folder
4. adafruit_wiznet5k folder
5. adafruit_onewire folder
6. adafruit_request
7. adafruit_ds18x20

## Coding setup
If you wanted to know the coding method for adafruit IO, please refer the link below.

[Adafruit IO communication procedure][link-setup from plant]

## PH value
PH values related to the ratio between the ammonia(NH3) to ammonium (NH4+)

1. When PH increased, the amount of ammonia will increase and ammonium will decrease
2. When PH decreased, the amount of ammonia will decrease and ammonium will increase

Ammonia is created from fishes wasted and the food remains inside the fishing tanks. Ammonia is a toxic component to the fishes, therefore it is important for removing these toxic materials from the fish tank.

Ammonia in water will quickly picks up a proton and transform to ammonium that is not harmful to the fish. Ammonium could be apsorb and used by plants, therefore increasing the the numbers of ammonium would be helpful for making the water turn clean by plants. 

According to my research, PH value within 6.8 - 7 is the bast value for the fish and the plants.

Reference: 
1. [Aquapros - Ammonia][link-aquapros]
2. [Aquaponic research 1][link-research 1]

## ORP value
ORP values is calculating the oxidizer agents and reducing agents

ORP values is calucating in millivolts (mv). 

1. When there are a lot of oxidizer, it wanted to absorbed more electrons. Therefore it creates a positive voltage
2. When there are a lot of reducing agents, it creates a lot of electrons for oxidizer. This creates a negative voltage

By using ammonium as the only method to remove the ammonia from the fish tank, it will not be a enough to remove most of the ammonia.

Using bacteria to extra method to create more foods for the plant and reduce the ammonia is the best way to solve this issue. 

There are bacterias could covert ammonia into nitrates. Nitrates are the best food source for plant growth. 

Howevever, nitrates are still toxic to fish. Thus, it is important to remove these toxic materials from the fish tank.

1. Nitrates  = oxidizer agent
2. Ammonia  = reducing agent

According to my research, having a positive voltage results means there would be a highly chance to have more food inside the fish tank.

Suggested OPR value is 350mV - 450mV

Reference:
1. [Aquapros - nitrates][link-aquapros1]
2. [ORP research][link-research 2]

## Coding method
1. Collecting data (200 samples)
```python
    def collection (self,choice,counter):
        if counter < self.sample: #check sample size
            if choice == 'PH': #determine the data needs to input into the list
                temp = int(PH.value) #collect data from the related analogue IO pin
                self.P_data.append(temp)  #save it to the related list
            elif choice == 'ORP':
                temp = int(ORP.value)
                self.O_data.append(temp)
            else:
                print("error")
```
2. Calculation for PH values and ORP values
```python
    def calculation (self,choice):
        if choice == 'PH':
            if len(self.P_data) == self.sample: #check the sample size is correct
                self.total = sum(self.P_data) 
                self.average = int(self.total/len(self.P_data)/64) #finalize the sample size into 1024 bit and calculate the average
                value = ((self.average*3300/1024)+self.ph_min)/1000 # calculate the PH value
                actual = -5.741*value +16.654
                print(value)
                self.average = 0
                self.total = 0
                self.P_data.clear()
        elif choice == 'ORP':
            if len(self.O_data) == self.sample:
                self.total = sum(self.O_data)
                self.average = int(self.total/len(self.O_data)/64)
                value = int(((self.average*3.3*1000/1024)+self.orp_min))
                actual = ((value-self.mid) /3.1)+ self.orp_cal #calculate the ORP value
                print(value)
                self.average = 0
                self.total = 0
                self.O_data.clear()
        return actual
```
3. Error prevention
```python
while True:
    io.loop(0.02) #check is there any updates from the MQTT channel
    try:
            
        PH_read.collection('PH',counter) #collect data every 0.02 second
        ORP_read.collection('ORP',counter)  
        if counter == 200: #after received 200 samples
            temp = int(ds18.temperature) #get the temperature value
            print("Publishing value {0} to feed: {1}".format(temp, temp_feed))
            io.publish(temp_feed, temp)
            
            PH_result = PH_read.calculation('PH') # calcuate the PH value 
            print("Publishing value {0} to feed: {1}".format(PH_result, PH_feed))
            io.publish(PH_feed, PH_result)
    
            ORP_result = int(ORP_read.calculation('ORP')) # calcuate the ORP value 
            print("Publishing value {0} to feed: {1}".format(ORP_result, ORP_feed))
            io.publish(ORP_feed, ORP_result)
            counter  = -1  #reset the counter back to zero
            #Maintain the error is not active, unless the water level is overflow    
            if water_alarm.value == 0: #if overflow
                error_value = 1
                pump.value = 0 #stop pump
                error_msg = "Water overflow - check water flow"
                print("Publishing value {0} to feed: {1}".format(error_value, error_feed)) #update the indicator
                io.publish(error_feed, error_value)
                print("Publishing value {0} to feed: {1}".format(error_msg, error_msg_feed)) #update the message
                io.publish(error_msg_feed, error_msg)
                break #stops everything after upload the information to adafruit io
            else:
                print("Publishing value {0} to feed: {1}".format(error_value, error_feed))
                io.publish(error_feed, error_value)  #if the water level is under the sensor, it won't alert the error indicator
            
        counter += 1 # counter 
     
    #error occurs - stop all pumps   
    except RuntimeError as error: #when software error occurs
        pump.value = 0 
        error_value = 1 #turn off the pump 
        #upload errors
        print("Publishing value {0} to feed: {1}".format(error_value, error_feed))
        io.publish(error_feed, error_value)
        error_msg = error.args[0]
        print("Publishing value {0} to feed: {1}".format(error_msg, error_msg_feed))
        io.publish(error_msg_feed, error_msg)
        break #turn off everything

    except Exception as error: #Another possible software error occurs
        pump.value = 0
        error_value = 1
        #upload errors
        print("Publishing value {0} to feed: {1}".format(error_value, error_feed))
        io.publish(error_feed, error_value)
        error_msg = error.args[0]
        print("Publishing value {0} to feed: {1}".format(error_msg, error_msg_feed))
        io.publish(error_msg_feed, error_msg)
        raise error
        break
```
## Dashboard display
![][link-dashboard]



[link-WIZnet circuitpython]:https://github.com/Wiznet/RP2040-HAT-CircuitPython
[link-adafruit]:https://github.com/adafruit/Adafruit_CircuitPython_Bundle
[link-circuitpython]: https://circuitpython.org/
[link-iomodule]: https://www.wiznet.io/product/network-module/
[link-setup from plant]:https://github.com/ronpang/Smart-Plant-WIZnet-Ethernet-HAT-Raspberry-PI-PICO-
[link-setup from general]: https://github.com/Wiznet/RP2040-HAT-CircuitPython/blob/master/Ethernet%20Example%20Getting%20Started%20%5BCircuitpython%5D.md
[link-flow diagram]: https://github.com/ronpang/Aquaponic-system/blob/main/aquaponic%20system%20structure.PNG
[link-connection diagram]: https://github.com/ronpang/Aquaponic-system/blob/main/aquaponic%20connection%20diagram.PNG
[link-PH]: https://item.taobao.com/item.htm?spm=a230r.1.14.16.10341e49n9vO3m&id=608203826244&ns=1&abbucket=9#detail
[link-ORP]: https://item.taobao.com/item.htm?spm=a230r.1.14.20.647f6566nldcXV&id=614953359192&ns=1&abbucket=9#detail
[link-fishpump]: https://item.taobao.com/item.htm?spm=a230r.1.14.16.63591ab6OsFyqX&id=612904638950&ns=1&abbucket=6#detail
[link-led]: https://item.taobao.com/item.htm?spm=a230r.1.14.38.5b5677edy8OI2q&id=642558377399&ns=1&abbucket=6#detail
[link-neopixel]: https://github.com/ronpang/WIZnet-HK_Ron/blob/main/Adafruit%20io/Adafruit%20io%20(pixel%20light%20control).py
[link-aquaimg]: https://github.com/ronpang/Aquaponic-system/blob/main/IMG_0154.JPG
[link-aquapros]: https://www.youtube.com/watch?v=v1vIyGf9kRI
[link-research 1]: https://learn.eartheasy.com/articles/how-to-grow-with-aquaponics-in-5-simple-steps/
[link-aquapros1]: https://www.youtube.com/watch?v=dFk6m-1zxyE
[link-research 2]: http://reefkeeping.com/issues/2003-12/rhf/feature/index.htm
[link-dashboard]: https://github.com/ronpang/Aquaponic-system/blob/main/aquaponic%20adafruit%20dashboard.PNG
[link-circuit python]: https://circuitpython.org/
[link-adafruitbundle]: https://github.com/adafruit/Adafruit_CircuitPython_Bundle
[link-wiznet]: https://github.com/Wiznet/RP2040-HAT-CircuitPython
[link-waterlevel]: https://item.taobao.com/item.htm?spm=a230r.1.14.16.6a522d7cTLnbZU&id=610994738551&ns=1&abbucket=6#detail
[link-mosfet]: https://item.taobao.com/item.htm?spm=a230r.1.14.58.5e5071efH4OSxI&id=556895473089&ns=1&abbucket=6#detail
[link-aquaponic youtube]: https://www.youtube.com/watch?v=7pQ-9O_Bbr0
