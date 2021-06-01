from steam_stats import download_stats_for_player


def blue_square():
    with open("blue_square.html", "r") as f:
        htmll = f.read()
    return htmll


def get_player_stats_generate_site(steam_id: str, player_customization: (str, str, str, str)):
    stat_dict = download_stats_for_player(steam_id)

    return generate_player_site(stat_dict, player_customization)


GENERAL_STATS_DICT = {
  "Total kills": "total_kills",
  "Total deaths": "total_deaths",
  "Total wins": "total_wins",
  "Total demage done": "total_damage_done",
  "Total planted bombs": "total_planted_bombs",
  "Total defused bombs": "total_defused_bombs"
}


CATEGORY_TO_WEAPONS_DICT = {
  "Rifles": [('ak47', 'AK-47'), ('m4a1', 'M4A1-s'), ('famas', 'FAMAS'), ('galilar', 'GALIIL'), ('ssg08', 'SCOUT'), ('sg556', 'SG556'), ('awp', 'AWP'), ('scar20', 'AUTOLAMA CT'), ('g3sg1', 'AUTOLAMA T')],
  "SMG's": [('mac10', 'MAC-10'), ('mp7', 'MP-7'), ('mp9', 'MP-9'), ('p90', 'P-90'), ('ump45', 'UMP-45'), ('bizon', 'BIZON')],
  "Heavy": [('negev', 'NEGEV'), ('mag7', 'MAG-7')],
  "Pistols": [('glock', 'GLOCK'), ('p250', 'P250'), ('tec9', 'TEC-9'), ('fiveseven', 'FIVESEVEN')]
}


def generate_player_site(samko_stats: dict, player_customization: (str, str, str, str, str, str, str)) -> str:
    icon, title, name, profile_img, real_name, graph_name = player_customization
    return (f"""
    <html>
        <link rel="icon" href="{icon}">
        <body>
          <title>{title}</title>
          <h1>{name}'s stats</h1>
          <div>
            <p style="float: left;"><img src="{profile_img}" height="200px" width="200px"></p>
            <h2><br>{name}</h2>
            <p1>{real_name}</p1>
          </div>
          <h><br></h1>
          {blue_square()}
        </body>
    <body style = "font-family: Verdana, sans-serif;">
      <table>
        <p style = "font-family:courier,arial,helvetica;">
          {generate_gnrl_stats(samko_stats)}
      </table>
      {blue_square()}
      {generate_weapon_stats(samko_stats)}
          <br>
          <table border=3>
          <tr><td>Acc -> Accuracy is ratio between shots fired and shots hit.
        </tr></td>
      </table>
      {blue_square()}
    </body>
    </html>
    """)


def generate_gnrl_stats(samko_stats: dict) -> str:
    rows = ""
    for name, key in GENERAL_STATS_DICT.items():
        rows += f"<tr><td>{name}</td><td>| {samko_stats[key]} |</td>"
    return rows


def generate_weapon_category_stats(samko_stats: dict, weapons: list) -> str:
    weapon_rows = ""
    accuracy = get_guns_accuracy(samko_stats, CATEGORY_TO_WEAPONS_DICT)
    for weapon_steam, weapon_nice in weapons:
        weapon_rows += f"<tr><td>{'Total kills '+weapon_nice}</td><td>| {samko_stats['total_kills_'+weapon_steam]} | </td><td> -> Accuracy</td><td>| {accuracy[f'Accuracy {weapon_nice}']}% |</td>"
    return weapon_rows


def generate_weapon_stats(samko_stats: dict) -> str:
    html = ''
    for name, weapons in CATEGORY_TO_WEAPONS_DICT.items():
        html += f"<table><h3>{name}</h3>"
        html += generate_weapon_category_stats(samko_stats, weapons)
        html += "</table>"
    return html


def get_guns_accuracy(samko_stats, weapon_dict) -> int:
    final_dict = {}
    for _, value in weapon_dict.items():
        for steam_name, nice_name in value:
            final_dict[f"Accuracy {nice_name}"] = int(int(samko_stats[f'total_hits_{steam_name}']) / int(samko_stats[f'total_shots_{steam_name}']) * 100)
    return final_dict
