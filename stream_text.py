import ggwave
from pydub import AudioSegment as seg
import numpy as np

def smartsplit(text):
    chunks = []
    current_chunk = ""
    # split the whole text by lines
    lines: list[str] = text.split("\n")
    for line in lines:
        words = line.split()
        for word in words:
            hypothesis = current_chunk + " " + word
            if len(hypothesis.encode("UTF-8")) >= 64:
                chunks.append(current_chunk)
                current_chunk = word
            else:
                current_chunk = hypothesis
        if current_chunk:  # if a line has words
            chunks.append(current_chunk)
            current_chunk = ""
    if current_chunk:  # if the last line has words
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