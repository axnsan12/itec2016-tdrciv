from sqlalchemy import Table, Column, Integer, Unicode, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

from init import engine

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

class Comment(Base, _BaseMixin):
	__tablename__ = 'comments'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	text = Column(Unicode(256), unique=False)
	# relations
	profileevent = relationship("ProfileEvent", backref='comment')

class Profile(Base, _BaseMixin):
	__tablename__ = 'profiles'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	# username = Column(Unicode(128), ForeignKey('users.username', ondelete='CASCADE'), nullable = False)
	name = Column(Unicode(128), unique=True)
	# relations
	rel_profileevent = relationship("ProfileEvent", collection_class=attribute_mapped_collection('event'),
								  cascade='all,delete-orphan',
								  backref='profile',
								  )
	events = association_proxy('rel_profileevent', 'comment', creator=lambda event, comment: ProfileEvent(event=event, comment=comment))

	rel_interests = relationship("Interest", secondary=lambda: profileinterests_table)

	interests = association_proxy('rel_interests', 'interest', creator=lambda interest: interest)

class Event(Base, _BaseMixin):
	__tablename__ = 'events'
	# columns
	id = Column(Integer, primary_key=True, autoincrement=True)
	name = Column(Unicode(256), unique=False)

	# relations
	rel_profileevent = relationship("ProfileEvent", collection_class=attribute_mapped_collection('profile'),
								  cascade='all,delete-orphan',
								  backref='event',
								  )
	users = association_proxy('rel_profileevent', 'comment', creator=lambda profile, comment: ProfileEvent(profile=profile, comment=comment))

	rel_interests = relationship("Interest", secondary=lambda: eventinterests_table)

	interests = association_proxy('rel_interests', 'interest', creator=lambda interest: interest)

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

eventinterests_table = Table('event_interest', Base.metadata,
	Column('event_id', Integer, ForeignKey(Event.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False),
	Column('interest_id', Integer, ForeignKey(Interest.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False)
)

profileinterests_table = Table('profile_interest', Base.metadata,
	Column('profile_id', Integer, ForeignKey(Profile.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False),
	Column('interest_id', Integer, ForeignKey(Interest.__tablename__ + '.id', ondelete='CASCADE'), primary_key=True, nullable=False)
)

#class ProfileInterest(Base, _BaseMixin):
#	__tablename__ = 'profile_interest'
#	id = Column(Integer, primary_key=True, autoincrement=True)
#	profile_id = Column(Integer, ForeignKey(Profile.__tablename__ + '.id', ondelete='CASCADE'), nullable=False)
#	interest_id = Column(Integer, ForeignKey(Interest.__tablename__ + '.id', ondelete='CASCADE'), nullable=False)

#class EventInterest(Base, _BaseMixin):
#	__tablename__ = 'event_interest'
#	id = Column(Integer, primary_key=True, autoincrement=True)
#	profile_id = Column(Integer, ForeignKey(Event.__tablename__ + '.id', ondelete='CASCADE'), nullable=False)
#	interest_id = Column(Integer, ForeignKey(Interest.__tablename__ + '.id', ondelete='CASCADE'), nullable=False)


Base.metadata.create_all(engine)

##############################################################################
# TESTS (showing usages)
#
# Requirements:
#  - list all groups of the user: user.groups (use keys)
#  - list all users of the group: group.users (use keys)
#  - get all users ordered (grouped) by group with the role title
##############################################################################

#def _requirement_get_user_groups(user):
#    return user.groups.keys()

#def _requirement_get_group_users(group):
#    return group.users.keys()

#def _requirement_get_all_users_by_group_with_role():
#    qry = session.query(Group).order_by(Group.name)
#    res = []
#    for g in qry.all():
#        for u, r in sorted(g.users.items()):
#            value = (g.name, u.name, r.name)
#            res.append(value)
#    return res

#def _test_all_requirements():
#    print '--requirement: all-ordered:'
#    for v in _requirement_get_all_users_by_group_with_role():
#        print v

#    print '--requirement: user-groups:'
#    for v in session.query(User).order_by(User.id):
#        print v, " has groups: ",  _requirement_get_user_groups(v)

#    print '--requirement: group-users:'
#    for v in session.query(Group).order_by(Group.id):
#        print v, " has users: ",  _requirement_get_group_users(v)

## create db schema
#Base.metadata.create_all(engine)

###############################################################################
## CREATE TEST DATA
###############################################################################

## create entities
#u_peter = User(name='u_Peter')
#u_sonja = User(name='u_Sonja')
#g_sales = Group(name='g_Sales')
#g_wales = Group(name='g_Wales')
#r_super = Role(name='r_Super')
#r_minor = Role(name='r_Minor')

## helper functions
#def _get_entity(entity, name):
#    return session.query(entity).filter_by(name=name).one()
#def get_user(name):
#    return _get_entity(User, name)
#def get_group(name):
#    return _get_entity(Group, name)
#def _checkpoint():
#    session.commit()
#    session.expunge_all()
#    _test_all_requirements()
#    session.expunge_all()
#    print '-' * 80


## test: **ADD**
#u_peter.groups[g_wales] = r_minor # add
#g_wales.users[u_sonja] = r_super # add
#g_sales.users[u_peter] = r_minor # add
#session.add(g_wales)
##session.add(g_sales)
#_checkpoint()

## test: **UPDATE**
#u_peter = get_user('u_Peter')
#assert u_peter.name == 'u_Peter' and len(u_peter.groups) == 2
#assert len(u_peter.groups) == 2
#g_wales = get_group('g_Wales')
#g_wales.users[u_peter] = r_super # update
#_checkpoint()

## test: **DELETE**
#u_peter = get_user('u_Peter')
#assert u_peter.name == 'u_Peter' and len(u_peter.groups) == 2
#g_wales = get_group('g_Wales')
#del u_peter.groups[g_wales] # delete
#_checkpoint()