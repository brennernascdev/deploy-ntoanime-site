from flask import Flask, render_template
import socket

app = Flask(__name__)

serverIp = '191.252.223.223'
serverPort = 7171
download_link = "https://drive.google.com/file/d/1oVkdskoQzwdHk6p4cGU2rkCadf_Ms6oy/view?usp=drive_link"

def getServerState():
    global serverIp, serverPort
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.01) #Timeout in case of port not open
    result = 'offline'
    try:
        sock.connect((serverIp,serverPort))
        result = 'online'
    except Exception:
        result = 'offline'
    
    sock.close()
    print(result)
    return result

@app.route('/')
def homepage():
    global serverOnline
    serverOnline = getServerState()
    print(serverOnline)
    return render_template("index.html", online=serverOnline)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
