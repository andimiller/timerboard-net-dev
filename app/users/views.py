from flask import Blueprint, render_template, g, request, redirect, flash, abort
from flask import jsonify
from app.models import *
from app.database import db_session
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask import current_app as app

mod = Blueprint('users', __name__, template_folder='templates')

import json, datetime, re
import arrow

regionmap = {}
with open("system2region.csv", "r") as regionfile:
	for line in regionfile:
		k,v = line.split(",")
		regionmap[k]=v.strip()



def query_timers_by_ids(ids):
	return Timer.query.filter(Timer.visibility.contains(ids)).all()

@mod.route("/about")
def about():
	return render_template("about.html")


def gettimers():
	return Timer.query.filter(Timer.visibility.overlap(current_user.get_access_ids())).filter(Timer.time > arrow.utcnow().replace(hours=-2).naive).all()

@mod.route("/")
def index():
    if current_user.is_anonymous():
	    return render_template("index_guest.html")
    else:
	    return render_template("index.html", timers=gettimers())

@mod.route("/api/timers")
@login_required
def timers():
    timers = map(lambda x: x.json, gettimers())
    m = current_user.get_access_map()
    for timer in timers:
        timer["region"] = regionmap[timer["system"]]
    for timer in timers:
        timer["visibility"] = filter(lambda x: x in m, timer["visibility"])
        timer["visibility"] = map(lambda x:m[x], timer["visibility"])
    for timer in timers:
        if timer["user"] == current_user.CharacterID:
            timer["yours"] = True
    for timer in timers:
        if timer["moon"]==0:
            timer["moon"]="-"
    return jsonify(timers=timers)


@mod.route("/groups")
@login_required
def groups():
	return render_template("groups.html")

systemlist = []
with open("systems.json", "r") as systemsfile:
	systemlist = json.loads(systemsfile.read())

@mod.route("/post", methods=["GET", "POST"])
@login_required
def post():
	if request.method == "GET":
		return render_template("post.html")
	if request.method == "POST":
		results = map(lambda x:request.form.get(x, ""), ["system", "planet", "moon", "owner", "time", "notes", "type"])
		sharedwith = request.form.getlist("sharewith")
		for share_target in sharedwith:
			if int(share_target) not in current_user.get_access_ids():
				flash("I can't let you do that Dave.", "danger")
				return redirect("/")
		sharedwith = sharedwith+[current_user.CharacterID]
		if ("reltime" in request.form) and request.form["reltime"]:
			if len(results[4])>0:
				flash("Please pick an absolute or relative time", "danger")
				return redirect("/post")
			reltime = request.form["reltime"].lower()
			kwargs = {
					"days": "(\d+)d",
					"hours": "(\d+)h",
					"minutes": "(\d+)m",
					"seconds": "(\d+)s"
				}
			for key, value in kwargs.items():
				kwargs[key] = re.search(value, reltime)
				if kwargs[key]:
					kwargs[key] = int(kwargs[key].groups()[0])
				else:
					del kwargs[key]
			results[4] = datetime.datetime.now() + datetime.timedelta(**kwargs)
		# checks
		if results[0] not in systemlist:
			flash("%s is not a valid system" % results[0], "danger")
			return redirect("/post")
		if len(results[1])<1:
			flash("Please enter a planet.", "danger")
			return redirect("/post")
		if results[2]=="":
			results[2]="0"
		if len(results[3])<1:
			flash("Please enter an owner.", "danger")
			return redirect("/post")
		if results[4]=="":
			flash("Please enter a timer.", "danger")
			return redirect("/post")
		if results[6] not in ["Station Shield", "Station Armour", "IHub Shield", "IHub Armour", "POS", "Custom"]:
			flash("Please select a timer type from the dropdown", "danger")
			return redirect("/post")
		newtimer = Timer(user=current_user.CharacterID, system=results[0], planet=results[1], moon=results[2], owner=results[3], time=results[4], notes=results[5], visibility=map(lambda x:int(x), sharedwith), type=results[6])

		db_session.add(newtimer)
		db_session.commit()
		db_session.expire_all()
		flash("Timer created.", "success")
		return redirect("/")


@mod.route('/systems')
@login_required
def systems():
	term = request.args.get('term')
	results = filter(lambda x:x.lower().startswith(term.lower()), systemlist)
	return json.dumps(results)

@mod.route("/delete/<id>")
@login_required
def delete(id):
	target = Timer.query.filter_by(id=id).first()
	if target==None:
		abort(404)
	if target.user != current_user.CharacterID:
		flash("You can't delete other people's timers.", "warning")
		redirect("/")
	db_session.delete(target)
	db_session.commit()
	flash("Timer successfully deleted.", "success")
	return redirect("/")

