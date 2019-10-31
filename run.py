#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from app import app
from config import HOST, DEBUG, PORT
from apps.accounts.models import db


if __name__ == '__main__':
    db.create_all()
    app.run(host=HOST, port=PORT, debug=DEBUG)
