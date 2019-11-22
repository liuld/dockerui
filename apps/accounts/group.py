#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint, request, redirect, url_for, jsonify
from flask import render_template
from apps.accounts.models import Group, db, GroupSchema, User, Role, Permission, UserSchema, PermissionSchema, RoleSchema
from apps.accounts.forms import AddGroupForm
import json


blueprint = Blueprint('groups_blueprint', __name__)


@blueprint.route('/list/', methods=['get'])
def group_list():
    gid = request.args.get('id')
    is_modify = request.args.get('is_modify')
    try:
        if gid and isinstance(int(gid), int):
            group_obj = Group.query.get(int(gid))
            if group_obj:
                group_json = GroupSchema().dump(group_obj)

                if is_modify == 'true':
                    group_json['all_users'] = UserSchema(only=('id', 'name'), many=True).dump(User.query.all())
                    group_json['all_roles'] = RoleSchema(only=('id', 'name'), many=True).dump(Role.query.all())
                    group_json['all_permissions'] = PermissionSchema(only=('id', 'dis_name'), many=True).dump(Permission.query.all())
                return jsonify(group_json)
    except Exception as E:
        return jsonify({"result": False, "errors": "发生未知错误,请联系管理员!"})
    groups = Group.query.all()
    if request.args.get('json'):
        return jsonify(GroupSchema(many=True, only=('id', 'name')).dump(groups))
    return render_template('accounts/group.html', groups=groups)


@blueprint.route('/add/', methods=['get', 'post'])
def group_add():
    form = AddGroupForm()
    if request.method == "POST" and form.validate_on_submit():
        try:
            form.name = form.verify_name(form.name)
            if form.name.errors:
                return render_template('accounts/group_add.html', form=form)
            name = form.name.data
            desc = form.desc.data
            new_group = Group(name=name, desc=desc)
            db.session.add(new_group)
            db.session.commit()
            return redirect(url_for("groups_blueprint.group_list"))
        except Exception as e:
            return {"message": "内部错误，请联系管理员!"}
    return render_template('accounts/group_add.html', form=form)


@blueprint.route('/modify/', methods=['post', 'delete', 'patch', 'put'])
def group_modify():
    data = request.form.copy().to_dict()
    if request.method == 'POST':
        try:
            group_obj = Group.query.get(int(data.get('id')))
            if group_obj:
                validate = GroupSchema(only=('name', 'desc')).validate(data)
                print(data)
                return jsonify({"result": True})
        except Exception as E:
            db.session.rollback()
            return jsonify({"result": False, "errors": "发生未知错误,请联系管理员!"})
        return jsonify({"result": False, "errors": "参数错误,请确认传参是否正确!"})
    if request.method == "PUT":
        if data.get('option') and data['option'] == 'group_add_users':
            try:
                u_list = json.loads(data.get('users', '[]'))
                g_list = json.loads(data.get('groups', '[]'))
                if u_list and isinstance(u_list, list) and g_list and isinstance(g_list, list):
                    u_objs = User.query.filter(User.id.in_(u_list)).all()
                    g_objs = Group.query.filter(Group.id.in_(g_list)).all()
                    if u_objs and g_objs:
                        for g in g_objs:
                            for u in u_objs:
                                if not u in g.users:
                                    g.users.append(u)
                        db.session.commit()
                        return jsonify({"result": True})
            except Exception as E:
                db.session.rollback()
                return jsonify({"result": False, "errors": "发生未知错误,请联系管理员!"})
        if data.get('option') and data['option'] == 'group_add_roles':
            try:
                g_list = json.loads(data.get('groups', '[]'))
                r_list = json.loads(data.get('roles', '[]'))
                if g_list and isinstance(g_list, list) and r_list and isinstance(r_list, list):
                    g_objs = Group.query.filter(Group.id.in_(g_list)).all()
                    r_objs = Role.query.filter(Role.id.in_(r_list)).all()
                    if g_objs and r_objs:
                        for g_obj in g_objs:
                            for r_obj in r_objs:
                                if not r_obj in g_obj.roles:
                                    g_obj.roles.append(r_obj)
                        db.session.commit()
                        return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
                return jsonify({"result": False, "errors": "发生未知错误,请联系管理员!"})
        if data.get('option') and data['option'] == 'group_add_permissions':
            try:
                g_list = json.loads(data.get('groups', '[]'))
                p_list = json.loads(data.get('permissions', '[]'))
                if g_list and isinstance(g_list, list) and p_list and isinstance(p_list, list):
                    g_objs = Group.query.filter(Group.id.in_(g_list)).all()
                    p_objs = Permission.query.filter(Permission.id.in_(p_list)).all()
                    if g_objs and p_objs:
                        for g_obj in g_objs:
                            for p_obj in p_objs:
                                if not p_obj in g_obj.permissions:
                                    g_obj.permissions.append(p_obj)
                        db.session.commit()
                        return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
                return jsonify({"result": False, "errors": "发生未知错误,请联系管理员!"})
        return jsonify({"result": False, "errors": "参数错误,请确认传参是否正确!"})
    if request.method == "DELETE":
        try:
            groups = Group.query.filter(Group.id.in_(json.loads(data.get('g_list', '[]')))).all()
            if groups:
                for g in groups:
                    db.session.delete(g)
                db.session.commit()
                return jsonify({"result": True})
        except Exception as E:
            db.session.rollback()
            return jsonify({"result": False, "errors": "发生未知错误,请联系管理员!"})
        return jsonify({"result": False, "errors": "参数错误,请确认传参是否正确!"})
