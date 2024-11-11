import ggwave
from pydub import AudioSegment as seg
import numpy as np

def smartsplit(text):
    # each chunk can be at most 64 bytes
    chunks = []
    current_chunk = ""
    sep_idx = -1  # what if the accumulated text is too long, we need to quickly remember the last separator
    space_idx = -1  # space is the last resort if no way to split
    for i, char in enumerate(text):
        if char in [",", ";", ".", "!", "?"]:
            sep_idx = i
        if char == " ":
            space_idx = i
        if char == "\n":
            chunks.append(current_chunk)
            current_chunk = ""
            space_idx = -1
            sep_idx = -1
        # 64 bytes, not 64 characters
        if len(current_chunk.encode("utf-8")) >= 64:
            if sep_idx > -1:  # if we have a separator, split there
                chunks.append(current_chunk[:sep_idx])
                current_chunk = current_chunk[sep_idx:].lstrip()  # dont care about the space
                sep_idx = -1
                space_idx = -1  # we fresh start from the new chunk
            elif space_idx != -1:
                chunks.append(current_chunk[:space_idx])
                current_chunk = current_chunk[space_idx:]
                sep_idx = -1
                space_idx = -1
            else:  # ok, lets corrupt the data
                chunks.append(current_chunk)
                current_chunk = ""

        current_chunk += char
    chunks.append(current_chunk)
    return chunks

def make_wave(text, *args, **kwargs):  # args and kwargs are passed to ggwave.encode
    chunks = smartsplit(text)
    pause = seg.silent(duration=1000)
    wave = seg.empty()
    first = True
    for chunk in chunks:
        data = np.frombuffer(ggwave.encode(chunk, *args, **kwargs), dtype=np.float32)
        data = (data * 32767).astype(np.int16)  # this worked for me
        s = seg(data.tobytes(), frame_rate=48000, sample_width=2, channels=1)
        if first:
            first = False
        else:
            wave += pause
        wave += s
    return wave

def make_wave_from_file(file, *args, **kwargs):
    with open(file, "r") as f:
        text = f.read()
    return make_wave(text, *args, **kwargs)


if __name__ == "__main__":
    wave = make_wave_from_file("files/helloworld.txt", 2)  # protocol 2 is middle frequency fastest dual tone
    wave.export("output.wav", format="wav")
    print("Done.")