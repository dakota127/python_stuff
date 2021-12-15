#!/bin/bash

#  setup switcher

echo "kopiere Files für mosquitto"

# User Config mosquitto ---------------
echo " "
echo "Kopiere Files für mosquitto"

file="/etc/mosquitto/conf.d/my_mosquitto.conf"
if [ -f "$file" ]
then
	echo "$file bereits vorhanden, remove"
	sudo rm -f $file
fi
echo "$file not found, copy"
sudo cp -n -v mosquitto_stuff/my_mosquitto.conf /etc/mosquitto/conf.d

# Password file   ---------------
sudo rm -f my_passw.txt
file="/etc/mosquitto/my_passw.txt"
if [ -f "$file" ]
then
	echo "$file bereits vorhanden, remove"
	sudo rm -f $file
fi

echo "$file not found, also kopiere"
sudo cp -n -v mosquitto_stuff/my_passw.txt /etc/mosquitto


# acl file   ---------------
sudo rm -f my_aclfile.txt
file="/etc/mosquitto/my_aclfile.txt"
if [ -f "$file" ]
then
	echo "$file bereits vorhanden, remove"
	sudo rm -f $file
fi

echo "$file not found, also kopiere"
sudo cp -n -v mosquitto_stuff/my_aclfile.txt /etc/mosquitto


# encrypt the passowrd file
echo "encrypt password file..."
sudo mosquitto_passwd -U /etc/mosquitto/my_passw.txt
echo "mosquitto logfile permissions"
sudo chmod 777 /var/log/mosquitto/mosquitto.log
echo "mosquitto user config done"
echo " "





