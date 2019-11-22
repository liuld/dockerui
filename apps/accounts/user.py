#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask import Blueprint, request, redirect, url_for, jsonify
from flask import render_template
from apps.accounts.models import User, db, Group, Role, Permission, UserSchema, GroupSchema, RoleSchema, PermissionSchema, validate_unique
from apps.accounts.forms import AddUserForm
import json


blueprint = Blueprint('users_blueprint', __name__)


@blueprint.route('/list/', methods=['get'])
def user_list():
    users = User.query.all()
    if request.args.get('json'):
        return jsonify(UserSchema(many=True, only=('id', 'name')).dump(users))
    return render_template('accounts/user.html', users=users)


@blueprint.route('/list/<int:id>', methods=['get'])
def get_user(id):
    user = User.query.get(id)
    if user:
        userschema = UserSchema(exclude=('pwd_hash',))
        user_info = userschema.dump(user)
        if request.args.get('modify'):
            all_groups = GroupSchema(only=('id', 'name'), many=True).dump(Group.query.all())
            all_roles = RoleSchema(only=('id', 'name'), many=True).dump(Role.query.all())
            all_permissions = PermissionSchema(only=('id', 'dis_name'), many=True).dump(Permission.query.all())
            user_info['all_roles'] = all_roles
            user_info['all_groups'] = all_groups
            user_info['all_permissions'] = all_permissions
        return jsonify(user_info)
    else:
        return jsonify({})


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


@blueprint.route('/modify/', methods=['post', 'delete', 'patch', 'put'])
def user_modify():
    if request.method == "POST":
        data = request.form.copy().to_dict()
        user = User.query.filter_by(id=data['id']).first()
        result = []
        if user:
            userschema = UserSchema(only=('name', 'cname', 'email', 'phone_number'))
            res = userschema.validate(data)
            if not res:
                if validate_unique(user, User, {'name': data['name']}):
                    user.name = data['name']
                else:
                    result.append('用户名已存在')
                if validate_unique(user, User, {'cname': data['cname']}):
                    user.cname = data['cname']
                else:
                    result.append('用户别名已存在')
                if validate_unique(user, User, {'email': data['email']}):
                    user.email = data['email']
                else:
                    result.append('邮箱已被注册')
                if validate_unique(user, User, {'phone_number': data['phone_number']}):
                    user.phone_number = data['phone_number']
                else:
                    result.append('手机号码已注册')
                if result:
                    return jsonify({"errors": result, "result": False})
                if data.get('groups', 'no') != 'no':
                    user.groups = Group.query.filter(Group.id.in_(json.loads(data['groups']))).all()
                if data.get('roles', 'no') != 'no':
                    user.roles = Role.query.filter(Role.id.in_(json.loads(data['roles']))).all()
                if data.get('permissions', 'no') != 'no':
                    user.permissions = Permission.query.filter(Permission.id.in_(json.loads(data['permissions']))).all()
                try:
                    db.session.commit()
                    return jsonify({"result": True})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({"errors": e.args, "result": False})
            else:
                return jsonify({"errors": res, "result": False})
        else:
            return jsonify({"errors": "用户不存在", "result": False})
    if request.method == "DELETE":
        user_list = request.form.copy().to_dict()
        users = User.query.filter(User.id.in_(json.loads(user_list.get('user_list', '[]')))).all()
        if users:
            try:
                for user in users:
                    db.session.delete(user)
                db.session.commit()
                return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
                print(e.args)
                return jsonify({"result": False, "errors": e.args})
        return jsonify({"result": False, "errors": "用户为空，请提交要删除的用户!"})
    if request.method == 'PATCH':
        patch_data = request.form.copy().to_dict()
        # 启用/禁用用户
        if patch_data.get('option', None) and patch_data['option'] == 'dis_or_enable':
            try:
                enable_user_list = json.loads(patch_data.get('user_list', '[]'))
                if isinstance(enable_user_list, list):
                    enable_users = User.query.filter(User.id.in_(enable_user_list)).all()
                    for user in enable_users:
                        if user.status:
                            user.status = False
                        else:
                            user.status = True
                    db.session.commit()
                    return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
            return jsonify({"result": False, 'errors': '操作失败，请联系管理员!'})
        # 设置/移除用户超级管理员
        if patch_data.get('option', None) and patch_data['option'] == 'set_super':
            try:
                user = int(patch_data.get('user', 'empty'))
                user_obj = User.query.get(user)
                if user_obj:
                    if user_obj.is_super:
                        user_obj.is_super = False
                    else:
                        user_obj.is_super = True
                    db.session.commit()
                    return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
            return jsonify({"result": False, 'errors': '操作失败，请联系管理员!'})
        # 重置用户密码
        if patch_data.get('option', None) and patch_data['option'] == 'reset_pwd':
            try:
                user = int(patch_data.get('user', 'empty'))
                user_obj = User.query.get(user)
                if user_obj:
                    if isinstance(patch_data.get('password', None), str) and isinstance(patch_data.get('password2', None), str) and patch_data['password'] == patch_data['password2']:
                        user_obj.password = patch_data['password']
                        db.session.commit()
                        return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
            return jsonify({"result": False, 'errors': '操作失败，请联系管理员!'})
        return jsonify({"result": False, 'errors': '参数错误'})
    if request.method == 'PUT':
        patch_data = request.form.copy().to_dict()
        # 批量添加用户组
        if patch_data.get('option') and patch_data['option'] == 'add_users_to_groups':
            try:
                u_list = json.loads(patch_data.get('users', '[]'))
                g_list = json.loads(patch_data.get('groups', '[]'))
                if u_list and isinstance(u_list, list) and g_list and isinstance(g_list, list):
                    u_objs = User.query.filter(User.id.in_(u_list)).all()
                    g_objs = Group.query.filter(Group.id.in_(g_list)).all()
                    if u_objs and g_objs:
                        for u_obj in u_objs:
                            for g_obj in g_objs:
                                if not g_obj in u_obj.groups:
                                    u_obj.groups.append(g_obj)
                        db.session.commit()
                        return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
                return jsonify({"result": False, 'errors': '未知错误'})
        # 批量添加角色
        if patch_data.get('option') and patch_data['option'] == 'user_add_roles':
            try:
                u_list = json.loads(patch_data.get('users', '[]'))
                r_list = json.loads(patch_data.get('roles', '[]'))
                if u_list and isinstance(u_list, list) and r_list and isinstance(r_list, list):
                    u_objs = User.query.filter(User.id.in_(u_list)).all()
                    r_objs = Role.query.filter(Role.id.in_(r_list)).all()
                    if u_objs and r_objs:
                        for u_obj in u_objs:
                            for r_obj in r_objs:
                                if not r_obj in u_obj.roles:
                                    u_obj.roles.append(r_obj)
                        db.session.commit()
                        return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
                return jsonify({"result": False, 'errors': '未知错误'})
        # 批量添加权限
        if patch_data.get('option') and patch_data['option'] == 'user_add_permissions':
            try:
                u_list = json.loads(patch_data.get('users', '[]'))
                p_list = json.loads(patch_data.get('permissions', '[]'))
                if u_list and isinstance(u_list, list) and p_list and isinstance(p_list, list):
                    u_objs = User.query.filter(User.id.in_(u_list)).all()
                    p_objs = Permission.query.filter(Permission.id.in_(p_list)).all()
                    if u_objs and p_objs:
                        print(patch_data)
                        for u_obj in u_objs:
                            for p_obj in p_objs:
                                if not p_obj in u_obj.permissions:
                                    u_obj.permissions.append(p_obj)
                        db.session.commit()
                        return jsonify({"result": True})
            except Exception as e:
                db.session.rollback()
                return jsonify({"result": False, 'errors': '未知错误'})
        return jsonify({"result": False, 'errors': '参数错误'})
