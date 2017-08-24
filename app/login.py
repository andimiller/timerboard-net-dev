from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import url_for
from flask import current_app as app
import requests
from requests.auth import HTTPBasicAuth
from flask import request, jsonify, redirect, flash, session
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
import eveapi
import redis_wrap
from timerboard.main import load_user
from timerboard.models import *

import json

mod = Blueprint('login', __name__, template_folder='templates')

api = eveapi.EVEAPIConnection()

users = redis_wrap.get_hash("timerboard_net_users")



@mod.route("/login")
def redirect_route():
	config = app.myconfig
	print app.config
	req = requests.Request("GET", config["CCP_SSO_DOMAIN"]+config["CCP_SSO_AUTHORIZE"], params={
		"response_type": "code",
		"redirect_uri": config["CCP_SSO_CALLBACK"],
		"client_id": config["CCP_SSO_CLIENTID"],
		"scope": "",
		"state": "stategoeshere"
		})
	req = req.prepare()
	print req.url

	return redirect(req.url)

@mod.route("/login/callback")
def ccp_sso_callback():
	config = app.myconfig
	code = request.args.get("code", "")
	state = request.args.get("state", "")
	req = requests.post(config["CCP_SSO_DOMAIN"]+config["CCP_SSO_TOKEN"], params={
			"grant_type": "authorization_code",
			"code": code
		}, auth=HTTPBasicAuth(config["CCP_SSO_CLIENTID"], config["CCP_SSO_SECRET"]))
	tokendata = req.json()
	print tokendata
	# get character data
	print config["CCP_SSO_DOMAIN"]+config["CCP_SSO_VERIFY"]
	print "Bearer "+tokendata["access_token"]
	chardata = requests.get(config["CCP_SSO_DOMAIN"]+config["CCP_SSO_VERIFY"], headers={"Authorization": "Bearer "+tokendata["access_token"]}).json()

	# authenticated, get extra data
	r = api.eve.CharacterInfo(characterID=chardata["CharacterID"])
	results = {}
	results["CharacterID"] = chardata["CharacterID"]
	results["CharacterName"] = chardata["CharacterName"]
	results["CorporationID"] = r.corporationID
	results["CorporationName"] = r.corporation
	if hasattr(r, "alliance"):
		results["AllianceID"] = r.allianceID
		results["AllianceName"] = r.alliance
	uid = results["CharacterName"]
	users[uid] = json.dumps(results)
	login_user(load_user(uid))
	flash("Logged in as %s" % results["CharacterName"], "success")
	return redirect("/")

@mod.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect("/")
