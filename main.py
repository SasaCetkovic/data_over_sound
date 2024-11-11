import gw

def data_callback(data):
    print(data)

g=gw.GW(data_callback)
g.start()

help = """
/p [protocol number] [payload length] - set protocol and payload length. payload length is optional and must be between 4 and 64. It is only required for protocols 9 to 11 but can be set for all protocols
/reset - reset the instance. If data starts to get corrupted, this command can be used to reset the instance
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
            case "/stop":
                g.stopcondition=True
            case "/exit":
                g.stop()
                exit()
            case "/device":
                gw.configure_sound_devices.test()
                input("!Program must be restarted. Press enter to exit")
                exit()
            case "/help":
                return help
            case "/sendhelp":
                for i in help.split("\n"):
                    g.send(i)
                return "sending"
    except Exception as e:
        return (e)

while True:
    cmd=input(">")
    print(command(cmd))