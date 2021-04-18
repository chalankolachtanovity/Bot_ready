import requests
import os
import json

def download_stats_for_player(steam_id: str) -> dict:
    key = os.getenv('steam_key')
    stat_dict = dict()
    stats_url = f'http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=730&key={key}&steamid={steam_id}'
    KMASKO = requests.get(stats_url, auth=('user', 'pass'))
    KMASKO = KMASKO.json()
    kmaso = KMASKO['playerstats']['stats']
    for stat in kmaso:
        stat_dict[stat['name']] = stat['value'] 
    return stat_dict
    
def download_profile(steam_id: str) -> dict:
    key = os.getenv('steam_key')
    profile_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={key}&steamids={steam_id}"
    PROFILE = requests.get(profile_url, auth=('user', 'pass'))
    PROFILE = PROFILE.json()
    user_profile = PROFILE["response"]["players"]
    return user_profile[0]