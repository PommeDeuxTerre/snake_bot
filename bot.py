import websocket, re

def play(ws):
    while True:
        res = ws.recv()
        if (res=="2"):
            print("check ping")
            ws.send("3")
        elif (re.search('onEnd', res)):
            print("game finished")
            return
        elif (re.search('updateSnakes', res)):
            print("snake update")
        else:
            print(f"undefined res: {res}")

