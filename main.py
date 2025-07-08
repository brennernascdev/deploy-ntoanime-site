from flask import Flask, render_template
import socket

app = Flask(__name__)

serverIp = '170.84.158.7'
serverPort = 7171

def getServerState():
    global serverIp, serverPort
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.01) #Timeout in case of port not open
    result = sock.connect_ex((f'{serverIp}',serverPort))
    sock.close()
    return (result == 0 and 'online' or 'offline')

@app.route('/')
def homepage():
    global serverOnline
    serverOnline = getServerState()
    return render_template("index.html", online=serverOnline)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
