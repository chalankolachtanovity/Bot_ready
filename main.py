import sqlite3
import base64
from io import BytesIO
import numpy as np
import re
from matplotlib.figure import Figure
import string
from steam_stats import download_profile
from flask import Flask, render_template, request
from threading import Thread
from game_stats_compare import generate_kd_page, generate_hs_page
from site_generator import get_player_stats_generate_site
import os
import main_lachtan
from flask_restful import Resource, Api, reqparse
import pandas as pd
import ast



app = Flask(__name__)
api = Api(app)

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



import json 

def assign_to_dict(names) -> json:
    dictionary = {}
    for _, name in names:
        stats = get_data(name, 'total_kills')
        print(stats)
        stats_list = [int(s) for s in re.findall(r'\b\d+\b', f'{stats}')]
        dictionary[name] = stats_list
    
    datetimes = get_data('Kmasko', 'datetime')
    datetimes_list = [item[0] for item in datetimes]
    dictionary['Datetimes'] = datetimes_list

    json_object = json.dumps(dictionary, indent = 2)

    return json_object


class Data(Resource):
    def get(self):
        return assign_to_dict(PLAYERS), 200
    pass

api.add_resource(Data, '/users')


@app.route("/graph")
def g():
    return render_template('graph.html')


def get_data(name, data) -> list:
    conn = sqlite3.connect("file::memory:?cache=shared")
    c = conn.cursor()
    c.execute(f"""SELECT {data} FROM stats WHERE name='{name}'""")
    z = c.fetchall()
    conn.commit()
    conn.close()
    return z


@app.route("/")
def home():
    lst = main_lachtan.html_ready_list
    lachtan_dict = main_lachtan.html_dict
    if lachtan_dict == {}:
        return render_template("scraped_sc.html", kmasko=KMASKO_DICT['personaname'], stano=STANO_DICT['personaname'], aligator=ALIGATOR_DICT['personaname'], teetou=TEETOU_DICT['personaname'], tajmoti=TAJMOTI_DICT['personaname'],
        dron=DRON_DICT['personaname'], martin=MARTIN_DICT['personaname'], kulivox=KULIVOX_DICT['personaname'], bonsai_avatar=ALIGATOR_DICT["avatarfull"], bonsai_realname=ALIGATOR_DICT['realname']
        )
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