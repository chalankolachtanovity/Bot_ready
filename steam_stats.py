import requests


def download_stats_for_player(steam_id: str) -> dict:
    stat_dict = dict()
    stats_url = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key=D33FA7D4C85464093F988722544CE60D&steamid={steam_id}'
    KMASKO = requests.get(stats_url, auth=('user', 'pass'))
    KMASKO = KMASKO.json()
    kmaso = KMASKO['playerstats']['stats']
    for stat in kmaso:
        stat_dict[stat['name']] = stat['value'] 
    return stat_dict