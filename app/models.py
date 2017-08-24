from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base
import time


class Group(Base):
	__tablename__ = 'groups'
	id = Column(Integer, primary_key=True)
	name = Column(String(24))
	admins = Column(ARRAY(Integer))
	members = Column(ARRAY(Integer))

	def __init__(self, id=None, name=None, admins=None, members=None):
		self.id = id
		self.name = name
		self.admins = admins
		self.members = members


class Timer(Base):
	__tablename__ = 'timers'
	id = Column(Integer, primary_key=True)
	user = Column(Integer)
	system = Column(String(12))
	planet = Column(String(6))
	moon = Column(Integer)
	owner = Column(String(64))
	time = Column(DateTime)
	notes = Column(String(256))
	visibility = Column(ARRAY(Integer))
	type = Column(String(32))

	def __init__(self, id=None, user=None, system=None, planet=None, moon=None, owner=None, time=None, notes=None, visibility=None, type=None):
		self.id=id
		self.user=user
		self.system=system
		self.planet=planet
		self.moon=moon
		self.owner=owner
		self.time=time
		self.notes=notes
		self.visibility=visibility
		self.type = type

	def __repr__(self):
		return '<Timer %r>' % (self.id)

	def to_unix_time(self):
		return int(time.mktime(self.time.timetuple()))

	@property
	def json(self):
		return dict(id=self.id, user=self.user, system=self.system, planet=self.planet, moon=self.moon, owner=self.owner, time=self.to_unix_time(), notes=self.notes, visibility=self.visibility, type=self.type)


class User:
	def __init__(self, data):
		print "New user:", data
		self.__dict__.update(data)
		self.groups = self.get_groups()

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.CharacterName

	def get_groups(self):
		return Group.query.filter(Group.members.contains([self.CharacterID])).all()

	def get_access_map(self):
		results = {}
		results[self.CharacterID] = self.CharacterName
		results[self.CorporationID] = self.CorporationName
		if hasattr(self, "AllianceID"):
			results[self.AllianceID] = self.AllianceName
		for group in self.groups:
			results[0-group.id] = group.name
		return results

	def group_ids(self):
		return map(lambda x:0-x.id, self.groups)

	def get_access_ids(self):
		if not hasattr(self, "groups"):
			self.groups = self.get_groups()
		if hasattr(self, "AllianceID"):
			return [self.CharacterID, self.CorporationID, self.AllianceID] + self.group_ids()
		else:
			return [self.CharacterID, self.CorporationID] + self.group_ids()
