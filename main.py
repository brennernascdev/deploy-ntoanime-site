from flask import Flask, render_template, request, redirect, url_for, make_response, flash, Response, jsonify, send_file, session
import mysql.connector
import hashlib
import socket
import threading
import time
checkServer = False
serverIp = "ntoanime.com"
serverPort = 7171
serverOnline = False

vocations = {
    "Naruto": 1,
    "Sasuke": 10,
    "Lee": 20,
    "Sakura": 30,
    "Kiba": 40,
    "Shikamaru": 50,
    "Hinata": 60,
    "Tenten": 70,
    "Itachi": 80,
    "Bee": 90,
    "Kakashi": 100,
    "Gaara": 120,
    "Neji": 130
}
# Database / Banco de Dados
'''db = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="@jbMysql01",
    database="ntoanime",
    auth_plugin="mysql_native_password"
)'''

# Instancia do Flask
app = Flask(__name__)
app.secret_key = "_@a123yA~123Sº"

def createNewCharacter(name, vocation):
    print(name, vocation)
    pass

def updateServerState():
    global serverOnline, serverIp, serverPort
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.01) #Timeout in case of port not open
    result = sock.connect_ex((f'{serverIp}',serverPort))
    sock.close()
    serverOnline = (result == 0 and True or False)
    
def checkServerState():
    global serverOnline, serverIp, serverPort
    global checkServer
    
    while checkServer:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1) #Timeout in case of port not open
        result = sock.connect_ex((f'{serverIp}',serverPort))
        sock.close()
        serverOnline = (result == 0 and True or False)
        time.sleep(60)

#Routes / Rotas
@app.route('/')
def index():
    updateServerState()
    if not 'account_id' in session:
        session['account_id'] = 0

    if not 'logged-in' in session:
        session['logged-in'] = False

    return render_template("home.html", logged=session['logged-in'], online=serverOnline)

@app.get('/account/')
def accountGet():
    if not 'account_id' in session:
        session['account_id'] = 0

    if not 'logged-in' in session:
        session['logged-in'] = False

    subtopic = request.args.get('subtopic')

    resp = make_response(render_template('login.html', logged=session['logged-in'], online=serverOnline))
    if subtopic == 'logout':
        session.pop('logged-in')
        session.pop('username')
        session.pop('account_id')
        return redirect('/account/')
    elif subtopic == 'createaccount':
        return render_template('createaccount.html', logged=session['logged-in'], online=serverOnline)

    if 'logged-in' in session and 'username' in session and 'password' in session:
        username = session.get('username')
        password = session.get('password')

        hasher = hashlib.sha1(password.encode())
        hashPass = hasher.hexdigest()

        db.cmd_refresh(options=True)
        cursor = db.cursor()
        query = f"SELECT id, name FROM accounts WHERE name = '{username}' AND password = '{hashPass}';"
        cursor.execute(query)
        lista = cursor.fetchone()

        if lista != None:
            query = f"SELECT name, level FROM players WHERE account_id = {lista[0]};"
            cursor.execute(query)
            characters = cursor.fetchall()
            resp = make_response(render_template('account.html', logged=session['logged-in'], characters=characters, online=serverOnline))

        cursor.close()
    return resp

@app.post('/account/')
def accountPost():
    if not 'account_id' in session:
        session['account_id'] = 0

    if not 'logged-in' in session:
        session['logged-in'] = False

    subtopic = request.args.get('subtopic')

    if subtopic == 'createcharacter':
        character_name = request.form.get('charName').strip()
        vocationName = request.form.get('radVoc').capitalize()

        db.cmd_refresh(options=True)

        cursor = db.cursor()
        query = f"""INSERT INTO players (name, account_id, vocation, conditions, town_id, posx,posy,posz, soul, mana, cap)
            VALUES ('{character_name}', {session['account_id']}, {vocations[vocationName]}, '', 1, 1027, 912, 5, 100, 100, 400);
        """
        ret = cursor.execute(query)
        print(ret)
        db.commit()

        cursor.close()
        createNewCharacter(character_name, vocationName)
        return redirect('/account/')

    if subtopic == 'createaccount':
        username = request.form.get('usuario')
        password = request.form.get('senha')

        hasher = hashlib.sha1(password.encode())
        hashPass = hasher.hexdigest()

        db.cmd_refresh(options=True)
        cursor = db.cursor()
        query = f"INSERT INTO accounts (name, password) VALUES ('{username}', '{hashPass}');"
        cursor.execute(query)
        db.commit()
        cursor.close()
        return redirect('/account/')

    username = request.form.get('usuario')
    password = request.form.get('senha')

    if username == "1" and password == "1":
        return redirect('/account/')

    hasher = hashlib.sha1(password.encode())
    hashPass = hasher.hexdigest()

    db.cmd_refresh(options=True)
    cursor = db.cursor()
    query = f"SELECT id, name FROM accounts WHERE name = '{username}' AND password = '{hashPass}';"
    cursor.execute(query)
    lista = cursor.fetchone()
    cursor.close()
    if lista != None:
        session['username'] = username
        session['password'] = password
        session['account_id'] = lista[0]
        session['logged-in'] = True

    return redirect('/account/')

if __name__ == "__main__":
    th = threading.Thread(target=checkServerState, args=[])
    
    checkServer = True
    #th.start()
    app.run(host="0.0.0.0", port=8081)
    
    checkServer = False
