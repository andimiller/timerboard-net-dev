from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Set up SQLAlchemy
db = SQLAlchemy()
engine = create_engine("postgres://timerboard-postgres/timerboard")
db_session = scoped_session(sessionmaker(autocommit=False,
	autoflush=False,
	bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
	import models
	Base.metadata.create_all(bind=engine)

def get_visible_timers(current_user):
	return Timer.query.filter(Timer.visibility.overlap(current_user.get_access_ids())).all()

def get_owned_timers(current_user):
	return Timer.query.filter(Timer.owner == current_user.CharacterID).all()
