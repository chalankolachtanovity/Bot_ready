import sqlite3
from datetime import datetime
from pytz import timezone
tz = timezone("Europe/Bratislava")


def table_insert(calculated_dict, sess):
  time_now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
  conn = sqlite3.connect("file::memory:?cache=shared")
  c = conn.cursor()
  for key, val in calculated_dict.items():
    params = [key] + val
    c.execute(f"INSERT INTO stats (session, datetime, name, 'total_kills', 'total_kills_headshot', 'total_damage_done', 'total_kills_knife', 'total_kills_hegrenade', 'total_deaths', 'total_wins', 'total_wins_pistolround', 'total_wins_map_de_dust2', 'total_wins_map_de_inferno', 'total_wins_map_de_nuke', 'total_wins_map_de_train', 'total_planted_bombs', 'total_defused_bombs', 'total_kills_ak47', 'total_hits_ak47', 'total_shots_ak47','total_kills_m4a1', 'total_shots_m4a1', 'total_hits_m4a1', 'total_kills_awp', 'total_hits_awp', 'total_shots_awp', 'total_kills_mp9', 'total_shots_mp9', 'total_hits_mp9', 'total_kills_galilar', 'total_hits_galilar', 'total_shots_galilar', 'total_kills_famas', 'total_hits_famas', 'total_shots_famas', 'total_kills_mac10', 'total_hits_mac10', 'total_shots_mac10', 'total_kills_mp7', 'total_hits_mp7', 'total_shots_mp7', 'total_weapons_donated', 'total_kills_sg556', 'total_hits_sg556', 'total_shots_sg556', 'total_kills_aug', 'total_hits_aug', 'total_shots_aug', 'total_kills_ssg08', 'total_hits_ssg08', 'total_shots_ssg08', 'total_kills_p90', 'total_hits_p90', 'total_shots_p90', 'total_kills_glock', 'total_hits_glock', 'total_shots_glock', 'total_kills_p250', 'total_hits_p250', 'total_shots_p250', 'total_kills_fiveseven', 'total_hits_fiveseven', 'total_shots_fiveseven', 'total_kills_tec9', 'total_hits_tec9', 'total_shots_tec9', 'total_kills_ump45', 'total_hits_ump45', 'total_shots_ump45', 'total_kills_deagle', 'total_hits_deagle', 'total_shots_deagle', 'total_kills_negev', 'total_hits_negev', 'total_shots_negev', 'total_kills_xm1014', 'total_hits_xm1014', 'total_shots_xm1014', 'total_kills_mag7', 'total_hits_mag7', 'total_shots_mag7', 'total_kills_sawedoff', 'total_hits_sawedoff', 'total_shots_sawedoff', 'total_kills_nova', 'total_hits_nova', 'total_shots_nova') VALUES (\'{sess}\', \'{time_now}\', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", params)      

  print("sqlite_demo.py > stats inserted in db")
  conn.commit() 
  conn.close()  

print('system -> db executed')