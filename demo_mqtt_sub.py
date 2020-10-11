#!/usr/bin/python
# coding: utf-8
# ***********************************************************
#
# This is program ONE of a suite of two programs to demonstrate and test
# MQTT functionality on a Raspberry Pi
# Runs with Python3   and not tested under Python2 (it should run, however)
# 
# This version of the program uses the  MQTT_Conn class tha encapsulates MQTT

# enhanced by Peter (Sept 2020)
# *********************************************************

import paho.mqtt.client as mqtt
import argparse, os, sys
import time
from sub.myprint import MyPrint             # Class MyPrint replace print, debug output
from sub.mqtt import MQTT_Conn              # Class MQTT_Conn handles MQTT stuff

# Define Variables

DEBUG_LEVEL0=0
DEBUG_LEVEL1=1
DEBUG_LEVEL2=2
DEBUG_LEVEL3=3
debug=0
terminate = False
what_to_do = 1                  # action 1
MQTT_TOPIC_PUB =   "test2"
MQTT_TOPIC_SUB =   "test"
MQTT_TOPIC_CMD =   "commands"
mqtt_broker_ip_cmdline = ""     # ipc adr from commandline
mqtt_connect = False
mqtt_error = 0
# instances of classes
myprint = 0
mqttc=0
wait_time = 10
retry = False                   # do not retry on connect to brokaer
progname = "pgm_sub2: "

# ***** Function Parse commandline arguments ***********************
#----------------------------------------------------------
# get and parse commandline args
def argu():
    global debug, mqtt_broker_ip_cmdline, retry

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="small debug", action='store_true')
    parser.add_argument("-D", help="medium debug", action='store_true')
    parser.add_argument("-A", help="details debug", action='store_true')
    parser.add_argument("-r", help="retry indicator", action='store_true')
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
    if args.i: 
       mqtt_broker_ip_cmdline = args.i
 
    return(args)
#----------------------------------------------------------
      


# handle incoming messages with topic MQTT_TOPIC_SUB
# program2 send messages in format nnntext (first three bytes numeric)
#--------------------------------------
def handle_message_1 (client,userdata ,message):
    print ("message received: {}, userdata: {} ".format( message.payload.decode(), userdata))
    msgident = message.payload.decode()[0:1]           #   test  first byte of message, must be numeric
    if msgident.isnumeric() == True :
        if int (msgident) == 8:     # check identifier in message                 
            print ("last msg of current sequence received, sending thank you message\n\n")
            payload = "{:d}{:03d}{}".format (8,0, "thanks") # publish ack on topic test2

            mqtt_error = mqttc.publish_msg (MQTT_TOPIC_PUB, payload)
            if (mqtt_error > 0):
                myprint.myprint (DEBUG_LEVEL0,  "publish returns: {} ".format(mqtt_error))

    else:
        print ("invalid msg first byte not numeric\n\n")
        
# handle incoming messages with MQTT_TOPIC_CMD
#--------------------------------------
def handle_message_2 (client,userdata, message):
    global what_to_do, terminate
    print ("command received: {}". format(message.payload.decode()))
    
    if ("this" in message.payload.decode()):
        what_to_do = 1
    if ("that" in message.payload.decode()):
        what_to_do = 2
    print ("what to do: {}: ".format(what_to_do))
    
    if ("halt" in message.payload.decode()):
        print ("terminate received")
        terminate = True
        
       
# --- do subscribe and publish
# --- needs to be called after initial connection and after reconnect
#-------------------------------------------------------------       
def do_pub():
    res = mqttc.subscribe_topic (MQTT_TOPIC_SUB , handle_message_1)     # subscribe to topic
    if (res > 0):
        myprint.myprint (DEBUG_LEVEL0, progname +  "subscribe returns errorcode: {}".format(res)) 
        myprint.myprint (DEBUG_LEVEL0, progname +  "terminating")       
        sys.exit(2)                     # cannot proceed
    myprint.myprint (DEBUG_LEVEL0,  "subscribed to topic: {} ".format(MQTT_TOPIC_SUB))
    
    res = mqttc.subscribe_topic (MQTT_TOPIC_CMD , handle_message_2)     # subscribe to topic
    if (res > 0):
        myprint.myprint (DEBUG_LEVEL0, progname +  "subscribe returns errorcode: {}".format(res)) 
        myprint.myprint (DEBUG_LEVEL0, progname +  "terminating")       
        sys.exit(2)                     # cannot proceed

        
#-----------------------------------------------------
# Setup routine
# -----------------------------------------------------
def setup():
    global mqttc, myprint, mqtt_connect
    
    print(progname + "started: {}".format(time.strftime('%X')))   
    argu()                          # get commandline argumants
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
                        conf = "/demo_config.ini" )    # creat instance, of Class MQTT_Conn  

    mqtt_connect, mqtt_error = mqttc.get_status()           # get connection status
    #  returns mqtt_error = 128 if not connected to broker
    if mqtt_connect == True:
        myprint.myprint (DEBUG_LEVEL0,  progname + "connected to mqtt broker")
         # subscribe to MQTT topics   
        do_pub()                           # doing subscribe
    else:
        myprint.myprint (DEBUG_LEVEL0, progname + "did NOT connect to mqtt broker, error: {}".format(mqtt_error))       
        # we are quitting if no connection
        # you could also try again later...
        myprint.myprint (DEBUG_LEVEL0, progname + "serious mqtt error,quit")           
        sys.exit(2)
        
    myprint.myprint (DEBUG_LEVEL0,  progname + "setup done")

    return()

#-----------------------------------------------------
# main body of program
# -----------------------------------------------------
def runit():
    global   mqtt_connect
    counter1 = 0
    counter2 = 0
    try:
        
# here is the meat, meaning, whatever this program has to do it does it here
# in the main loop we have to call   mqttc.mqtt_start() once for every iteration
# other wise we can do what we want.
# in this example we simply incremant a counter. depending on the command we receive we incr one or the other
# if ordered to terminate wew raise a KeyboardInterrupt

        while True:
#  ---- MAIN LOOP of program ---------------------------------
            while( mqtt_connect == True)  :       
                if (what_to_do == 1):
                    counter1 = counter1 + 1
                if (what_to_do == 2):
                    counter2 = counter2 + 1           
                time.sleep(1)
                mqtt_connect, mqtt_error  = mqttc.get_status()
                myprint.myprint (DEBUG_LEVEL0,  "program loop: {} / {}". format(counter1, counter2))
                if (terminate == True): raise KeyboardInterrupt
                
            while (mqtt_connect == False):   
                myprint.myprint (DEBUG_LEVEL0 ,"no connection, we are going to wait for {} seconds". format(wait_time))
                time.sleep(wait_time)
                
                
                mqtt_connect, mqtt_error = mqttc.get_status()
                myprint.myprint (DEBUG_LEVEL2 ,"nach get_status(), mqtt_connect: {}/{}".format(mqtt_connect, mqtt_error))
                
                if (mqtt_connect == True):
                    time.sleep(2)
                    pub_sub()           # we have reconnect, do pub and sub again
                pass
            myprint.myprint (DEBUG_LEVEL2 ," end of big while")
        pass           
            

#   END OF MAIN LOOP -------------------------------------------------
        
    except KeyboardInterrupt:
	    print ('^C received, shutting down pgm_sub2')

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
    setup()
    runit()
    
    