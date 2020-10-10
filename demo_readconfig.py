#!/usr/bin/python
# coding: utf-8
# ***********************************************************
# 	Demo program using the configread Class
# 	Designed and written by Peter K. Boxler, Februar 2015  
# 
#   Used to read .ini type configfiles
#
#	Commandline Parameter
#	see function argu()
#
#  Note: in case the specified configfile does not exist the existing key-value pairs remain as defined

#   Tested under Python3  Sept 2020 
#   Enhanced Sept 2020
# ***** Imports ******************************
import sys, getopt, os
import time
from time import sleep
import datetime
import argparse

from sub.myprint import MyPrint              # Class MyPrint replace print, debug output
from sub.configread import ConfigRead


# ***** Variables *****************************
# Configdictionary
# Python dictionary for config values
# key-value pairs
# values are default values, the will not be changed if key not found in configfile 
configval={
        "url"           : "defaulturl", 
        "username"      : "usernamedefault", 
        "password"      : "passworddefault",
        "abc"           : "default",
        "timeout"       : 123,
        "xmlfile_prefix" : "g1",
        "setup_mqtt"    : 8,
        "termination"   : "yes",
        }



config_filename = "demo_readconfig.ini"      # name of config file (in current dir)
config_section = "peter"

DEBUG_LEVEL0=0
DEBUG_LEVEL1=1
DEBUG_LEVEL2=2
DEBUG_LEVEL3=3
debug=0
#
progname = "demo_readconfig.py"

# ***** Function Parse commandline arguments ***********************
#----------------------------------------------------------
# get and parse commandline args
def argu():
    global debug

    parser = argparse.ArgumentParser()

    parser.add_argument("-d", help="kleiner debug", action='store_true')
    parser.add_argument("-D", help="grosser debug", action='store_true')
    parser.add_argument("-A", help="ganz grosser debug", action='store_true')

    args = parser.parse_args()
    if args.d:
        debug=DEBUG_LEVEL1
    if args.D: 
        debug=DEBUG_LEVEL2
    if args.A: 
        debug=DEBUG_LEVEL3
                 
    return(args)
    



# *************************************************
# Program starts here
# *************************************************

if __name__ == '__main__':
#
    print ( "Start program: " + progname)
    options=argu()                          # get commandline args
     #   get the current path 
    path = os.path.dirname(os.path.realpath(__file__))    # current path
    logfile_name = path + "/configtest.log"
    
    print ("Name logfile: {} ".format(logfile_name) )

    mypri=MyPrint(  appname = progname, 
                    debug_level = debug,
                    logfile = logfile_name ) 
                        # Instanz von MyPrint Class erstellen
                                            # provide app_name and logfilename

    config = ConfigRead(debug_level = debug)     # Create Instance of the ConfigRead Class

    print ("\nConfigdictionary before reading:")
    for x in configval:
        print ("{} : {}".format (x, configval[x]))


    ret=config.config_read (path+"/"+config_filename ,config_section, configval)  # call method config_read()
    mypri.myprint (DEBUG_LEVEL1,  "config_read() returnvalue: {}".format (ret))	# für log und debug
 
    print ("\nConfigdictionary after reading:")
    for x in configval:
        print ("{} : {}".format (x, configval[x]))
         
    if ret > 0 :
        sys.exit(2)
 


#  Abschlussvearbeitung
    print ("\nProgram terminated....")
    sys.exit(0)
#**************************************************************
#  That is the end
#***************************************************************
#