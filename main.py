import requests
import websocket
import json
import re
from bot import play
import datas

def get_sid(session):
    url = "https://snake-online-d2fcff637053.herokuapp.com/socket.io/?EIO=4&transport=polling&t=Or6DQd9"
    r = session.get(url)

    try:sid = json.loads(r.text[1:])["sid"]
    except:raise Exception("echec de la réception du sid")
    
    return sid

def init_ws(session, sid):
    url=f"wss://snake-online-d2fcff637053.herokuapp.com/socket.io/?EIO=4&transport=websocket&sid={sid}"

    ws = websocket.WebSocket()
    ws.connect(url)
    return ws

def connect(session, sid, ws, username):
    r = session.post(f"https://snake-online-d2fcff637053.herokuapp.com/socket.io/?EIO=4&transport=polling&t=Or6DQfM&sid={sid}",
           data='40')
    print(f"sent 40: {r.status_code}")

    ws.send('2probe')
    print(f"sent '2probe': {ws.status}")
    print(f"recieve {ws.recv()}: {ws.status}")

    r = session.post(f"https://snake-online-d2fcff637053.herokuapp.com/socket.io/?EIO=4&transport=polling&t=Or6DQfM&sid={sid}",
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

def wait_room(ws):
    while True:
        res = ws.recv()
        if (res=="2"):
            #print("check ping")
            ws.send("3")
        elif (re.search("addClientRoom", res)):
            print("lancement de la partie")
            ws.send('42["playRoom"]')
            play(ws, datas.bot)
        elif (re.search("removeClientRoom", res)):
            print("orther player quit")
            nb_players-=1
        else:
            print(f"undefined res: {res}")

def main():
    while True:
        s = requests.Session()

        sid = get_sid(s)

        ws = init_ws(s, sid)

        connect(s, sid, ws, datas.name)

        create_room(ws)

        wait_room(ws)

        ws.close()

main()
