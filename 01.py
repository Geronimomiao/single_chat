from flask import  Flask, request, render_template
from geventwebsocket.websocket import WebSocket, WebSocketError
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

import json

app = Flask(__name__)

@app.route('/index/')
def index():
    return render_template('websocket.html')

user_socket_list = []
user_socket_dict={}

@app.route('/ws/<phone>')
def ws(phone):
    user_socket=request.environ.get("wsgi.websocket")
    if not user_socket:
        return "请以WEBSOCKET方式连接"

    user_socket_dict[phone]=user_socket
    print(user_socket_dict)

    while True:
        try:
            user_msg = user_socket.receive()
            if user_msg:
                user_msg = json.loads(user_msg)
                # user_msg.get("to_user") 获得目标用户昵称
                # to_user_socket 获得目标用户 Socket
                to_user_socket = user_socket_dict.get(user_msg.get("r_phone"))
                if not to_user_socket:
                    send_msg = {
                        "state": 101,
                        "send_msg": '对方不在线'
                    }
                    my_socket = user_socket_dict.get(phone)
                    my_socket.send(json.dumps(send_msg))
                else:
                    send_msg = {
                        "send_msg": user_msg.get("send_msg"),
                        "s_phone": user_msg.get("s_phone"),
                        "s_nickname": user_msg.get("s_nickname"),
                        "r_phone": user_msg.get("r_phone"),
                        "r_nickname": user_msg.get("r_nickname"),
                    }
                    to_user_socket.send(json.dumps(send_msg))
        except WebSocketError:
            user_socket_dict.pop(phone)
            print(user_socket_dict)
            break



if __name__ == '__main__':

    http_serve=WSGIServer(("0.0.0.0",5000), app, handler_class = WebSocketHandler)
    http_serve.serve_forever()
