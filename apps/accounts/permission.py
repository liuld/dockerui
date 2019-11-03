#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint
from flask import render_template


blueprint = Blueprint('permissions', __name__)


@blueprint.route('/list/', methods=['get'])
def permission_list():
    return render_template('accounts/permission.html')