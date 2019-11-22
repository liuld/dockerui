#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint, request, redirect, url_for, jsonify
from flask import render_template
from apps.accounts.models import db, Role, RoleSchema
from apps.accounts.forms import AddRoleForm


blueprint = Blueprint('roles_blueprint', __name__)


@blueprint.route('/list/', methods=['get'])
def role_list():
    roles = Role.query.all()
    if request.args.get('json'):
        return jsonify(RoleSchema(many=True, only=('id', 'name')).dump(roles))
    return render_template('app-accounts/role-list.html', roles=roles)


@blueprint.route('/add/', methods=['get', 'post'])
def role_add():
    form = AddRoleForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            form.name = form.verify_name(form.name)
            if form.name.errors:
                return render_template('accounts/role_add.html', form=form)
            name = form.name.data
            desc = form.desc.data
            new_role = Role(name=name, desc=desc)
            db.session.add(new_role)
            db.session.commit()
            return redirect(url_for("roles_blueprint.role_list"))
        except Exception as e:
            return {"message": "内部错误，请联系管理员!"}
    return render_template('accounts/role_add.html', form=form)
