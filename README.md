# Data_over_sound
A python program for receiving and transmitting data over sound waves using only speaker and a microphone.
# Descryption
Imagine if you want to send a file or piece of data to another machine, but one of the computer's wifi, bluetooth and usb are broken but you both have a speaker and a microphone.
You open this app, select a piece of data that you want to send and it will generate series of tones from a speaker. The microphone of another machine listens this beeps and decodes the data back.
Voila! We have the data on the other computer!
#  How is that even possible!!!
As I know, the data is splitted into bytes and each byte have it's corresponding beep frequency and pitch.
When computer is told to beep the data, it beeps the bytes one by one via a speaker. and the microphone of another machine recognizes it.
Luckily i didn't make this app from scratch. the python library ggwave is provided by Georgy Gerganov.
https://github.com/ggerganov/ggwave
Thank him so much!
# Installation and building
```
pip install -r requirements.txt
```
You need to have visual c++ build tools if you're installing on windows.
To compile, just run compile.bat for windows.
If you're on another platform,
```
pyinstaller receiver.spec
```
It will not run in python 3.11 until the developer fixes ggwave.
