from flask import Flask, request
from threading import Thread
import json
app = Flask('')
counter = 0
last_message = 'Zatial nic'

@app.route('/', methods = ['GET', 'POST'])
def home():
    global counter
    html = """
<html>
  <head>
    <title>Milosovy hratky CSGO stats</title>
  </head>
  <form action = "https://botready.discordsam.repl.co/submit" method = "post">
         <h10 style="font-family:verdana;">CSGO stat viewer<h10>
         <p>Request:</p>
         <button onclick=>Hide elements</button>
      </form>   
  <body>
    <h3>Documentation</h3>
    <p1>This is sample documentation <br> total_kills</p1>
  </body>
</html>
    """
    #return f"Current player count is {counter}!"
    return html


@app.route('/submit', methods = ['POST'])
def submit_text():
    user = request.form['nm']
    global last_message
    last_message = user
    return user


def run():
    app.run(host='0.0.0.0', port=8080)


def set_player_count(players: int):
    global counter
    counter = players

def get_last_message() -> str:
    global last_message
    return last_message

def keep_alive():
    t = Thread(target=run)
    t.start()
