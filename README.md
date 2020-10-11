Python Stuff on the Raspberry Pi

This repository contains three useful Python examples. 

Demo Print Test (A better print statement)
This is a replacement for simple print() statement. The MyPrint class expands the simple
print () statement with logging and fine control over what is printed/logged.

Demo Configfile Read (easily read from config files)
Often one needs to read parameters from a config file. The ConfigRead class makes this very easy touse.

Demo MQTT  (MQTT the easy way)
These two demo programs demonstrate the use of MQTT mosquitto in the pi. The MQTTCon class encapsulates
most of the code and make it easy to implement programs publishing and subscribing to the broker.
 
Folder sub contains the three Python files (classes)
Folder mosquitto_config holds files to setup a user config file for the mosquitto browser on the pi
Folder documentation contains a pdf for each demo explaining its workings

How to get all the files to your pi:
Open a terminal window, login to the pi and in the user pi home folder execute this command:
git clone https://github.com/dakota127/python_stuff.git

This will give you a folder python_stuff.

Free to use, modify, and distribute with proper attribution.
Frei für jedermann, vollständige Quellangabe vorausgesetzt.

