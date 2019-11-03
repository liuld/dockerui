#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from app import app
from config import HOST, DEBUG, PORT
from flask import render_template
from apps import accounts
from apps.accounts.models import db


accounts.register_blueprint(app)


@app.route('/', methods=['get'])
def index():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
