#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint, request, redirect, url_for, flash
from wtforms.validators import ValidationError
from flask import render_template
from apps.accounts.models import Group, db
from apps.accounts.forms import AddGroupForm


blueprint = Blueprint('groups_blueprint', __name__)


@blueprint.route('/list/', methods=['get'])
def group_list():
    groups = Group.query.all()
    return render_template('accounts/group.html', groups=groups)


@blueprint.route('/add/', methods=['get', 'post'])
def group_add():
    form = AddGroupForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            name = form.verify_name(form.name).data
            desc = form.desc.data
            new_group = Group(name=name, desc=desc)
            db.session.add(new_group)
            db.session.commit()
            return redirect(url_for("groups_blueprint.group_list"))
        except ValidationError as e:
            form.name.errors = e.args
            return render_template('accounts/group_add.html', form=form)
        except Exception as e:
            return flash(message="内部错误，请联系管理员!")
    return render_template('accounts/group_add.html', form=form)