#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


import pymysql


HOST = '0.0.0.0'
PORT = 8000
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@192.168.10.20/dockerui'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'test'
JSON_AS_ASCII = False

