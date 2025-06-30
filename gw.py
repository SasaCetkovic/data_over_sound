import configure_sound_devices
from time import sleep, time
from queue import Queue
import numpy as np
import ggwave
import sounddevice as sd
import base64

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
        # For variable-length protocols, payloadLength should be 0.
        self.pars['payloadLength'] = 0
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
            # The ggwave library returns a null-terminated payload. The Python
            # wrapper includes this null byte, so we strip it.
            if res.endswith(b'\x00'):
                res = res[:-1]
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

    def send_many(self, data_list):
        full_waveform = bytearray()
        for data in data_list:
            # ggwave.encode seems to require a string.
            # Control messages (headers/footers) are sent as is (decoded as utf-8).
            # Data chunks are base64-encoded to ensure they are valid strings
            # and to prevent corruption of binary data.
            if data.startswith((b'$$$$', b'FEND', b'TEND')):
                payload = data.decode('utf-8')
            else:
                payload = base64.b64encode(data).decode('ascii')

            full_waveform.extend(
                ggwave.encode(payload, protocolId=self.protocol, instance=self.instance)
            )
        
        wf = np.frombuffer(full_waveform, dtype="float32")
        
        for i in range(0, len(wf), frames):
            self.sendqueue.put(wf[i : i + frames])

    def switchinstance(self, leng=-1):
        # switch instance to another protocol
        ggwave.free(self.instance)
        if leng is not None:
            if leng == -1:
                self.pars['payloadLength'] = 0
            else:
                self.pars["payloadLength"] = leng
        self.instance = ggwave.init(self.pars)

    def get_max_payload_size(self):
        pl = self.pars.get("payloadLength", 0)
        if pl == 0:
            return 140
        return pl

    def __del__(self):
        ggwave.free(self.instance)


