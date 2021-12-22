import requests, os, json, time, traceback
from dotenv import dotenv_values

env = dotenv_values(".env")

config = json.load(open("config.json"))
config["steam"]["key"] = env["STEAM"]

def getSteamGame(appid):
    appid = str(appid)
    with open(config["dir"]+"steam/store/store.json") as store:
        store = json.load(store)

    if appid in store:
        return store[appid]

    else:
        time.sleep(0.5) ## scuffed avoiding steam ratelimits ftw
        url = "https://store.steampowered.com/api/appdetails?appids=" + appid + "&l=english"
        headers = {"Accept-Language": "en-US,en;q=0.5"}
        r = requests.get(url, headers=headers)

        if r.status_code == 200:
            try:
                game = r.json()[appid]["data"]
                print(f"Adding {game['name']} to cache")

                game = {
                    "name":game["name"],
                    "image":game["header_image"],
                    "platform": "Steam",
                    "link":"https://store.steampowered.com/app/" + appid
                }

                store[appid] = game
                
                json.dump(store, open(config["dir"]+"steam/store/store.json","w"), indent=4)
                return store[appid]
            except:
                return "error"

        else:
            return "error"

def check(dir,type):
    dir = config["dir"] + dir
    if (type == "dir"):
        if not os.path.isdir(dir):
            os.mkdir(dir)

    elif (type == "file"):
        if not os.path.isfile(dir):
            file = open(dir, 'w')
            file.write("{}")
            file.close()

def getAllSteamGames():
    ## get games from each account
    for account in config["steam"]["games"]["accounts"]:
        url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=" + config["steam"]["key"] + f"&steamid={account}&format=json" 
        r = requests.get(url)
        try:
            games = r.json()["response"]["games"]
            manual = json.load(open(config["dir"]+"steam/accounts/"+account+"/"+config["steam"]["games"]["files"]["manual"]))
            
            games += manual

            games = sorted(games, key=lambda k: k['playtime_forever'])
            games = games[:config["steam"]["games"]["amount"]*-1:-1]

            gameData = []

            for item in range(len(games)):
                game = games[item]
                
                try:
                    platform = game["platform"]
                except:
                    platform = "Steam"

                error = False

                if platform == "Steam":
                    newGame = getSteamGame(game["appid"])
                    if newGame == "error":
                        error = True
                    else:
                        newGame["playtime_forever"] = game["playtime_forever"]

                else:
                    newGame = game

                if not error:
                    gameData.append(newGame)

                else:
                    print(f"Error getting game {game['appid']}")

            json.dump(gameData, open(config["dir"]+"steam/accounts/"+account+"/"+config["steam"]["games"]["files"]["cache"],"w"), indent=4)

        except Exception as e:
            print("Couldn't fetch games for " + account)
            traceback.print_exc()

def main():
    # Create files and directories if they don't exist

    dirs = [
        "", # base dir
        "steam/",
        "steam/store/",
        "steam/accounts/",
        "dev/"
    ]

    
    files = [
        "steam/store/store.json",
        "dev/projects.json"
    ]

    [check(dir,"dir") for dir in dirs]
    [check(file,"file") for file in files]

    [check("steam/accounts/"+account+"/","dir") for account in config["steam"]["games"]["accounts"]]

    [
        [check("steam/accounts/"+account+"/"+file,"file") for filetype, file in config["steam"]["games"]["files"].items()]
        for account in config["steam"]["games"]["accounts"]
    ]
    while True:
        getAllSteamGames()
        time.sleep(600)

if __name__ == "__main__":
    main()