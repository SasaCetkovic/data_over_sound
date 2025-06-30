import gw
import parse
from webbrowser import open as wopen
import os
from sys import exit  # stupid pyinstaller bug, it doesn't work without this line
import chunker
import math
import base64

class Output:
    def __init__(self):
        self.data = ""
        self.receiving_file = False
        self.file_chunks = []
        self.file_name = ""
        self.file_size = 0
        self.receiving_text = False
        self.text_chunks = []
        self.text_size = 0

    def data_callback(self, data):
        if not isinstance(data, bytes):
            return

        # If we are in a transfer, the data must be a chunk (base64) or a footer (cleartext).
        if self.receiving_file:
            if data == b'FEND$$$$':
                if not self.receiving_file:
                    return # ignore stray FEND
                print("File transfer finished.")
                self.receiving_file = False
                match chunker.dechunk(self.file_chunks):
                    case chunker.Result.Ok(file_data):
                        # check if recs directory exists
                        if not os.path.exists("recs"):
                            os.makedirs("recs")
                        filepath = os.path.join("recs", os.path.basename(self.file_name))
                        with open(filepath, "wb") as f:
                            f.write(file_data)
                        print(f"File saved to {filepath}")
                    case chunker.Result.Err(failed):
                        print(f"File reconstruction failed. Missing chunks: {failed}")
                self.file_chunks = []
                return
            
            try:
                decoded_data = base64.b64decode(data)
                self.file_chunks.append(decoded_data)
                num_chunks = int.from_bytes(decoded_data[2:4], 'big')
                chunk_idx = int.from_bytes(decoded_data[0:2], 'big')
                print(f"Received chunk {chunk_idx + 1}/{num_chunks}")
            except (IndexError, ValueError, base64.binascii.Error):
                print("Received malformed file chunk.")
            return

        if self.receiving_text:
            if data == b'TEND$$$$':
                if not self.receiving_text:
                    return # ignore stray TEND
                print("Text transfer finished.")
                self.receiving_text = False
                match chunker.dechunk(self.text_chunks):
                    case chunker.Result.Ok(text_data):
                        print("Received text:")
                        print(text_data.decode('utf-8', errors='ignore'))
                    case chunker.Result.Err(failed):
                        print(f"Text reconstruction failed. Missing chunks: {failed}")
                self.text_chunks = []
                return

            try:
                decoded_data = base64.b64decode(data)
                self.text_chunks.append(decoded_data)
                num_chunks = int.from_bytes(decoded_data[2:4], 'big')
                chunk_idx = int.from_bytes(decoded_data[0:2], 'big')
                print(f"Received text chunk {chunk_idx + 1}/{num_chunks}")
            except (IndexError, ValueError, base64.binascii.Error):
                print("Received malformed text chunk.")
            return

        # Not in a transfer. Could be a header (base64) or a simple message.
        try:
            decoded_data = base64.b64decode(data)

            if decoded_data.startswith(b'$$$$FILE'):
                self.receiving_file = True
                self.file_chunks = []
                try:
                    self.file_size = int.from_bytes(decoded_data[8:12], 'big')
                    self.file_name = decoded_data[12:].decode("utf-8")
                    print(f"Receiving file: {self.file_name} ({self.file_size} bytes)")
                except Exception as e:
                    print(f"Error parsing file header: {e}")
                    self.receiving_file = False
                return

            if decoded_data.startswith(b'$$$$TEXT'):
                self.receiving_text = True
                self.text_chunks = []
                try:
                    self.text_size = int.from_bytes(decoded_data[8:12], 'big')
                    print(f"Receiving text ({self.text_size} bytes)")
                except Exception as e:
                    print(f"Error parsing text header: {e}")
                    self.receiving_text = False
                return
            
            # It was base64, but not a header. Treat as a simple message.
            data = decoded_data
            
        except base64.binascii.Error:
            # Not base64, so it's a simple message.
            pass

        # Handle as a simple message
        try:
            decoded_text = data.decode('utf-8').replace("\x00", "")
            self.data = decoded_text
            print(decoded_text)
        except (UnicodeDecodeError, AttributeError):
            # This can happen with noise or corrupted data.
            # The original code did str(data), which would show b'...'.
            # We'll just ignore it to keep the output clean.
            self.data = ""

    def parse(self):
        return parse.extract_info(self.data)

output = Output()
g=gw.GW(output.data_callback)
g.start()

help = """
/p [protocol number] [payload length] - set protocol and payload length. payload length is optional and must be between 5 and 64. It is only required for protocols 9 to 11 but can be set for all protocols
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
        # ggwave has a limit of ~140 bytes per message
        max_payload = g.get_max_payload_size()
        if len(cmd.encode('utf-8')) > max_payload:
            print("Message is too long, sending as chunked text...")
            # chunk header is 4 bytes (idx + num_chunks).
            # Data chunks are base64 encoded, which adds ~33% overhead.
            # We adjust the chunk size to fit within the max_payload.
            chunk_size = (max_payload * 3 // 4) - 4
            if chunk_size <= 0:
                return "Payload size too small to chunk message."
            try:
                chunks = list(chunker.chunk_text(cmd, chunk_size, max_payload))
                g.send_many(chunks)
                return "Long message queued for sending."
            except ValueError as e:
                return str(e)
        else:
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
                    if int(c[2])<5 or int(c[2])>64:
                        return ("invalid payload length. it must be between 5 and 64")
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
                max_payload = g.get_max_payload_size()
                # chunk header is 4 bytes (idx + num_chunks).
                # Data chunks are base64 encoded, which adds ~33% overhead.
                # We adjust the chunk size to fit within the max_payload.
                chunk_size = (max_payload * 3 // 4) - 4
                if chunk_size <= 0:
                    return "Payload size too small to chunk file."
                print(f"Sending file {filepath}...")
                try:
                    chunks = list(chunker.chunk(filepath, chunk_size, max_payload=max_payload))
                    g.send_many(chunks)
                    return f"File {filepath} queued for sending."
                except ValueError as e:
                    return str(e)

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
