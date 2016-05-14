"""
Routes and views for the bottle application.
"""

import traceback
from bottle import view, default_app
from datetime import datetime

from init import app, cork, engine
from cork import AAAException, AuthException
from bottle import request, response, static_file
from model import Profile, Event, Interest, Comment

from sqlalchemy.orm import scoped_session, sessionmaker

def format_response(func):
	def wrapper(*args, **kwargs):
		body = {}
		message = None
		try:
			result = func(*args, **kwargs)
			body['status'] = 'success'
			if result is not None and not isinstance(result, dict):
				response.status = 500
				message = "Internal server error - bad response %s" % json.dumps(result)
			else:
				body['data'] = result if result is not None else { }
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
		# except Exception as e:
		#	message = "A crepat - %s" % str(e)

		if message is not None:
			body['status'] = 'error'
			body['message'] = message
			body['trace'] = trace
		return body
	return wrapper

authorize = cork.make_auth_decorator(role="user")

@app.route("/", method=['GET'])
def serve_index():
	return static_file('index.html', root='frontend/app')

@app.post('/api/register')
@format_response
def register():
	"""Send out registration email"""
	cork.register(request.json['username'], request.json['password'], request.json['email'])
	return { 'success': True }

@app.post('/api/login')
@format_response
def login():
	if not cork.login(request.json['username'], request.json['password']):
		raise AuthException("incorrect username/password pair")
	return { 'success': True }

@app.get('/api/activate/:registration_code')
@format_response
def activate(registration_code):
	cork.validate_registration(registration_code)
	cork.list_users
	return { 'success': True }

@app.get('/api/user')
@format_response
def logged_in_user():
	user = cork.current_user
	return { 'username': user.username, 'email': user.email_addr, 'role': user.role }

@app.post('/api/logout')
@format_response
def logout():
	cork.logout(success_redirect=None, fail_redirect=None)
	return { 'success': True }

@app.get('/api/users')
@format_response
def list_users():
	cork.require(username=None, role="admin")
	return { 'users': [{ 'username': user[0], 'role': user[1], 'email': user[2] } for user in cork.list_users()] }


@app.get('/api/test_db')
@format_response
def test_db():
	session = scoped_session(sessionmaker(bind=engine, autoflush=False))
	p1 = Profile(name="profile1", username="axnsan")
	p2 = Profile(name="profile2", username="tdr")
	e = Event(name="event")
	i1 = Interest(interest="interest1")
	i2 = Interest(interest="interest2")
	i3 = Interest(interest="interest3")
	e.users[p1] = Comment(text="comment 1")
	e.users[p2] = Comment(text="comment 2")
	e.interests.append(i1)
	e.interests.append(i3)
	session.add(e)
	session.commit()
	return { 'success': True }

@app.route('/api/test')
def test():
	return dict(
		status='success',
		data=[
		{ 
			'id': 1, 
			'name': 'API Bind', 
			'description': 'This is a very long description. This is a very long description. This is a very long description. This is a very long description. This is a very long description. ', 
			'image': 'http://imgsv.imaging.nikon.com/lineup/lens/zoom/normalzoom/af-s_dx_18-140mmf_35-56g_ed_vr/img/sample/sample1_l.jpg',
			'count': 69 
		},
		{ 
			'id': 2, 
			'name': 'API Bind 2', 
			'description': 'This is also a very long description. This is a also very long description. This is also a very long description. This is a very long description. This is a very long description. ', 
			'image': 'http://colorvisiontesting.com/images/plate%20with%205.jpg',
			'count': 42
		}
		]
	)



@app.route("/<url:path>", method=['GET'])
def serve_frontend(url):
	print(url)
	return static_file(url, root='frontend/app')