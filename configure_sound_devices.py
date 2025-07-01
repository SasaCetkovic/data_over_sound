from os.path import exists
import json
import numpy as np
import sounddevice as sd

devs = [-1, -1]
s = sd.query_devices()
start_idx = 0
samplerate = 48000
amplitude = 0.2
frequency = 440


def incallback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata


def sinecallback(outdata, frames, time, status):
    if status:
        print(status)
    global start_idx
    t = (start_idx + np.arange(frames)) / samplerate
    t = t.reshape(-1, 1)
    outdata[:] = amplitude * np.sin(2 * np.pi * frequency * t)
    start_idx += frames


def testoutput():
    global samplerate
    while True:
        for d in s:
            if d["max_output_channels"] == 0:
                continue
            samplerate = d["default_samplerate"]
            try:
                with sd.OutputStream(
                    device=d["index"],
                    channels=1,
                    callback=sinecallback,
                    samplerate=samplerate,
                ):
                    if "y" in input(
                        "this is "
                        + d["name"]
                        + " is playing sound. if you prefer this device, and you here the sound, type y, otherwise just press enter"
                    ):
                        return d["index"]
            except Exception as e:
                print("error openning ", d["name"], e)
                input("press enter")
            except KeyboardInterrupt:
                exit()
        input("no sounddevice selected. press enter to loop over")


def testinput():
    input(
        "now testing your microphone or other input device. after you press enter, we will go through all input devices and choose a device for you. while testing, you will hear your microphone or other device. if you don't hear it, just skip it. press enter to start"
    )
    global samplerate
    while True:
        for d in s:
            if d["max_input_channels"] == 0:
                continue
            samplerate = d["default_samplerate"]
            try:
                with sd.Stream(
                    device=(d["index"], devs[1]),
                    channels=1,
                    callback=incallback,
                    samplerate=samplerate,
                ):
                    if "y" in input(
                        "this is "
                        + d["name"]
                        + " is playing sound. if you prefer this device, and you here the sound, type y, otherwise just press enter"
                    ):
                        return d["index"]
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                print("error openning ", d["name"], e)
                input("press enter")
        input("no sounddevice selected. press enter to loop over")


def test():
    global devs
    devs[1] = testoutput()
    devs[0] = testinput()
    with open("devices.json", "w", encoding="UTF-8") as f:
        f.write(json.dumps(devs))


if not exists("devices.json"):
    test()
with open("devices.json", encoding="UTF-8") as f:
    devs = json.loads(f.read())
