# JackBailey API + Backend

A simple flask API and json based backend to list mine and other's steam games, send emails with contact forms and get projects easily

---
### Easily configured with a json file


#### **`config.json`**

```
{
    "dir":"data/",
    "steam":{
        "games" :{
            "amount": 80,
            "accounts": [
                "steamIdsHere"                
            ],
            "files": {
                "cache":"games.json",
                "manual":"manual.json"
            }
        }
    },
    "flask":{
        "port":flask port,
        "host":"flask host"
    },
    "email":{
        "recievers":{
            "one":{
                "email":"hello@example.com",
                "default":true
            },
            "two":{
                "email":"me@example.com"
            }
        },
        "login":{
            "email":"loginEmail",
            "server":"",
            "port":587
        }
    }
}
```

#### **`.env`**
```
STEAM=STEAMAPIKEY #get from https://steamcommunity.com/dev/apikey

EMAIL_PASSWORD=PASSWORD123
```