#!/bin/bash

#  setup switcher

echo "kopiere Files für mosquitto"

file="/etc/mosquitto/conf.d/my_mosquitto.conf"
if [ -f "$file" ]
then
	echo "$file bereits vorhanden, replace"
	cp -u my_mosquitto.conf /etc/mosquitto/conf.d
else
	echo "$file not found, also kopiere"
	cp -n -v my_mosquitto.conf /etc/mosquitto/conf.d
fi

rm -f mqtt_password.txt
file="/etc/mosquitto/my_mqtt_password.txt"
if [ -f "$file" ]
then
	echo "$file bereits vorhanden, ersetze"
	cp -u my_mqtt_password.txt /etc/mosquitto
else
	echo "$file not found, also kopiere"
	cp -n -v my_mqtt_password.txt /etc/mosquitto
fi

echo "Files fuer mosquitto gemacht"
echo " "




