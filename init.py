import bottle
import os
import sys
from os import getenv
from bottle import request, response
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base
from beaker.middleware import SessionMiddleware
from cork import Cork
from cork.backends import SqlAlchemyBackend
from cork import AAAException, AuthException

app = bottle.default_app()
bottle.debug(True)

@app.hook('after_request')
def enable_cors():
	"""
	You need to add some headers to each request.
	Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
	"""
	response.headers['Access-Control-Allow-Origin'] = 'http://unified.tdr'
	response.headers['Access-Control-Allow-Credentials'] = "true";
	response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
	response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Cookie, Content-Type, X-Requested-With, X-CSRF-Token, Cookie'

@app.route("/<url:re:.+>", method=['OPTIONS'])
def allow_options(url):
	return ""

Base = declarative_base()

connection_string = getenv('MYSQLCONNSTR_itec2016')
arg_name = { 'Database': 'database', 'User Id': 'user', 'Data Source': 'host', 'Password': 'password' }
kwargs = { arg_name[key] : val for (key, val) in [arg.split('=') for arg in connection_string.split(';')]}
kwargs['port'] = 3306 if 'port' not in kwargs else kwargs['port']
connection_string = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}".format(**kwargs)
print(connection_string)
engine = create_engine(connection_string, echo=True)

plugin = sqlalchemy.Plugin(
	engine, # SQLAlchemy engine created with create_engine function.
	Base.metadata, # SQLAlchemy metadata, required only if create=True.
	keyword='db', # Keyword used to inject session database in a route (default 'db').
	create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
	commit=True, # If it is true, plugin commit changes after route is executed (default True).
	use_kwargs=False # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
)

app.install(plugin)

cork_mysql = SqlAlchemyBackend(connection_string, initialize=True)
cork = Cork(backend=cork_mysql, email_sender='danpulea12@gmail.com', smtp_url='ssl://danpulea12@gmail.com:parola12@smtp.gmail.com:465')

session_opts = {
	'session.cookie_expires': True,
	'session.encrypt_key': 'please use a random key and keep it secret!',
	'session.httponly': True,
	'session.timeout': 3600 * 24,  # 1 day
	'session.type': 'cookie',
	'session.validate_key': True,
}

session_app = SessionMiddleware(app, session_opts)