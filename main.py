import gw
import parse
from webbrowser import open as wopen
import os
from sys import exit  # stupid pyinstaller bug, it doesn't work without this line
import chunker

class Output:
    def __init__(self):
        self.data = ""
        self.receiving_file = False
        self.file_chunks = []
        self.file_name = ""
        self.file_size = 0

    def data_callback(self, data):
        if isinstance(data, bytes):
            if data.startswith(b'$$$$FILE'):
                self.receiving_file = True
                self.file_chunks = []
                try:
                    self.file_size = int.from_bytes(data[8:12], 'big')
                    self.file_name = data[12:].decode("utf-8")
                    print(f"Receiving file: {self.file_name} ({self.file_size} bytes)")
                except Exception as e:
                    print(f"Error parsing file header: {e}")
                    self.receiving_file = False
                return

            if data.startswith(b'FEND$$$$'):
                if not self.receiving_file:
                    return # ignore stray FEND
                print("File transfer finished.")
                self.receiving_file = False
                
                match chunker.dechunk(self.file_chunks):
                    case chunker.Result.Ok(file_data):
                        # check if recs directory exists
                        if not os.path.exists("recs"):
                            os.makedirs("recs")
                        filepath = os.path.join("recs", self.file_name)
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        print(f"File saved to {filepath}")
                    case chunker.Result.Err(failed):
                        print(f"File reconstruction failed. Missing chunks: {failed}")
                self.file_chunks = []
                return

            if self.receiving_file:
                self.file_chunks.append(data)
                try:
                    num_chunks = int.from_bytes(data[2:4], 'big')
                    chunk_idx = int.from_bytes(data[0:2], 'big')
                    print(f"Received chunk {chunk_idx + 1}/{num_chunks}")
                except (IndexError, ValueError):
                    print("Received malformed chunk.")
                return

        # If not file data, treat as regular message
        self.data = str(data)
        print(self.data)

    def parse(self):
        return parse.extract_info(self.data)

output = Output()
g=gw.GW(output.data_callback)
g.start()

help = """
/p [protocol number] [payload length] - set protocol and payload length. payload length is optional and must be between 4 and 64. It is only required for protocols 9 to 11 but can be set for all protocols
/reset - reset the instance. If data starts to get corrupted, this command can be used to reset the instance
/open - open URLs, emails, and phone numbers in the default web browser, email client, and phone dialer respectively. Use this command if a url, email, or phone number is received. Use it on your own risk, as it may open malicious websites
/sendfile <path> - send a file
/stop - stop the program (not working properly, use ctrl+c instead)
/exit - exit the program
/device - test sound devices
/help - display this message
/sendhelp - sends each line of this message as a separate message via sound
"""


def command(cmd):
    if not cmd.startswith("/"):
        g.send(cmd)
        return "sending"
    c=cmd.split(" ")
    try:
        match c[0]:
            case "/p":
                if int(c[1])<0 or int(c[1])>11:  # there are 4 protocols, each with 3 sending speeds
                    return ("specify protocol between 0 and 11")
                g.protocol=int(c[1])
                toreturn=f"protocol set to {str(g.protocol)}. "
                if len(c)>2:  # if there is a payload length
                    if c[2]=="-":  # if the payload length is set to default
                        g.switchinstance(-1)
                        return toreturn
                    if int(c[2])<4 or int(c[2])>64:
                        return ("invalid payload length. it must be between 4 and 64")
                    g.switchinstance(int(c[2]))
                    return toreturn+(" payload length "+str(c[2]))
                else:  # if there is no payload length
                    if int(c[1])>8:
                        return ("protocols 9 to 11 needs a payload length. specify a length after the protocol number")
                    g.switchinstance(-1)
                    return toreturn
            case "/reset":  # if data starts to get corrupted, this command can be used to reset the instance
                g.switchinstance(-1)
                return ("instance reset")
            case "/open":
                result = output.parse()
                for url in result["urls"]:
                    wopen(url)
                for email in result["emails"]:
                    wopen("mailto:"+email)
                for phone in result["phones"]:
                    wopen("tel:"+phone)
                return "opening"

            case "/sendfile":
                if len(c) < 2:
                    return "Usage: /sendfile <path>"
                filepath = " ".join(c[1:])
                if not os.path.exists(filepath):
                    return f"File not found: {filepath}"
                chunk_size = 128
                print(f"Sending file {filepath}...")
                for chunk in chunker.chunk(filepath, chunk_size):
                    g.send(chunk)
                return f"File {filepath} queued for sending."

            case "/stop":
                g.stopcondition=True
            case "/exit":
                g.stop()
                exit()
            case "/device":
                os.remove("devices.json")
                input("!Press enter and restart the program. It will start with the device test prompt.")
                g.stop()
                exit()
            case "/help":
                return help
            case "/sendhelp":
                for i in help.split("\n"):
                    g.send(i)
                return "sending"
    except Exception as e:
        return (e)

try:
    print("Welcome to data_over_sound")
    print("Type /help for help")
    print("enter your message or command:")
    while True:
        cmd=input()  # don't show > prompt because it prints something else in another thread
        print(command(cmd))
except (KeyboardInterrupt, EOFError):
    g.stop()
    exit()
