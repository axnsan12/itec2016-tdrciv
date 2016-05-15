import bottle
import os
import sys
from os import getenv
from bottle import request, response
from bottle.ext import sqlalchemy
from beaker.middleware import SessionMiddleware
from cork import Cork
from cork.backends import SqlAlchemyBackend
from cork import AAAException, AuthException

from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

app = bottle.default_app()
bottle.debug(True)

@app.hook('after_request')
def enable_cors():
	"""
	You need to add some headers to each request.
	Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
	"""
	allowed = [ 'http://unified.tdr', 'http://unitaste.tdr', 'http://unitaste.ro' ]
	origin = request.get_header("Origin")
	if origin is not None:
		for host in allowed:
			if origin.startswith(host):
				response.headers['Access-Control-Allow-Origin'] = host;
				response.headers['Access-Control-Allow-Credentials'] = "true";
				response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, OPTIONS'
				response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Cookie, Content-Type, X-Requested-With, X-CSRF-Token'
				break

@app.route("/<url:re:.+>", method=['OPTIONS'])
def allow_options(url):
	return ""

Base = declarative_base()

kwargs = { 'database': 'default', 'user': 'root', 'password': '', 'host': 'localhost', 'port': 3306 }
if 'MYSQLCONNSTR_itec2016' in os.environ:
	connection_string = getenv('MYSQLCONNSTR_itec2016')
	arg_name = { 'Database': 'database', 'User Id': 'user', 'Data Source': 'host', 'Password': 'password' }
	kwargs.update({ arg_name[key] : val for (key, val) in [arg.split('=') for arg in connection_string.split(';')]})
connection_string = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}".format(**kwargs)
engine = create_engine(connection_string, echo=False, pool_size=2, max_overflow=3)

plugin = sqlalchemy.Plugin(
	engine, # SQLAlchemy engine created with create_engine function.
	Base.metadata, # SQLAlchemy metadata, required only if create=True.
	keyword='db', # Keyword used to inject session database in a route (default 'db').
	create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
	commit=True, # If it is true, plugin commit changes after route is executed (default True).
	use_kwargs=False # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
)

app.install(plugin)

_sessionmaker = sessionmaker(bind=engine, autoflush=False)
session = None # type: Session
@app.hook('before_request')
def open_session():
	global session
	if session is not None:
		session.close()
		session = None
	session = _sessionmaker()

@app.hook('after_request')
def close_session():
	global session
	if session is not None:
		session.close()
		session = None

cork_mysql = SqlAlchemyBackend(connection_string, initialize=True, pool_size=1, max_overflow=1)
cork = Cork(backend=cork_mysql, email_sender='cristian.vijdea@gmail.com', smtp_url='ssl://cristian.vijdea@gmail.com:itec2016web@smtp.gmail.com:465')

session_opts = {
	'session.cookie_expires': True,
	'session.encrypt_key': 'please use a random key and keep it secret!',
	'session.httponly': True,
	'session.timeout': 3600 * 24,  # 1 day
	'session.type': 'cookie',
	'session.validate_key': True,
}

session_app = SessionMiddleware(app, session_opts)

def wsgi_app():
	"""Returns the application to make available through wfastcgi. This is used
	when the site is published to Microsoft Azure."""
	return app

import routes