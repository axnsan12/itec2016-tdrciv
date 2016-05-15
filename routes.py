"""
Routes and views for the bottle application.
"""

import init
import traceback
from bottle import view, default_app, redirect
from datetime import datetime
from time import strftime
from init import app, cork
from cork import AAAException, AuthException
from bottle import request, response, static_file
from model import User, Profile, Event, Interest, Comment, ProfileInterest, EventInterest, ProfileEvent
from datetime import timezone, datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from operator import itemgetter

def format_response(func):
	def wrapper(*args, **kwargs):
		body = {}
		message = None
		trace = None
		try:
			result = func(*args, **kwargs)
			if result is not None and not isinstance(result, dict):
				response.status = 500
				message = "Internal server error - bad response %s" % json.dumps(result)
			else:
				if result is not None and 'status' in result and ('data' in result or 'message' in result):
					body = result
				else:
					body['status'] = 'success'
					body['data'] = result if result is not None else { }
				
		except TypeError as e:
			if request.json is None and request.method != "GET":
				response.status = 400
				message = "Request body was expected but not found"
			else:
				raise
		except KeyError as e:
			message = "Missing required argument '%s'." % e.args[0]
			trace = traceback.format_exc()
			response.status = 400
		except AuthException as e:
			message = "Authentication exception: %s" % str(e)
			trace = traceback.format_exc()
			response.status = 401
		except AAAException as e:
			message = "Authorization exception: %s" % str(e)
			trace = traceback.format_exc()
			response.status = 403
		except IntegrityError as e:
			message = "Database integrity error: %s" % str(e)
			trace = traceback.format_exc()
			response.status = 409
		except NoResultFound as e:
			message = "No resource found at the given URL"
			trace = traceback.format_exc()
			response.status = 404
		#except SQLAlchemyError as e:
		#	message = "Database error: %s" % str(e)
		#	trace = traceback.format_exc()
		#	response.status = 500
		#except Exception as e:
		#	message = "A crepat - %s" % str(e)
		#	trace = traceback.format_exc()
		#	response.status = 500

		if message is not None:
			body['status'] = 'error'
			body['message'] = message
			body['trace'] = trace
		return body
	return wrapper

authorize = cork.make_auth_decorator(role="user", fail_redirect=None)
def current_user():
	return init.session.query(User).filter(User.username == cork.current_user.username).one()

def parse_interests(interests):
	new_interests = []
	interest_ids = []
	deleted_interest_ids = []
	for interest in interests:
		if 'id' in interest:
			if 'delete' not in interest or not interest['delete']:
				interest_ids.append(interest['id'])
			else:
				deleted_interest_ids.append(interest['id'])
		else:
			existent = init.session.query(Interest).filter(Interest.interest == interest['name']).one_or_none()
			if existent is None:
				new_interests.append(Interest(interest=interest['name']))
			else:
				interest_ids.append(existent.id)

	return interest_ids, new_interests, deleted_interest_ids

@app.route("/", method=['GET'])
def serve_index():
	return static_file('index.html', root='frontend/app')

@app.post('/api/register')
@format_response
def register():
	"""Send out registration email"""
	try:
		user = User(username=request.json['username'], email=request.json['email'])
		profile = Profile(name=request.json['displayName'])
		user.profile = profile
		interest_ids, new_interests, deleted_interests = parse_interests(request.json['interests'])
		if new_interests:
			profile.interests = new_interests
		init.session.add(user)
		init.session.flush()
		if interest_ids:
			init.session.add_all([ProfileInterest(profile_id=profile.id, interest_id=interest_id) for interest_id in interest_ids ])
			init.session.flush()
		cork.register(user.username, request.json['password'], user.email)
		init.session.commit()
		return { 'user_id': user.id, 'profile_id': profile.id }
	except IntegrityError as e:
		response.status = 409
		if str(e.args[0]).endswith("'username'"):
			return { 'status': 'error', 'message': 'Username is already registered', 'error': 'username_already_exists' }
		elif str(e.args[0]).endswith("'email'"):
			return { 'status': 'error', 'message': 'E-mail address is already registered', 'error': 'email_already_exists' }
		else: 
			raise

@app.post('/api/login')
@format_response
def login():
	if not cork.login(request.json['username'], request.json['password']):
		raise AuthException("incorrect username/password pair")
	return { 'success': True }

@app.get('/api/activate/:registration_code')
@format_response
def activate(registration_code):
	try:
		cork.validate_registration(registration_code)
	except:
		pass
	redirect('/#/login')
	return { 'success': True }

@app.post('/api/change_password')
@format_response
@authorize()
def change_password():
	corkuser = cork.current_user
	if cork.login(corkuser.username, request.json['currentPassword']):
		corkuser.update(pwd=request.json['newPassword'])
		return { 'success': True }
	else:
		raise AuthException("current password does not match")


@app.get('/api/user')
@format_response
@authorize()
def logged_in_user():
	user = current_user()
	return { 'id': user.id, 'username': user.username, 'email': user.email }

@app.get('/api/profile')
@format_response
@authorize()
def get_my_profile():
	return get_profile(-1)

@app.get('/api/profile/<user_id:int>')
@format_response
def get_profile(user_id=-1):
	if user_id < 0:
		profile = current_user().profile
	else:
		profile = init.session.query(Profile).filter(Profile.user_id == user_id).one()
	return profile.tojson()

@app.put('/api/profile')
@format_response
@authorize()
def update_my_profile():
	return update_profile(-1)

@app.put('/api/profile/<user_id:int>')
@format_response
@authorize()
def update_profile(user_id=-1):
	user = current_user()
	if user_id > 0 and user_id != user.id:
		cork.require(role="admin")

	profile = current_user().profile if user_id < 0 else init.session.query(Profile).filter(Profile.user_id == user_id).one()
	user_id = profile.user_id
	if 'displayName' in request.json:
		profile.name = request.json['displayName']

	if 'interests' in request.json:
		interest_ids, new_interests, deleted_interest_ids = parse_interests(request.json['interests'])
		if new_interests:
			profile.interests.extend(new_interests)
		if interest_ids:
			results = init.session.query(ProfileInterest.interest_id).filter(ProfileInterest.profile_id == profile.id, ProfileInterest.interest_id.in_(interest_ids)).all()
			existing_interest_ids = { r[0] for r in results }
			init.session.add_all([ProfileInterest(profile_id=profile.id, interest_id=interest_id) for interest_id in set(interest_ids) - existing_interest_ids ])
		if deleted_interest_ids:
			init.session.query(ProfileInterest).filter(ProfileInterest.profile_id == profile.id, ProfileInterest.interest_id.in_(deleted_interest_ids)).delete(synchronize_session=False)
			init.session.expire_all()

	init.session.add(profile)
	init.session.commit()
	return profile.tojson()
		

@app.post('/api/logout')
@format_response
def logout():
	cork.logout(success_redirect=None, fail_redirect=None)
	return { 'success': True }

@app.get('/api/interests')
@format_response
def list_interests():
	return { 'interests': [ interest.tojson() for interest in init.session.query(Interest).all()] }

@app.post('/api/interests')
@format_response
def insert_interests():
	interests = []
	for name in request.json['names']:
		interests.append(Interest(interest=name))
	
	init.session.add_all(interests)
	init.session.commit()
	return { 'ids': [interest.id for interest in interests] }

@app.get('/api/events')
@format_response
@authorize()
def list_events():
	user = current_user()
	now = datetime.utcnow().replace(tzinfo=timezone.utc)
	events = init.session.query(Event).outerjoin(ProfileEvent).outerjoin(Profile).filter((Event.start_time > now) | (Profile.user_id == user.id)).all()
	result = []
	joined_event_ids = { event.id for event in user.profile.events }
	my_interest_ids = { interest.id for interest in user.profile.rel_interests }
	for event in events:
		ev = event.tojson()
		ev['joined'] = event.id in joined_event_ids
		ev['users'] = [ { 'user_id': profile.user_id, 'username': profile.user.username, 'displayName': profile.name, 
				   'comment': event.users[profile].text, 'comment_id': event.users[profile].id } for profile in event.users ]
		interests = [ ]
		interests_in_common = 0
		for interest in event.rel_interests:
			ijs = interest.tojson()
			ijs['common'] = interest.id in my_interest_ids
			interests_in_common += 1 if ijs['common'] else 0
			interests.append(ijs)
		ev['interests'] = interests
		ev['commonInterests'] = interests_in_common
		ev['expired'] = event.start_time < now
		result.append(ev)

	return { 'events': sorted(result, key=lambda ev: (int(ev['expired']), -1 * ev['commonInterests'], ev['startTime'])) }

@app.post('/api/events')
@format_response
@authorize()
def create_event():
	user = current_user()
	event = Event(name=request.json['name'])
	now = datetime.utcnow().replace(tzinfo=timezone.utc)
	start_time = datetime.fromtimestamp(request.json['startTime'], timezone.utc)
	if start_time < now:
		now = now.strftime("%Y-%m-%d %H:%M")
		start_time = start_time.strftime("%Y-%m-%d %H:%M")
		return { 'status': 'error', 'message': 'Cannot create an event in the past (current %s vs event %s)' % (now, start_time), 'error': 'create_event_past_time' }
	interest_ids, new_interests, deleted_interests = parse_interests(request.json['interests'])
	if len(new_interests) + len(interest_ids) == 0:
		return { 'status': 'error', 'message': 'Event must target at least one interest', 'error': 'create_event_no_interests' }
	if new_interests:
		event.interests = new_interests
	
	comment = Comment(text=request.json['comment'])
	if len(comment.text) == 0:
		return { 'status': 'error', 'message': 'Event join comment must not be empty', 'error': 'create_event_no_comment' }
	event.users[user.profile] = comment
	event.start_time = start_time
	init.session.add(event)
	if interest_ids:
		init.session.flush()
		init.session.add_all([EventInterest(event_id=event.id, interest_id=interest_id) for interest_id in interest_ids ])
	init.session.commit()
	return { 'event_id': event.id, 'comment_id': comment.id }

@app.post('/api/events/<id:int>/join')
@format_response
@authorize()
def join_event(id):
	user = current_user()
	event = init.session.query(Event).filter(Event.id == id).one()
	now = datetime.utcnow().replace(tzinfo=timezone.utc)
	if event.start_time > now:
		comment = Comment(text=request.json['comment'])
		if len(comment.text) == 0:
			return { 'status': 'error', 'message': 'Event join comment must not be empty', 'error': 'join_event_no_comment' }

		if user.profile in event.users:
			return { 'status': 'error', 'message': 'You have already joined this event', 'error': 'join_event_already_member' }

		event.users[user.profile] = comment
		init.session.add(event)
		init.session.commit()
		return { 'comment_id': comment.id }
	else:
		now = now.strftime("%Y-%m-%d %H:%M")
		start = event.start_time.strftime("%Y-%m-%d %H:%M")
		return { 'status': 'error', 'message': 'Event start time has passed (current %s vs event %s)' % (now, start), 'error': 'join_event_past_start_time' }

@app.put('/api/comments/<id:int>')
@format_response
@authorize()
def update_comment(id):
	result = init.session.query(Comment).join(ProfileEvent).add_columns(Comment.id, Comment.text, ProfileEvent.profile_id, ProfileEvent.event_id).filter(Comment.id == id).one()
	profile = current_user().profile
	if profile.id != result.profile_id:
		cork.require(role="admin")

	comment = Comment(id=result.id, text=request.json['text'])
	init.session.merge(comment)
	init.session.commit()
	return { 'id': comment.id, 'text': comment.text, 'profile_id': result.profile_id, 'event_id': result.event_id }

@app.post('/api/events/<id:int>/unjoin')
@format_response
@authorize()
def unjoin_event(id):
	user = current_user()
	event = init.session.query(Event).filter(Event.id == id).one()
	if user.profile not in event.users:
		return { 'status': 'error', 'message': 'You have not joined this event', 'error': 'unjoin_event_not_a_member' }
	del event.users[user.profile]
	init.session.add(event)

	result = { 'event_deleted': False, 'success': True }
	if len(event.users) == 0:
		init.session.delete(event)
		result['event_deleted'] = True
	init.session.commit()
	return result

@app.get('/api/users')
@format_response
@authorize()
def list_users():
	cork.require(role="admin")
	return { 'users': [{ 'username': user[0], 'role': user[1], 'email': user[2] } for user in cork.list_users()] }

@app.route("/<url:path>", method=['GET'])
def serve_frontend(url):
	print(url)
	response = static_file(url, root='frontend/app')
	response.set_header("Cache-Control", "public, max-age=604800")
	return response