import sqlite3
import base64
from io import BytesIO
import numpy as np
from flask import Flask
from matplotlib.figure import Figure
import string
from steam_stats import *
from sqlite_demo import *
from bs4 import BeautifulSoup
from flask import Flask, redirect, url_for, render_template
from stats_compare import *
import requests
from flask import Flask, request
from threading import Thread
from flask import Flask, render_template
from game_stats_compare import *
from site_generator import *
import os
from discord.ext import commands
import discord
import random
import os
import main_lachtan
from flask import jsonify
app = Flask(__name__)

PLAYERS = [('t_stano','Stano'), ('t_aligator','Aligator'), ('t_kmaso','Kmasko'), ('t_teetou','Teetou'), ('t_tajmoti','Tajmoti')]
LETTERS = string.ascii_uppercase
KMASKO_DICT = download_profile(os.getenv("t_kmaso"))
STANO_DICT = download_profile(os.getenv("t_stano"))
ALIGATOR_DICT = download_profile(os.getenv("t_aligator"))
TEETOU_DICT = download_profile(os.getenv("t_teetou"))
TAJMOTI_DICT = download_profile(os.getenv("t_tajmoti"))

def create_graph(name, steam_name, stat, stat1, id):
    fig = Figure()
    ax = fig.subplots()
    bar1 = get_data(name, stat)
    if id == 2:
      bar2 = get_data(name, stat1)
    session_time = get_data(name, 'datetime')
    labels = []
    bar1_list = []
    bar2_list = []

    for st1 in bar1:
      for s1 in st1:
        bar1_list.append(s1)
    if id == 2:
      for st2 in bar2:
        for s2 in st2:
          bar2_list.append(s2)   
    for label in session_time:
      for l in label:
        labels.append(l)  

    x = np.arange(len(bar1_list))
    width = 0.35
    if id == 1:
      rects1 = ax.bar(x - width/800, bar1_list, width, label=stat)
    if id == 2:
      rects1 = ax.bar(x - width/2, bar1_list, width, label=stat)
      rects2 = ax.bar(x + width/2, bar2_list, width, label=stat1)
    ax.set_ylabel('Stats')
    ax.set_title(f"{steam_name}'s graph")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.bar_label(rects1, padding=3)
    if id == 2:
      ax.bar_label(rects2, padding=3)
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    labels.clear()
    bar1_list.clear()
    bar2_list.clear()
    return f"""
<html>
<body>
<head>
	  <link rel="icon" href="https://image.freepik.com/free-icon/graph_318-10306.jpg">
	    <title>Stats graph</title>
  </head>
	  <h1>Session graph for {steam_name}</h1>     
    <img src='data:image/png;base64,{data}'/>
</body>
</html>"""

def get_data(name, data):
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
    return redirect(url_for("s_f", nam=user, sta=stat))
  else:
    return render_template("index_graph.html")

@app.route("/<nam>/<sta>")
def s_f(nam, sta):
  return create_graph(nam, nam, sta, "", 1)

@app.route("/")
def home():
    print(request.environ.get('HTTP_X_REAL_IP', request.remote_addr))
    lst = main_lachtan.html_ready_list
    lachtan_dict = main_lachtan.html_dict
    if lachtan_dict == {}:
      return render_template("index.html", kmasko=KMASKO_DICT['personaname'], stano=STANO_DICT['personaname'], aligator=ALIGATOR_DICT['personaname'], teetou=TEETOU_DICT['personaname'], tajmoti=TAJMOTI_DICT['personaname'])
    else:
      return render_template("index.html", players_ready=(', '.join(lst)), curr_session=lachtan_dict["session"], max_players=lachtan_dict["max_players"], kmasko=KMASKO_DICT['personaname'], stano=STANO_DICT['personaname'], aligator=ALIGATOR_DICT['personaname'], teetou=TEETOU_DICT['personaname'], tajmoti=TAJMOTI_DICT['personaname']
      )

@app.route("/graph_stano")
def g_stano():
  return create_graph('Stano', STANO_DICT['personaname'], 'total_kills', 'total_deaths', 2)

@app.route("/graph_tajmoti")
def g_tajmoti():
  return create_graph('Tajmoti', TAJMOTI_DICT['personaname'], 'total_kills', 'total_deaths', 2)

@app.route("/graph_aligator")
def g_aligator():
  return create_graph('Aligator', ALIGATOR_DICT['personaname'], 'total_kills', 'total_deaths', 2)

@app.route("/graph_kmasko")
def g_kmasko():
  return create_graph('Kmasko', KMASKO_DICT['personaname'], 'total_kills', 'total_deaths', 2)

@app.route("/graph_teetou")
def g_teetou():
  return create_graph('Teetou', TEETOU_DICT['personaname'], 'total_kills', 'total_deaths', 2)

@app.route("/kmaso")
def kmaso():
    smako_custom = ('https://dam.nmhmedia.sk/image/3d61f2ee-e9cc-4f0d-9fea-d1f5b82bb61b_dam-urlwlvhbz.jpg/960/540','Kmaaaaaaaaaaaaaaaaasko',KMASKO_DICT['personaname'], KMASKO_DICT['avatarfull'], KMASKO_DICT['realname'] , 'kmasko')
    return get_player_stats_generate_site(os.getenv('t_kmaso'), smako_custom)


@app.route("/stano")
def stano():
    stano_custom = ("https://e7.pngegg.com/pngimages/117/291/png-clipart-flag-of-hungary-vecteur-flag-miscellaneous-flag-thumbnail.png", 'Milaaaaaaaaaaaaaaan', STANO_DICT['personaname'], STANO_DICT['avatarfull'], STANO_DICT['realname'],  'stano')
    return get_player_stats_generate_site(os.getenv('t_stano'), stano_custom)


@app.route("/aligator")
def aligator():
    aligator_custom = ("https://i.pinimg.com/originals/02/09/59/0209592f535ef9b9402946a2599191ac.jpg", "Aligaaaaaaaaaaator", ALIGATOR_DICT['personaname'], ALIGATOR_DICT['avatarfull'], ALIGATOR_DICT['realname'], 'aligator')
    return get_player_stats_generate_site(os.getenv('t_aligator'), aligator_custom)


@app.route("/teetou")
def teetou():
    risko_custom = ("https://i1.sndcdn.com/artworks-000157051671-azmuka-t500x500.jpg","Rííííííííížo",TEETOU_DICT['personaname'], TEETOU_DICT['avatarfull'], TEETOU_DICT['realname'], 'teetou')
    return get_player_stats_generate_site(os.getenv('t_teetou'), risko_custom)


@app.route("/tajmoti")
def tajmoti():
    tajmoti_customize = ("https://www.hopkinsmedicine.org/sebin/custom/hopkins_photos/large/4004786.jpg","Timothyyyyyyyyyyyyy",TAJMOTI_DICT['personaname'], TAJMOTI_DICT['avatarfull'], TAJMOTI_DICT['realname'],  'tajmoti')
    return get_player_stats_generate_site(os.getenv('t_tajmoti'), tajmoti_customize)


@app.route("/kdratio")
def kd_ratio():
    return generate_kd_page(PLAYERS)


@app.route("/headshot_ratio")
def hs_ratio():
    return generate_hs_page(PLAYERS)


@app.route("/other_stats")
def all_stats():
    return (f'{other_stats()}')

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()