#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config


app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)
