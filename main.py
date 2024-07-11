import requests
import websocket
import json
import re
from bot import play
import time
import threading

POMME_DES_TERRES = 0
POMME_JEDUSOR = 1
POMME_ELVIS_JEDUSOR = 2
TEST = 3

URL = "snake-online-54f289ce69bf.herokuapp.com"

def get_sid(session):
    url = f"https://{URL}/socket.io/?EIO=4&transport=polling&t=Or6DQd9"
    r = session.get(url)

    try:sid = json.loads(r.text[1:])["sid"]
    except:raise Exception("echec de la réception du sid")
    
    return sid

def init_ws(session, sid):
    url=f"wss://{URL}/socket.io/?EIO=4&transport=websocket&sid={sid}"

    ws = websocket.WebSocket()
    ws.connect(url)
    return ws

def connect(session, sid, ws, username):
    r = session.post(f"https://{URL}/socket.io/?EIO=4&transport=polling&t=Or6DQfM&sid={sid}",
           data='40')
    print(f"sent 40: {r.status_code}")

    ws.send('2probe')
    print(f"sent '2probe': {ws.status}")
    print(f"recieve {ws.recv()}: {ws.status}")

    r = session.post(f"https://{URL}/socket.io/?EIO=4&transport=polling&t=Or6DQfM&sid={sid}",
           data=f'420["name","{username}"]')
    print(f"sent username: {r.status_code}")

    ws.send('5')
    print(f"sent '5': {ws.status}")
    ws.recv()
    ws.recv()
    ws.recv()

def create_room(ws):
    ws.send('42["createRoom"]')
    print(f"send '42[\"createRoom\"]': {ws.status}")
    ws.recv()

def wait_room(ws, bot_id, bot_name, bot_number):
    global bots
    while True:
        res = ws.recv()
        if (res=="2"):
            #print("check ping")
            ws.send("3")
        elif (re.search("addClientRoom", res)):
            print("lancement de la partie")
            ws.send('42["playRoom"]')
            bots.append([bot_name, bot_id, bot_number+1])
            play(ws, bot_id)
            ws.close()
            return True
        elif (re.search("removeClientRoom", res)):
            print("orther player quit")
            nb_players-=1
        else:
            print(f"undefined res: {res}")

def launch_bot(bot_name, bot_id, bot_number):
    while True:
        s = requests.Session()

        sid = get_sid(s)

        ws = init_ws(s, sid)

        connect(s, sid, ws, bot_name+str(bot_number%10))

        create_room(ws)

        res = False
        try:
            res = wait_room(ws, bot_id, bot_name, bot_number)
        except Exception as e:
            print(f"{time.ctime()}: \n{e}")
        
        #check if the game is finished or if it has crashed
        if res:return


        ws.close()

def main():
    global bots
    current_bots = []
    bots = [
        ["Pomme Des Terres", POMME_DES_TERRES, 1],
        ["Pomme Jedsuor", POMME_JEDUSOR, 1],
        ["Pomme Elvis Jedsuor", POMME_ELVIS_JEDUSOR, 1]
    ]
    for bot in bots:
        current_bots.append(threading.Thread(target=launch_bot, args=(bot[0], bot[1], bot[2])))
        current_bots[-1].start()
    bots = []
    while True:
        time.sleep(5)
        for bot in bots:
            current_bots.append(threading.Thread(target=launch_bot, args=(bot[0], bot[1], bot[2])))
            current_bots[-1].start()
        bots = []

main()