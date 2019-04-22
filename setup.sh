#!/bin/bash
green='\E[32;40m'
white='\E[37;40m'
sudo apt update
sudo apt upgrade
sudo apt install build-essential cmake pkg-config
sudo apt install libjpeg-dev libtiff5-dev libjasper-dev
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt install libxvidcore-dev libx264-dev
sudo apt install libgtk2.0-dev
sudo apt install libatlas-base-dev gfortran
sudo apt install python2.7-dev python3-dev
cd ~
echo -e "${green}Downloading OpenCV 3.4.5${white}"
wget -O opencv.zip https://github.com/opencv/opencv/archive/3.4.5.zip
unzip opencv.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/ 3.4.5.zip
unzip opencv_contrib.zip
echo  -e "${green}Downloading Python pip${white}"
wget https://bootstrap.pypa.io/get-pip.py
echo -e "Are you using Python 2 or 3?"
select yn in "Python 2" "Python 3"; do
	case $yn in
		"Python 2" ) echo -e "${green}Installing pip, numpy, and NetworkTables for Python 2${white}"; sudo python get-pip.py; sudo pip install numpy; sudo pip install pynetworktables;  break;;
		"Python 3" ) echo -e "${green}Installing pip, numpy, and NetworkTables for Python 3${white}"; sudo python3 get-pip.py; sudo pip3 install numpy; sudo pip3 install pynetworktables; break;;
		* ) echo "Invalid answer choice";;
	esac
done

