import configure_sound_devices
from time import sleep, time
from queue import Queue
import numpy as np
import ggwave
import sounddevice as sd

# import json
ggwave.disableLog()

rate = 48000
ch = 1
frames = 1024
slp = 0.5


class GW:
    def __init__(self, callback_function, **kwargs):
        self.q = Queue()
        self.sendqueue = Queue()
        self.callback_function = callback_function
        self.protocol = 2
        self.pars = ggwave.getDefaultParameters()
        for k, v in kwargs.items():
            self.pars[k] = v
        self.instance = ggwave.init(self.pars)
        self.stream = sd.Stream(
            samplerate=rate,
            blocksize=frames,
            dtype="float32",
            channels=ch,
            callback=self.callback,
            device=configure_sound_devices.devs,
        )
        self.started = False
        self.start()
        self.stopcondition = False

    def callback(self, indata, outdata, frames, time, status):
        if self.stopcondition:
            self.stopcondition = False
        # if there is data to send, don't receive from the microphone
        if not self.sendqueue.empty():
            q = self.sendqueue.get()
            outdata[:] = q.reshape(outdata.shape)
            return
        outdata[:] = 0  # if there is no data to send, send zeros
        res = ggwave.decode(self.instance, bytes(indata))
        if res is not None:
            res = try_to_utf8(res)
            self.q.put(res)
            self.callback_function(res)

    def start(self):
        if self.started:
            return
        self.started = True
        self.stream.start()

    def stop(self):
        if not self.started:
            return
        self.started = False
        self.stream.stop()

    def send(self, data):
        wf = np.frombuffer(
            ggwave.encode(data, protocolId=self.protocol, instance=self.instance),
            dtype="float32",
        )
        # put the data in the queue but framesize by framesize
        for i in range(0, len(wf), frames):
            self.sendqueue.put(wf[i : i + frames])

    def switchinstance(self, leng=-1):
        # switch instance to another protocol
        ggwave.free(self.instance)
        if leng is not None:
            self.pars["payloadLength"] = leng
        self.instance = ggwave.init(self.pars)

    def __del__(self):
        ggwave.free(self.instance)


def try_to_utf8(val):
    # try to decode bytes to utf-8
    try:
        return val.decode("UTF-8").replace("\x00", "")
    except:
        return val  # if it fails return the original value
