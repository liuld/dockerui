#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import fields, ValidationError, EXCLUDE
from app import db, ma


def validate_unique(user_obj, obj, field):
    res = obj.query.filter_by(**field).first()
    if not res or res.id == user_obj.id:
        return True
    return False


class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False, unique=True)
    dis_name = db.Column(db.String(32), nullable=False, unique=True)
    desc = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<Permission {}: {}({})>'.format(self.id, self.dis_name, self.name)

    class Meta:
        ordering = ('-id',)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(32), unique=True, nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    ctime = db.Column(db.DateTime, default=datetime.now)
    permissions = db.relationship('Permission', secondary='role_permission', backref=db.backref('roles', lazy='dynamic'))

    def __repr__(self):
        return '<Role {}: {}'.format(self.id, self.name)

    class Meta:
        ordering = ('-id',)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(16), unique=True, nullable=False)
    cname = db.Column(db.String(16), unique=True, nullable=False)
    pwd_hash = db.Column(db.String(100), nullable=False)
    is_super = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True)
    phone_number = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(32), unique=True, nullable=False)
    ctime = db.Column(db.DateTime, default=datetime.now)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    last_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    groups = db.relationship('Group', secondary='user_group', backref=db.backref('users', lazy='dynamic'))
    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy='dynamic'))
    permissions = db.relationship('Permission', secondary='user_permission', backref=db.backref('users', lazy='dynamic'))

    @property
    def password(self):
        raise AttributeError('密码为私有属性，不允许访问')

    @password.setter
    def password(self, pwd):
        self.pwd_hash = generate_password_hash(pwd)

    def verify_password(self, pwd):
        return check_password_hash(self.pwd_hash, pwd)

    def __repr__(self):
        return '<User {}: {}>'.format(self.id, self.name)

    class Meta:
        ordering = ('-id',)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(16), unique=True, nullable=False)
    desc = db.Column(db.String(255), nullable=False)
    ctime = db.Column(db.DateTime, default=datetime.now)
    roles = db.relationship('Role', secondary='group_role', backref=db.backref('groups', lazy='dynamic'))
    permissions = db.relationship('Permission', secondary='group_permission', backref=db.backref('groups', lazy='dynamic'))

    def __repr__(self):
        return '<Group {}: {}>'.format(self.id, self.name)

    class Meta:
        ordering = ('-id',)


# 权限与角色关联表
role_permission = db.Table('role_permission', db.Column('role_id', db.Integer, db.ForeignKey('roles.id')), db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id')))

# 用户与用户组关联表
user_group = db.Table('user_group', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('group_id', db.Integer, db.ForeignKey('groups.id')))

# 用户与角色关联表
user_role = db.Table('user_role', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))

# 用户与权限关联表
user_permission = db.Table('user_permission', db.Column('user_id', db.Integer, db.ForeignKey('users.id')), db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id')))

# 用户组与角色关联表
group_role = db.Table('group_role', db.Column('group_id', db.Integer, db.ForeignKey('groups.id')), db.Column('role_id', db.Integer, db.ForeignKey('roles.id')))

# 用户组与权限关联表
group_permission = db.Table('group_permission', db.Column('group_id', db.Integer, db.ForeignKey('groups.id')), db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id')))


class PermissionSchema(ma.ModelSchema):

    class Meta:
        model = Permission
        unknown = EXCLUDE


class RoleSchema(ma.ModelSchema):
    permissions = fields.Nested(PermissionSchema, many=True, only=('id', 'dis_name'))

    class Meta:
        model = Role
        unknown = EXCLUDE


class GroupSchema(ma.ModelSchema):
    roles = fields.Nested(RoleSchema, many=True, only=('id', 'name', 'permissions'))
    permissions = fields.Nested(PermissionSchema, many=True, only=('id', 'dis_name'))

    class Meta:
        model = Group
        unknown = EXCLUDE


class UserSchema(ma.ModelSchema):
    email = fields.Email(required=True, validate=[lambda n: len(n) <= 32])
    groups = fields.Nested(GroupSchema, many=True, only=('id', 'name', 'roles', 'permissions'))
    roles = fields.Nested(RoleSchema, many=True, only=('id', 'name', 'permissions'))
    permissions = fields.Nested(PermissionSchema, many=True, only=('id', 'dis_name'))

    class Meta:
        model = User
        unknown = EXCLUDE


