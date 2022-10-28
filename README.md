# data_over_sound
a python program for receiving and transmitting data over sound waves using only speaker and a microphone.
# discryption
emagine if you want to send a file or piece of data to another machine, but one of the computer's wifi, bluetooth and usb are broken but you both have a speaker and a microphone.
you open this app, select a piece of data that you want to send and it will generate series of tones from a speaker. the microphone of another machine listens this beeps and decodes the data back.
hurray! we have the data on the other computer!
#  how is that even possible!!!
as i know, the data is splitted into bytes and each byte have it's corrisponding beep frequency and pitch.
when computer is told to beep the data, it beeps the bytes one by one via a speaker. and the microphone of another machine recognizes it.
luckily i didn't make this app from scratch. the python library ggwave is provided by Georgy Gerganov.
https://github.com/ggerganov/ggwave
thank him so much!
# installation and building
pip install -r requirements.txt
you need to have visual c++ build tools if you're installing on windows.
to compile, just run compile.bat for windows.
if you're on another platform,
```
pyinstaller receiver.spec
```
