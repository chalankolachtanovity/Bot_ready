from flask import Flask, request
from threading import Thread

app = Flask('')
counter = 0
last_message = 'Zatial nic'


@app.route('/', methods = ['GET', 'POST'])
def home():
    global counter
    html = """
<html>
  <head>
    <title>Milosovy hratky CSGO tracker</title>
  </head>
  <form action = "https://botready.discordsam.repl.co/submit" method = "post">
         <p>Enter Name:</p>
         <p><input type = "text" name = "nm" /></p>
         <p><input type = "submit" value = "submit" /></p>
      </form>   
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
