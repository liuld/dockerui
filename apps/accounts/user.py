#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint, request, redirect, url_for, flash
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
            name = form.verify_field(form, 'name').name.data
            cname = form.verify_field(form, 'cname').cname.data
            phone_number = form.verify_field(form, 'phone_number').phone_number.data
            email = form.verify_field(form, 'email').email.data
            password = form.password.data
            if form.name.errors or form.cname.errors or form.phone_number.errors or form.email.errors:
                return render_template('accounts/user_add.html', form=form)
            new_user = User(name=name, cname=cname, password=password, phone_number=phone_number, email=email)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("users_blueprint.user_list"))
        except Exception as E:
            db.session.rollback()
            return flash(message="内部错误，请联系管理员!")
    return render_template('accounts/user_add.html', form=form)
