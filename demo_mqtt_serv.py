#!/usr/bin/python
# coding: utf-8
# ***********************************************************
#
# This is program TREE of a suite of four programs to demonstrate and test
# MQTT functionality on a Raspberry Pi
# Runs with Python3   and not tested under Python2 
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
from sub.mymqtt import MQTT_Conn              # Class MQTT_Conn handles MQTT stuff
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

# Define Variables
MQTT_BROKER_IPADR = "127.0.0.1"         # default value, durch commandline parm zu ändern
MQTT_PORT = 1883
MQTT_KEEPALIVE_INTERVAL = 45
mqtt_broker_ip_cmdline = ""   # # ipc adr from commandline
broker_user_id = ""
broker_user_passwort = ""


MQTT_TOPIC_PUB =   "test"           # test
MQTT_TOPIC_SUB =   "test2"           # test2
MQTT_TOPIC_CMD =   "commands"
MQTT_TOPIC_CLIENT =   "from_client"           # test
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


progname = "demo_mqtt_serv"
logfile_name = "demo_mqtt.log"
configfile_name = "demo_config.ini"

number_messages = 0

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

        

  

# handle incoming messages with topic MQTT_TOPIC_SUB
#--------------------------------------
def handle_message_1 (client, userdata, message):

    inmsg = message.payload.decode()
    myprint.myprint (DEBUG_LEVEL1,  progname +  "message received: {}, userdata: {} ".format( inmsg, userdata))

    msg_numbr = inmsg[:4]
    response_topic= inmsg[4:15]
    messa = inmsg[19:]
  #  if msg_numbr == "0006":                    # testing
  #      msg_numbr = "0777"
    response_topic = "".join(response_topic.rstrip())
    myprint.myprint (DEBUG_LEVEL1,  progname +  "response_topic:{}, msg_numbr:{} , msg:{}".format( response_topic, msg_numbr,messa))

  #  time.sleep(0.5) 
    mqttc.publish_msg (response_topic , msg_numbr + messa)


        
# --- do subscribe and publish
# --- needs to be called after initial connection and after reconnect
#-------------------------------------------------------------       
def do_sub():        
# subscribe to MQTT topics   
    res = mqttc.subscribe_topic ("from_client", handle_message_1)     # subscribe to topic
    if (res > 0):
   
        myprint.myprint (DEBUG_LEVEL0, progname +  ": subscribe returns errorcode: {}".format(res)) 
        myprint.myprint (DEBUG_LEVEL0, progname +  ": terminating")       
        sys.exit(2)
    myprint.myprint (DEBUG_LEVEL0,  progname +  ": subscribed to topic: {} ".format(MQTT_TOPIC_PUB))
    
    
#-----------------------------------------------------
# Setup routine
# -----------------------------------------------------
def setup():
    global mqttc, myprint , MQTT_BROKER_IPADR, mqtt_broker_ip_cmdline, broker_user_id, broker_user_passwort
 
    print(progname + ": started: {}".format(time.strftime('%X')))   
    argu()                          # get commandline argumants
    
 # create class instances   
 
    path = os.path.dirname(os.path.realpath(__file__))    # current path
    print ("Name logfile: {} ".format( path + "/" + logfile_name) )
    print ("Name configfile: {} ".format( path + "/" + configfile_name) ) 
     
# create Instance of MyPrint Class 
    myprint = MyPrint(  appname = progname, 
                    debug_level = debug,
                    logfile =  path + "/" + logfile_name ) 
  

# Broker IP Adresse bestimmen
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
    # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IPAdr_this_machine = s.getsockname()[0]
    except:
        IPAdr_this_machine = '127.0.0.1'
    finally:
        s.close()
        print("IPAdr this machine:{}".format(IPAdr_this_machine))


    # falls eine Ipadr auf der commandline gegeben wird, nehme diese
    if len (mqtt_broker_ip_cmdline) >0 :

        MQTT_BROKER_IPADR = mqtt_broker_ip_cmdline
        

    print ("MQTT Server, using IP_ADR:{} and Port:{}".format(MQTT_BROKER_IPADR, MQTT_PORT))

 # create Instance of MQTT-Conn Class  
    mqttc = MQTT_Conn ( debug = debug, 
                        path = path, 
                        client = progname, 
                        ipadr = mqtt_broker_ip_cmdline, 
                        retry = retry, 
                        conf = path + "/" + configfile_name)    # creat instance, of Class MQTT_Conn  
    
 # set will and testament - this needs to done BEFORE a connect !!     
    mqttc.set_will (MQTT_TOPIC_PUB," the publisher unexpectedly died... my condolences.")                       
#     check the status of the connection
    mqtt_connect, mqtt_error = mqttc.get_status()           # get connection status
    #  returns mqtt_error = 128 if not connected to broker
    if mqtt_connect == True:
        myprint.myprint (DEBUG_LEVEL0,  progname + ": connected to mqtt broker")
         # subscribe to MQTT topics   
        do_sub()                           # doing subscribe
    else:
        myprint.myprint (DEBUG_LEVEL0, progname + ": did NOT connect to mqtt broker, error: {}".format(mqtt_error))       
        # we are quitting if no connection
        # you could also try again later...
        myprint.myprint (DEBUG_LEVEL0, progname + ": serious mqtt error,quit")           
        sys.exit(2)
        

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
            print ("serverloop")
            time.sleep(4)
        
            



#   END OF MAIN LOOP -------------------------------------------------
        
    except KeyboardInterrupt:
        print ('^C received, terminating server')
        
    except Exception:
        #       etwas schlimmes ist passiert, wir loggen dies mit Methode myprint_exc der MyPrint Klasse
        myprint.myprint_exc ("Etwas Schlimmes ist passiert.... !")
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
    