from sqlalchemy import Table, Column, Integer, Unicode, ForeignKey, types
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import datetime, timezone
from init import engine
import time

# Configure test data SA
Base = declarative_base()

class _BaseMixin(object):
	"""
	A helper mixin class to set properties on object creation.

	Also provides a convenient default __repr__() function, but be aware that
	also relationships are printed, which might result in loading the relation
	objects from the database
	"""
	def __init__(self, **kwargs):
		for k, v in kwargs.items():
			setattr(self, k, v)

	def __repr__(self):
		return "<%s(%s)>" % (self.__class__.__name__,
			', '.join('%s=%r' % (k, self.__dict__[k])
					  for k in sorted(self.__dict__)
					  if '_' != k[0]
					  #if '_sa_' != k[:4] and '_backref_' != k[:9]
					  )
			)


class UTCDateTime(types.TypeDecorator):
	impl = types.Integer

	def process_bind_param(self, value, engine):
		if value is not None:
			ret = value.replace(tzinfo=timezone.utc)
			print("write into db " + str(time.mktime(ret.timetuple())))
			return str(value.timestamp())

	def process_result_value(self, value, engine):
		if value is not None:
			print("extract from db " + str(value))
			return datetime.fromtimestamp(value, timezone.utc)
			print(value.year, value.month, value.day,
							value.hour, value.minute, value.second,
							value.microsecond)
			ret = datetime(value.year, value.month, value.day,
							value.hour, value.minute, value.second,
							value.microsecond)
			print("extract from db 2 " + str(time.mktime(ret.timetuple())))
			ret = ret.astimezone(pytz.utc)
			print("parsed value from db to " + str(time.mktime(ret.timetuple())))
			return ret

class Comment(Base, _BaseMixin):
	__tablename__ = 'comments'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	text = Column(Unicode(256), unique=False)
	# relations
	profileevent = relationship("ProfileEvent", backref='comment')

	def tojson():
		return

class User(Base, _BaseMixin):
	__tablename__ = 'users2'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	username = Column(Unicode(128), unique=True, nullable=False)
	email = Column(Unicode(128), unique=True, nullable=False)
	blocked = Column(Integer, nullable=False, server_default='0')
	# relations
	profile = relationship("Profile", uselist=False, back_populates="user")

class Profile(Base, _BaseMixin):
	__tablename__ = 'profiles'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(Integer, ForeignKey(User.__tablename__ + '.id', ondelete='CASCADE'), nullable=False)
	name = Column(Unicode(128), unique=True)
	# relations
	rel_profileevent = relationship("ProfileEvent", collection_class=attribute_mapped_collection('event'),
								  cascade='all,delete-orphan',
								  backref='profile',
								  )
	events = association_proxy('rel_profileevent', 'comment', creator=lambda event, comment: ProfileEvent(event=event, comment=comment))

	rel_interests = relationship("Interest", secondary=lambda: profileinterests_table)

	interests = association_proxy('rel_interests', 'interest', creator=lambda interest: interest)
	user = relationship("User", back_populates="profile")

	def tojson(self):
		return { 'id': self.id, 'user_id': self.user_id, 'displayName': self.name, 'interests': [ interest.tojson() for interest in self.rel_interests ] }

class Event(Base, _BaseMixin):
	__tablename__ = 'events'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(Unicode(256), unique=False)
	start_time = Column(UTCDateTime, nullable=False)

	# relations
	rel_profileevent = relationship("ProfileEvent", collection_class=attribute_mapped_collection('profile'),
								  cascade='all,delete-orphan',
								  backref='event',
								  )
	users = association_proxy('rel_profileevent', 'comment', creator=lambda profile, comment: ProfileEvent(profile=profile, comment=comment))

	rel_interests = relationship("Interest", secondary=lambda: eventinterests_table)

	interests = association_proxy('rel_interests', 'interest', creator=lambda interest: interest)

	def tojson(self):
		return { 'id': self.id, 'name': self.name, 'startTime':  self.start_time.timestamp() }

class ProfileEvent(Base, _BaseMixin):
	__tablename__ = 'profile_event'
	# columns
	profile_id = Column(Integer, ForeignKey(Profile.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False)
	event_id = Column(Integer, ForeignKey(Event.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False)
	comment_id = Column(Integer, ForeignKey(Comment.__tablename__ + '.id', ondelete='CASCADE'), nullable=False)


class Interest(Base, _BaseMixin):
	__tablename__ = 'interests'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	interest = Column(Unicode(128), unique=True)

	def tojson(self):
		return { 'id': self.id, 'name': self.interest }

eventinterests_table = Table('event_interest', Base.metadata,
	Column('event_id', Integer, ForeignKey(Event.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False),
	Column('interest_id', Integer, ForeignKey(Interest.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False)
)


profileinterests_table = Table('profile_interest', Base.metadata,
	Column('profile_id', Integer, ForeignKey(Profile.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False),
	Column('interest_id', Integer, ForeignKey(Interest.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False)
)

Base.metadata.create_all(engine)

class EventInterest(Base, _BaseMixin):
	__table__ = Base.metadata.tables['event_interest']

class ProfileInterest(Base, _BaseMixin):
	__table__ = Base.metadata.tables['profile_interest']
