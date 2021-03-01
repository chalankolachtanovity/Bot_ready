from steam_stats import download_stats_for_player
import os

ComparisonPageCustomization = (str, str, str, str,(str, str, str), str, str)



def get_headshot_ratio(steam_id: str) -> int:
  stats = download_stats_for_player(steam_id)
  return int(int(stats['total_kills_headshot']) / int(stats['total_kills']) * 100)

def get_kd_ratio(steam_id: str) -> int:
  stats = download_stats_for_player(steam_id)
  return stats['total_kills'] / stats['total_deaths']

def get_best_stat(player_stats: list) -> (str,int):
  ruka = player_stats[0]
  for curr_name, curr_value in player_stats:
    if curr_value >= ruka[1]:
      ruka = curr_name, curr_value
  return ruka
  

def generate_hs_page(players: list) -> str:
  player_headshots = []
  for env_name, nice_name in players:
    headshots = get_headshot_ratio(os.getenv(env_name))   
    player_headshots.append((nice_name, headshots))
  max_headshots = get_best_stat(player_headshots)
  return generate_comparison_page(player_headshots, max_headshots, HS_PAGE_CUSTOMIZATION)

def generate_kd_page(players: list) -> str:
  player_kill_deaths = []
  for env_name, nice_name in players:
    kd_ratio = get_kd_ratio(os.getenv(env_name))
    player_kill_deaths.append((nice_name, kd_ratio))
  max_kd_ratio = get_best_stat(player_kill_deaths)
  return generate_comparison_page(player_kill_deaths, max_kd_ratio, KD_PAGE_CUSTOMIZATION)

def generate_comparison_page(player_stats: list, best: (str, int), customization: ComparisonPageCustomization):
    icon, title, heading, unit, (image, widht, height), best_title, idiot_table = customization
    stat_max_player, stat_max = best
    return (f"""
<html>
	<head>
		<link rel="icon" href="{icon}"/>
		<title>{title}</title>
	</head>
	<body style = "font-family: Verdana, sans-serif;">
		<h2>{heading}</h2>
		<table>
    {generate_comparison_table(player_stats, unit)}
		</table>
		<img src="{image}" alt="HTML5 Icon" width="{widht}" height="{height}"/>
		<h4>{best_title} {stat_max}{unit} achieved by {stat_max_player}</h4>
    {idiot_table}
	</body>
</html>
  """)



def generate_comparison_table(player_stats: list, unit: str):
  html = ''
  for player_stat in player_stats:
    html += generate_comparison_entry(player_stat, unit)
  return html
  
  


def generate_comparison_entry(player_stat: (str, int), unit: str):
  player, value = player_stat
  return f"""<tr>
				<td>{player}</td>
				<td>| {value}{unit} |</td>
			</tr>"""


HS_PAGE_CUSTOMIZATION = (
    "https://seeklogo.com/images/C/csgo-headshot-logo-D55BFE7334-seeklogo.com.png",
    "H/S ratio", "H/S ratio Lachtanov","%",
    ("https://staging2.filmdaily.co/wp-content/uploads/2020/05/coughing-cat-meme-lede.jpg",
     "25%", "20%"), "Best H/S ratio is", "")

KD_PAGE_CUSTOMIZATION = (
    "https://preview.redd.it/lh72f11p5jo31.png?auto=webp&s=c7252a6eeffdb5cdec87726552bac678667d95a5",
    "K/D ratio", "K/D ratio Lachtanov","",
    ("https://6.viki.io/image/7e05fe5b86b642c783dbbe1eeb92fd93.jpeg?s=900x600&e=t",
     '25%', '15%'), "Best k/d ratio is:", """<h3>Kartička pre idiotov:</h3>
            <table border=3>
              <tr><td>KD = kills / deaths , for your kill/deaths ratio; and. That means, if a<br> player has 10 kills and 5 deaths, his KD ratio is equal to 2. A KD ratio of 1 means<br> that the player got killed exactly as many times as he successfully eliminated his<br> opponents.
            </tr></td>
        </table>""")


def other_stats():
    return (f"""
  <html>
    <link rel="icon" href="https://cdn3.iconfinder.com/data/icons/e-commerce-8/91/stats-512.png">
      <body>
          <title>Other stats</title>
        <h1><u>Other stats</u></h1>
      </body>
    <table>
      <h3>Total kills</h3>
        <body style = "font-family: Verdana, sans-serif;">
          <tr><td>Stano total kills</td><td>| {stano_kills[0]} |---</td><td>|D|---| {stano_deaths[0]} |</td>
            <tr><td>Aligator total kills</td><td>| {aligator_kills[0]} |---</td><td>|D|---| {aligator_deaths[0]} |</td>
            <tr><td>Kmaso total kills</td><td>| {masko_kills[0]} |---</td><td>|D|---| {masko_deaths[0]} |</td>
          <tr><td>Teetou total kills</td><td>| {teetou_kills[0]} |---</td><td>|D|---| {teetou_deaths[0]} |</td>
        <tr><td>Tajmoti total kills</td><td>| {tajmoti_kills[0]} |---</td><td>|D|---| {tajmoti_deaths[0]} |</td>
    </table>
    {blue_square()}
    <table>
      <h3>Total knife kills</h3>
        <body style = "font-family: Verdana, sans-serif;">
          <tr><td>Stano knife kills</td><td>| {stano_kills_knife[0]} |</td>
            <tr><td>Aligator knife kills</td><td>| {aligator_kills_knife[0]} |</td>
            <tr><td>Kmaso knife kills</td><td>| {masko_kills_knife[0]} |</td>
          <tr><td>Teetou knife kills</td><td>| {teetou_kills_knife[0]} |</td>
        <tr><td>Tajmoti knife kills</td><td>| {tajmoti_kills_knife[0]} |</td>
    </table>
    {blue_square()}
    <table>
      <h3>Total TASER kills</h3>
        <body style = "font-family: Verdana, sans-serif;">
          <tr><td>Stano TASER kills</td><td>| {stano_kills_teaser[0]} |</td>
            <tr><td>Aligator TASER kills</td><td>| {aligator_kills_teaser[0]} |</td>
            <tr><td>Kmaso TASER kills</td><td>| {masko_kills_teaser[0]} |</td>
          <tr><td>Teetou TASER kills</td><td>| 0 |</td>
        <tr><td>Tajmoti TASER kills</td><td>| {tajmoti_kills_teaser[0]} |</td>
    </table>
    <img src="https://cdn.countryflags.com/thumbs/russia/flag-400.png" width="100%" height="33%">
    </body>
  </html>
  """)
