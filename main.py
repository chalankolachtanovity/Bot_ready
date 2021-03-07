from flask import Flask
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
app = Flask(__name__)

PLAYERS = [('t_stano','Stano'), ('t_aligator','Aligator'), ('t_kmaso','Kmasko'), ('t_teetou','Teetou'), ('t_tajmoti','Tajmoti')]


@app.route("/")
def home():
    with open("index.html", "r") as f:
        x = f.read()
    return x



@app.route("/kmaso")
def kmaso():
    smako_custom = (' https://dam.nmhmedia.sk/image/3d61f2ee-e9cc-4f0d-9fea-d1f5b82bb61b_dam-urlwlvhbz.jpg/960/540','Kmaaaaaaaaaaaaaaaaasko','Kmáskové štatistiky','https://www.sports.sk/Data/1092/UserFiles/clanky/sona_predna_sumce/sumec_1.png')
    return get_player_stats_generate_site(os.getenv('t_kmaso'), smako_custom)


@app.route("/stano")
def stano():
    stano_custom = ("https://e7.pngegg.com/pngimages/117/291/png-clipart-flag-of-hungary-vecteur-flag-miscellaneous-flag-thumbnail.png", 'Milaaaaaaaaaaaaaaan', 'Stanove štatistiky', "https://minorityrights.org/wp-content/uploads/2019/04/1996-Flag-of-Hungary.jpg")
    return get_player_stats_generate_site(os.getenv('t_stano'), stano_custom)


@app.route("/aligator")
def aligator():
    aligator_custom = ("https://i.pinimg.com/originals/02/09/59/0209592f535ef9b9402946a2599191ac.jpg", "Aligaaaaaaaaaaator", "Aligátoris štatistiky", "https://images2.minutemediacdn.com/image/upload/c_crop,h_1600,w_2378,x_11,y_0/v1579707709/shape/mentalfloss/56093-gettyimages-1171368832.jpg?itok=x5t6Tht2")
    return get_player_stats_generate_site(os.getenv('t_aligator'), aligator_custom)


@app.route("/teetou")
def teetou():
    risko_custom = ("https://i1.sndcdn.com/artworks-000157051671-azmuka-t500x500.jpg","Rííííííííížo","Rížové štatistiky","https://www.kfcslovakia.sk/wp-content/uploads/2018/12/kfc_buckety_hw30-400x400.jpg")
    return get_player_stats_generate_site(os.getenv('t_teetou'), risko_custom)


@app.route("/tajmoti")
def tajmoti():
    tajmoti_customize = ("https://www.hopkinsmedicine.org/sebin/custom/hopkins_photos/large/4004786.jpg","Timothyyyyyyyyyyyyy","Tajmonivove štatistiky", "https://visualsonline.cancer.gov/retrieve.cfm?imageid=10433&dpi=72&fileformat=jpg")
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