import smtplib, json, traceback
from flask import Flask, render_template, jsonify, request, redirect, send_from_directory,send_file
from flask_cors import CORS
from gevent.pywsgi import WSGIServer
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from dotenv import dotenv_values

env = dotenv_values(".env")
app = Flask('app')
app.url_map.strict_slashes = False

CORS(app)

config = json.load(open("config.json"))
config["email"]["login"]["password"] = env["EMAIL_PASSWORD"]


@app.route('/')
def index():
    return """
    <p>Whoa, it's an API I made for my basic backend - Epic</p>
    <ul>
        <li>
            <a href = "/projects">Prjects</a>
        </li>
        <li>
            <a href = "/steam/76561198363384787">Top Games</a>
        </li> 
    </ul>
    <a href="https://jck.cx/g/api">API + Backend Source</a>
    """

@app.route("/steam/<path:account>")
def steam(account):
    games = config["dir"] + "steam/accounts/" + account + "/games.json"
    gamesFile = json.load(open(games))
    return jsonify(gamesFile)

@app.route("/steam/<path:account>x<path:count>")
def steamCount(account,count):
    games = config["dir"] + "steam/accounts/" + account + "/games.json"
    gamesFile = json.load(open(games))[:int(count)]
    return jsonify(gamesFile)

@app.route("/projects")
def projects():
    projects = config["dir"] + "dev/projects.json"
    projectsFile = json.load(open(projects))
    return jsonify(projectsFile)

@app.route("/emailform", methods=["POST"])
def emailform():
    prevURL = request.referrer + "contact"
    try:
        name = request.form.get("name")
        sender = name +  " <"+request.form.get("email")+">"
        body = request.form.get("emailBody")
        user = request.form.get("user")
        if user != None:
            if user in config["email"]["recievers"]:
                reciever = config["email"]["recievers"]["email"]
            else:
                return redirect(prevURL + "?sent=false&message=invalidUser")
        else:
            reciever = [value for user, value  in config["email"]["recievers"].items() if "default" in value and value["default"]][0]["email"]

        subject = "New Message from " + name

        if sender == "" or name.replace(" ","") == "" or body == "":
            return redirect(prevURL + "?sent=false")

        else:
            body = f"From: {sender}\n\n{body}"
            server = smtplib.SMTP(config["email"]["login"]["server"], config["email"]["login"]["port"])
            server.ehlo()
            server.starttls()
            server.login(config["email"]["login"]["email"], config["email"]["login"]["password"])

            msg = MIMEMultipart()
            msg['From'] = name + " <"+config["email"]["login"]["email"] + ">"
            msg['To'] = reciever
            msg['Subject'] = subject
            msg['reply-to'] = sender

            msg.attach(MIMEText(body, 'plain'))

            text = msg.as_string()

            server.sendmail(config["email"]["login"]["email"], reciever, text)
            server.close()

            return redirect(prevURL + "?sent=true")

    except Exception:
        print(traceback.format_exc())
        return redirect(prevURL + "?sent=false")

if __name__ == "__main__":
    http_server = WSGIServer((config["flask"]["host"],config["flask"]["port"]), app)
    http_server.serve_forever()
    