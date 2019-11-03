#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint
from flask import render_template


blueprint = Blueprint('roles', __name__)


@blueprint.route('/list/', methods=['get'])
def role_list():
    return render_template('accounts/role.html')