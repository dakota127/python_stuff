#!/usr/bin/python
# coding: utf-8
# ***********************************************************
#
# This is program TWO of a suite of two programs to demonstrate and test
# MQTT functionality on a Raspberry Pi
# Runs with Python3   and not tested under Python2 (it should run, however)
# 
# This version of the program uses the  MQTT_Conn class tha encapsulates MQTT
#
# enhanced by Peter (Sept 2020)
# *********************************************************

import paho.mqtt.client as mqtt
import argparse, os, sys
import socket
import time
from sub.myprint import MyPrint             # Class MyPrint replace print, debug output
from sub.mqtt import MQTT_Conn              # Class MQTT_Conn handles MQTT stuff
import random
import asyncio
# Define Variables

DEBUG_LEVEL0=0
DEBUG_LEVEL1=1
DEBUG_LEVEL2=2
DEBUG_LEVEL3=3
debug=0
mqtt_status = False
mqtt_error = 0
wait_time = 6
retry = False
MQTT_TOPIC_PUB =   "test2"      # test2
MQTT_TOPIC_SUB =   "test"           # test
MQTT_TOPIC_CMD =   "commands"
mqtt_broker_ip_cmdline = ""     # ipc adr from commandline

MESSAGES = [                    # message payloads to be sent
    "Karl Popper",
    "Ernest Rutherford",
    "Wolfgang Amadeus Mozart",
    "Lee Child",
    "Mark Twain",
    "Thomas Mann",
    "Ludwig van Beethoven",
    "Steven Spielberg",
    "Albert Einstein",
    "Henry Poincarre",
]

progname = "demo_mqtt_pub"
number_messages = 0
logfile_name = ""
# instances of classes
myprint = 0
mqttc = 0

# ***** Function Parse commandline arguments ***********************
#----------------------------------------------------------
# get and parse commandline args
def argu():
    global debug, number_messages,mqtt_broker_ip_cmdline

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="small debug", action='store_true')
    parser.add_argument("-D", help="medium debug", action='store_true')
    parser.add_argument("-A", help="details debug", action='store_true')
    parser.add_argument("-r", help="retry indicator", action='store_true')
    parser.add_argument("-n", help="number of messages to send", type=int)
    parser.add_argument("-i", help="IP Addr", type=str)

    args = parser.parse_args()

    if args.d:
        debug=DEBUG_LEVEL1
    if args.D:
        debug=DEBUG_LEVEL2
    if args.A:
        debug=DEBUG_LEVEL3
    if args.r:
        retry = True
    if args.n:
        number_messages= args.n
    if args.i: 
       mqtt_broker_ip_cmdline = args.i
 
    return(args)
#----------------------------------------------------------

          

# Function to publish mesages
#-------------------------------------------------
def publish_messages ():
    counter =0
    global sends, number_messages

    print ("publishing messages....")
    if (number_messages == 0):                      # no input
        number_messages =  random.randint(2,12)      #  random number of messages  
#    number_messages = 1
    for y in range (0,number_messages):
        #  format payload string 
        #  byte zero:           message indicator (0=normal message, 9=last message)
        #  byte one,two, three: message count with leading zeros
        #  from byte four:     text
        payload = "{:d}{:03d}{}".format (0,y, random.choice(MESSAGES)) 
        mqtt_error = mqttc.publish_msg (MQTT_TOPIC_SUB, payload)
#        time.sleep(0.3)
        if mqtt_error > 0:
            myprint.myprint (DEBUG_LEVEL0, progname +  ": publish returns errorcode: {}".format(mqtt_error)) 
            return (mqtt_error)

    #   send last message with indicator 8 and some text
    payload = "{:d}{:03d}{}".format (8,0, "the end")
    mqtt_error = mqttc.publish_msg (MQTT_TOPIC_SUB, payload)
    
    print ("Number of messages sent: {}".format(number_messages))
    number_messages = 0
    return (mqtt_error)

  

# handle incoming messages with topic MQTT_TOPIC_PUB
#--------------------------------------
def handle_message_1 (client, userdata, message):
     print ("message received: {}, userdata: {} ".format( message.payload.decode(), userdata))
        
        
# --- do subscribe and publish
# --- needs to be called after initial connection and after reconnect
#-------------------------------------------------------------       
def do_pub():        
# subscribe to MQTT topics   
    res = mqttc.subscribe_topic (MQTT_TOPIC_PUB , handle_message_1)     # subscribe to topic
    if (res > 0):
   
        myprint.myprint (DEBUG_LEVEL0, progname +  ": subscribe returns errorcode: {}".format(res)) 
        myprint.myprint (DEBUG_LEVEL0, progname +  ": terminating")       
        sys.exit(2)
    myprint.myprint (DEBUG_LEVEL0,  progname +  ": subscribed to topic: {} ".format(MQTT_TOPIC_PUB))
    
    
#-----------------------------------------------------
# Setup routine
# -----------------------------------------------------
def setup():
    global mqttc, myprint
 
    print(progname + ": started: {}".format(time.strftime('%X')))   
    argu()                          # get commandline argumants
    
 # create class instances   
 
    path = os.path.dirname(os.path.realpath(__file__))    # current path
    logfile_name = path + "/demo_mqtt.log"
    print ("Name logfile: {} ".format(logfile_name) )
    
    myprint = MyPrint(  appname = progname, 
                    debug_level = debug,
                    logfile = logfile_name ) 
                        # Instanz von MyPrint Class erstellen
                                            # provide app_name and logfilename

    mqttc = MQTT_Conn ( debug = debug, 
                        path = path, 
                        client = progname, 
                        ipadr = mqtt_broker_ip_cmdline, 
                        retry = retry, 
                        conf = "/demo_mqtt_config.ini" )    # creat instance, of Class MQTT_Conn  
                        
#     check the status of the connection
    mqtt_connect, mqtt_error = mqttc.get_status()           # get connection status
    #  returns mqtt_error = 128 if not connected to broker
    if mqtt_connect == True:
        myprint.myprint (DEBUG_LEVEL0,  progname + ": connected to mqtt broker")
         # subscribe to MQTT topics   
        do_pub()                           # doing subscribe
    else:
        myprint.myprint (DEBUG_LEVEL0, progname + ": did NOT connect to mqtt broker, error: {}".format(mqtt_error))       
        # we are quitting if no connection
        # you could also try again later...
        myprint.myprint (DEBUG_LEVEL0, progname + ": serious mqtt error,quit")           
        sys.exit(2)
        

    mqttc.set_will ("test"," mein letzter wille....")

    myprint.myprint (DEBUG_LEVEL0,  progname + ": setup done")

     



#-----------------------------------------------------
# main body of program
# -----------------------------------------------------
def runit():
   
    try:
        
# here is the meat, meaning, whatever this program has to do it does it here
# in the main loop we have to call   mqttc.mqtt_start() once for every iteration
# other wise we can do what we want.
# in this example we simply incremant a counter. depending on the command we receive we incr one or the other
# if ordered to terminate wew raise a KeyboardInterrupt

#  ---- MAIN LOOP of program ---------------------------------
        myprint.myprint (DEBUG_LEVEL0,  "program loop: ")
#        print("Started: {}".format(time.strftime('%X')))
   
        while True:
            wt = wait_time
            err = publish_messages()
            if err > 0:
                wt = 10
                print ("could not publish, wait for {} secs. before trying again".format(wt))
                # or do something appropiate
            time.sleep(wt)
        
            



#   END OF MAIN LOOP -------------------------------------------------
        
    except KeyboardInterrupt:
        print ('^C received, terminating pgm_sub2')
        payload = "{:d}{:03d}{}".format (9,0, "demo_mqtt_pub terminates, bye bye")
        mqttc.publish (MQTT_TOPIC_SUB,payload)

    finally:
        print ("finally reached")
# Disconnect from MQTT_Broker
        mqttc.loop_stop()
        sys.exit(0)
#

#---------------------------------------------------
# Program starts here
#----------------------------------------------------
if __name__ == "__main__":
    from sys import argv
    setup()                     # do the setup

    runit()                     # run and publish
    
#   end of program
#    
    