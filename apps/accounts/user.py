#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint, request, redirect, url_for
from flask import render_template
from wtforms.validators import ValidationError
from apps.accounts.models import User, db
from apps.accounts.forms import AddUserForm


blueprint = Blueprint('users_blueprint', __name__)


@blueprint.route('/list/', methods=['get'])
def user_list():
    users = User.query.all()
    return render_template('accounts/user.html', users=users)


@blueprint.route('/add/', methods=['get', 'post'])
def user_add():
    form = AddUserForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            for field in ['name', 'cname', 'phone_number', 'email']:
                form = form.verify_field(form, field)
            if form.errors:
                return render_template('accounts/user_add.html', form=form)
            data = form.data
            data.pop('csrf_token')
            data.pop('password2')
            new_user = User(**data)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("users_blueprint.user_list"))
        except Exception as E:
            db.session.rollback()
            return {"messages": "内部错误，请联系管理员!"}
    return render_template('accounts/user_add.html', form=form)
