from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from requests import request
from modules.database import Database
from modules.args import createuser_args, getuser_args, authentication_args
from datetime import datetime

import secrets

class Session:
    ONE_IP_PER_TOKEN = True
    TOKEN_EXPIRATION = True
    TOKEN_LIFETIME_MINUTES = 1

    initialized = False
    allow_authentication = True

    active_sessions = []

    def Initialize():
        Session.initialized = True
    
    def TokenExists(token):
        for data in Session.active_sessions:
            if 'token' in data and data['token'] == token:
                return True
        return False
    
    def GetSessionByToken(token):
        for data in Session.active_sessions:
            if 'token' in data and data['token'] == token:
                return data
        return None 

    def CheckAuthorization(token, ip_address):
        if token == "" or not Session.TokenExists(token):
            return False
        _session = Session.GetSessionByToken(token)
        if Session.ONE_IP_PER_TOKEN and _session['ip_address'] != ip_address:
            return False
        exp = datetime.fromisoformat(_session['exp'])
        if Session.TOKEN_EXPIRATION and exp < datetime.utcnow():
            return False
        return True

    def auth_required(func):
        """[Decorator] Checking if the function call is authorized.
        \nHas to be called inside of an endpoint."""
        def wrapper(*args, token="", **kwargs):
            if not Session.CheckAuthorization(token, request.remote_addr):
                abort(401, message="Authorization token is missing or is invalid")
            func(*args, **kwargs)
        return wrapper

    def UserAlreadyAuthenticated(user_id):
        for data in Session.active_sessions:
            if 'user_id' in data and data['user_id'] == user_id:
                return True
        return False

    def RegisterSession(session_data):
        Session.active_sessions.append(session_data)
        return True
    
    