#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint, request, redirect, url_for, jsonify
from flask import render_template
from apps.accounts.models import db, Permission, PermissionSchema
from apps.accounts.forms import AddPermissionForm


blueprint = Blueprint('permissions_blueprint', __name__)


@blueprint.route('/list/', methods=['get'])
def permission_list():
    permissions = Permission.query.all()
    if request.args.get('json'):
        return jsonify(PermissionSchema(many=True, only=('id', 'dis_name')).dump(permissions))
    return render_template('accounts/permission.html', permissions=permissions)


@blueprint.route('/add/', methods=['get', 'post'])
def permission_add():
    form = AddPermissionForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            for field in ['name', 'dis_name']:
                form = form.verify_field(form, field)
            if form.errors:
                return render_template('accounts/permission_add.html', form=form)
            name = form.name.data
            dis_name = form.dis_name.data
            desc = form.desc.data
            new_permission = Permission(name=name, dis_name=dis_name, desc=desc)
            db.session.add(new_permission)
            db.session.commit()
            return redirect(url_for("permissions_blueprint.permission_list"))
        except Exception as e:
            return {"message": "内部错误，请联系管理员!"}
    return render_template('accounts/permission_add.html', form=form)
