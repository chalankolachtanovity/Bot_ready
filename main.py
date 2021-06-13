import sqlite3
import base64
from io import BytesIO
import numpy as np
from matplotlib.figure import Figure
import string
from steam_stats import download_profile
from flask import Flask, render_template, request
from threading import Thread
from game_stats_compare import generate_kd_page, generate_hs_page
from site_generator import get_player_stats_generate_site
import os
import main_lachtan
app = Flask(__name__)

PLAYERS = [('t_stano', 'Stano'), ('t_aligator', 'Aligator'), ('t_kmaso', 'Kmasko'), ('t_teetou', 'Teetou'), ('t_tajmoti', 'Tajmoti'), ('t_dron', 'Dron'), ('t_martin', 'Martin'), ('t_kulivox', 'Kulivox')]
LETTERS = string.ascii_uppercase
KMASKO_DICT = download_profile(os.getenv("t_kmaso"))
STANO_DICT = download_profile(os.getenv("t_stano"))
ALIGATOR_DICT = download_profile(os.getenv("t_aligator"))
TEETOU_DICT = download_profile(os.getenv("t_teetou"))
TAJMOTI_DICT = download_profile(os.getenv("t_tajmoti"))
DRON_DICT = download_profile(os.getenv("t_dron"))
MARTIN_DICT = download_profile(os.getenv("t_martin"))
KULIVOX_DICT = download_profile(os.getenv("t_kulivox"))


def create_graph(name, name1, stat, stat1, id):
    fig = Figure()
    ax = fig.subplots()
    bar1 = get_data(name, stat)
    session_time_name = get_data(name, 'datetime')
    session_time_name_1 = get_data(name1, 'datetime')
    session_time = session_time_name
    if len(session_time_name) != len(session_time_name_1):
        if len(session_time_name) >= len(session_time_name_1):
            session_time = session_time_name
        if len(session_time_name_1) >= len(session_time_name):
            session_time = session_time_name_1
    labels = []
    bar1_list = []
    bar2_list = []
    if id == 2:
        bar2 = get_data(name1, stat1)
        if len(bar1) >= len(bar2):
          difference = int(len(bar1) - len(bar2))
        if len(bar2) >= len(bar1):
          difference = int(len(bar2) - len(bar1))

        if len(bar1) != len(bar2):
          for x in range(difference):
              if len(bar1) <= len(bar2):
                  bar1_list.append(int(0))
              elif len(bar1) >= len(bar2):
                  bar2_list.append(int(0))
              elif len(bar2) <= len(bar1):
                  bar2_list.append(int(0))
              elif len(bar2) >= len(bar1):
                  bar1_list.append(0)
        for st2 in bar2:
            for s2 in st2:
                bar2_list.append(s2)
    for st1 in bar1:
        for s1 in st1:
            bar1_list.append(s1)
    for label in session_time:
        for l in label:
            labels.append(l)

    x = np.arange(len(bar1_list))
    width = 0.35
    if id == 1:
        rects1 = ax.bar(x - width / 800, bar1_list, width, label=f"{name} {stat}")
    if id == 2:
        rects1 = ax.bar(x - width / 2, bar1_list, width, label=f"{name} {stat}")
        rects2 = ax.bar(x + width / 2, bar2_list, width, label=f"{name1} {stat1}")
    ax.set_ylabel('Stats')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc='lower left',
           ncol=2, mode="expand", borderaxespad=0.)
    ax.bar_label(rects1, padding=3)
    if id == 2:
        ax.bar_label(rects2, padding=3)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    labels.clear()
    bar1_list.clear()
    bar2_list.clear()
    return html + f"""
<html>
<body>
<head>
	  <link rel="icon" href="https://image.freepik.com/free-icon/graph_318-10306.jpg">
	    <title>Stats graph</title>
  </head>
	  <h1>Session graph for {name}</h1> 
    <div class='center'>    
      <img src='data:image/png;base64,{data}'/>
    </div>
    <button class="button" onclick="location.href = '/'">Home</button>
</body>
</html>"""


def get_data(name, data) -> list:
    conn = sqlite3.connect("file::memory:?cache=shared")
    c = conn.cursor()
    c.execute(f"""SELECT {data} FROM stats WHERE name='{name}'""")
    z = c.fetchall()
    conn.commit()
    conn.close()
    return z


@app.route("/customize_graph", methods=["POST", "GET"])
def customize_graph():
    if request.method == "POST":
        user = request.form["names"]
        stat = request.form["stats"]
        user_2 = request.form['names_1']
        stat_2 = request.form["stats_1"]
        if user_2 == "none" or stat_2 == "none":
            return create_graph(user, user_2, stat, stat_2, 1)
        else:
            return create_graph(user, user_2, stat, stat_2, 2)
    else:
        return html


@app.route("/<nam>/<sta>")
def s_f(nam, sta):
    return create_graph(nam, nam, sta, "", 1)


@app.route("/")
def home():
    lst = main_lachtan.html_ready_list
    lachtan_dict = main_lachtan.html_dict
    if lachtan_dict == {}:
        return render_template("scraped_sc.html", kmasko=KMASKO_DICT['personaname'], stano=STANO_DICT['personaname'], aligator=ALIGATOR_DICT['personaname'], teetou=TEETOU_DICT['personaname'], tajmoti=TAJMOTI_DICT['personaname'],
        dron=DRON_DICT['personaname'], martin=MARTIN_DICT['personaname'], kulivox=KULIVOX_DICT['personaname'], bonsai_avatar=ALIGATOR_DICT["avatarfull"], bonsai_realname=ALIGATOR_DICT['realname']
      )
    else:
        return render_template("scraped_sc.html", players_ready=(', '.join(lst)), curr_session=lachtan_dict["session"], max_players=lachtan_dict["max_players"], kmasko=KMASKO_DICT['personaname'], stano=STANO_DICT['personaname'], aligator=ALIGATOR_DICT['personaname'], teetou=TEETOU_DICT['personaname'], tajmoti=TAJMOTI_DICT['personaname'], dron=DRON_DICT['personaname'], martin=MARTIN_DICT['personaname'], kulivox=KULIVOX_DICT['personaname'], bonsai_avatar=ALIGATOR_DICT["avatarfull"], bonsai_realname=ALIGATOR_DICT['realname']
      )


@app.route("/kmaso")
def kmaso():
    smako_custom = ('https://dam.nmhmedia.sk/image/3d61f2ee-e9cc-4f0d-9fea-d1f5b82bb61b_dam-urlwlvhbz.jpg/960/540','Kmasko',KMASKO_DICT['personaname'], KMASKO_DICT['avatarfull'], KMASKO_DICT['realname'] , 'kmasko')
    return get_player_stats_generate_site(os.getenv('t_kmaso'), smako_custom)


@app.route("/stano")
def stano():
    stano_custom = ("https://e7.pngegg.com/pngimages/117/291/png-clipart-flag-of-hungary-vecteur-flag-miscellaneous-flag-thumbnail.png", 'Milan', STANO_DICT['personaname'], STANO_DICT['avatarfull'], STANO_DICT['realname'],  'stano')
    return get_player_stats_generate_site(os.getenv('t_stano'), stano_custom)


@app.route("/aligator")
def aligator():
    aligator_custom = ("https://i.pinimg.com/originals/02/09/59/0209592f535ef9b9402946a2599191ac.jpg", "Aligator", ALIGATOR_DICT['personaname'], ALIGATOR_DICT['avatarfull'], ALIGATOR_DICT['realname'], 'aligator')
    return get_player_stats_generate_site(os.getenv('t_aligator'), aligator_custom)


@app.route("/teetou")
def teetou():
    risko_custom = ("https://i1.sndcdn.com/artworks-000157051671-azmuka-t500x500.jpg","Rížo",TEETOU_DICT['personaname'], TEETOU_DICT['avatarfull'], TEETOU_DICT['realname'], 'teetou')
    return get_player_stats_generate_site(os.getenv('t_teetou'), risko_custom)


@app.route("/tajmoti")
def tajmoti():
    tajmoti_customize = ("https://www.hopkinsmedicine.org/sebin/custom/hopkins_photos/large/4004786.jpg","Timothy",TAJMOTI_DICT['personaname'], TAJMOTI_DICT['avatarfull'], TAJMOTI_DICT['realname'], 'tajmoti')
    return get_player_stats_generate_site(os.getenv('t_tajmoti'), tajmoti_customize)

@app.route('/dron')
def dron():
    dron_customize = ("https://www.rcprofi.sk/files/rcprofi-sk/soubory/modulimages/800x800/drony-4.jpg","Dron",DRON_DICT['personaname'], DRON_DICT['avatarfull'], 'None', 'dron')
    return get_player_stats_generate_site(os.getenv('t_dron'), dron_customize)


@app.route('/martin')
def martin():
    martin_customize = ("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Seal_of_the_United_States_Senate.svg/1200px-Seal_of_the_United_States_Senate.svg.png","Martin", MARTIN_DICT['personaname'], MARTIN_DICT['avatarfull'], MARTIN_DICT['realname'], 'martin')
    return get_player_stats_generate_site(os.getenv('t_martin'), martin_customize)


@app.route('/kulivox')
def kulivox():
    kulivox_customize = ("https://i.pinimg.com/originals/ef/32/cc/ef32cceacbc5d21901cb46014b71c585.jpg","Kulivox",KULIVOX_DICT['personaname'], KULIVOX_DICT['avatarfull'], 'None', 'kulivox')
    return get_player_stats_generate_site(os.getenv('t_kulivox'), kulivox_customize)


@app.route("/kdratio")
def kd_ratio():
    return generate_kd_page(PLAYERS)


@app.route("/headshot_ratio")
def hs_ratio():
    return generate_hs_page(PLAYERS)


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()

html = """
<!DOCTYPE html>
<body>
<style>
custom-select {
  position: relative;
  font-family: Arial;
  backround-color: red
}
h3 {
  text-align: center;
}

h1 {
  text-align: center;
}

h3 {
  color: rgb(58, 187, 213)
}

.button {
  background-color: #008CBA;
  border: none;
  color: white;
  padding: 5px 8px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 18px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 8px;
}

.center {
  margin-left: auto;
  margin-right: auto;
  text-align: center;
}

.button4 {
  background-color: #E4E1E1;
  color: black;
  padding: 2px 5px;
  font-size: 16px;
  margin: 0px 0px
}

.button5 {
  background-color: #ffffff;
  color: black;
  padding: 2px 5px;
  font-size: 16px;
  margin: 0px 0px
}

label {
  font-size: 24px;
}

form {
  text-align: center;
}

option {
  /* background-color: #F0F6FF; */
  font-family: Arial;
  font-size: 1.2em;
  padding: 1em 1.5em;  
}

select {
  font-family: Arial;
  font-size: 1.2em;
  padding: 0.2em 0.2em; 
}

</style>
<h1>Customize your graph</h1>
<form action="#" method="post">
  <label for="name">Your name: </label>
  <select name="names" id="names">
    <option value="" selected disabled hidden>Choose here</option>
    <option value="Tajmoti">Tajmoti</option>
    <option value="Teetou">Teetou</option>
    <option value="Stano">Stano</option>
    <option value="Kmasko">Kmasko</option>
    <option value="Aligator">Aligator</option>
    <option value="Dron">Dron</option>
    <option value="Martin">Martin</option>
    <option value="Kulivox">Kulivox</option>
  </select>
  <br><br>
  <label for="stat">Stat: </label>
  <select name="stats" id="stats">
    <option value="" selected disabled hidden>Choose here</option>
    <option value="total_kills">Kills</option>
    <option value="total_deaths">Deaths</option>
    <option value="total_planted_bombs">Planted bombs</option>
    <option value="total_defused_bombs">Defused bombs</option>
    <option value="total_kills_ak47">Kills ak47</option>
  </select>
  <br><br>
  <label for="name">Second name: </label>
  <select name="names_1" id="names_1">
    <option value="" selected disabled hidden>Choose here</option>
    <option value="none">None</option>
    <option value="Tajmoti">Tajmoti</option>
    <option value="Teetou">Teetou</option>
    <option value="Stano">Stano</option>
    <option value="Kmasko">Kmasko</option>
    <option value="Aligator">Aligator</option>
    <option value="Dron">Dron</option>
    <option value="Martin">Martin</option>
    <option value="Kulivox">Kulivox</option>
  </select>
  <br><br>
  <label for="stat">Second stat: </label>
  <select name="stats_1" id="stats_1">
    <option value="" selected disabled hidden>Choose here</option>
    <option value="none">None</option>
    <option value="total_kills">Kills</option>
    <option value="total_deaths">Deaths</option>
    <option value="total_planted_bombs">Planted bombs</option>
    <option value="total_defused_bombs">Defused bombs</option>
    <option value="total_kills_ak47">Kills ak47</option>
  </select>
  <br><br>
  <input class="button" type="submit" value="submit">
</form>
</body>
</html>
"""