#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from flask_wtf import FlaskForm
from apps.accounts.models import User, Group, Role, Permission
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email


class AddUserForm(FlaskForm):
    name = StringField('用户名', validators=[DataRequired(), Length(1, 16), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'username must have only letters, numbers dots or underscores')],render_kw={"placeholder": "请输入用户名"})
    cname = StringField('别名', validators=[DataRequired(), Length(1, 16)], render_kw={"placeholder": "请输入别名"})
    password = PasswordField('密码', validators=[DataRequired()], render_kw={"placeholder": "请输入密码"})
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password', message='密码不一致')], render_kw={"placeholder": "请再次输入密码"})
    phone_number = StringField('手机号码', validators=[DataRequired(), Length(11, 11, message='手机号码必须为11位数字'), Regexp('^[0-9]*$', 0, message="手机号码必须为11位数字")], render_kw={"placeholder": "请输入手机号码"})
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 32), Email(message='邮箱格式错误')], render_kw={"placeholder": "请输入邮箱"})

    def verify_field(self, form, field_name):
        if field_name == 'name':
            user = User.query.filter_by(name=form.name.data).all()
            if user:
                form.name.errors = ("用户名已存在",)
            return form
        if field_name == 'cname':
            user = User.query.filter_by(cname=form.cname.data).all()
            if user:
                form.cname.errors = ("别名已存在",)
            return form
        if field_name == 'phone_number':
            user = User.query.filter_by(phone_number=form.phone_number.data).all()
            if user:
                form.phone_number.errors = ("手机号码已注册",)
            return form
        if field_name == 'email':
            user = User.query.filter_by(email=form.email.data).all()
            if user:
                form.email.errors = ("邮箱已注册",)
            return form


class AddGroupForm(FlaskForm):
    name = StringField('组名称', validators=[DataRequired(), Length(1, 16)],render_kw={"placeholder": "请输入用户组名称"})
    desc = StringField('描述', validators=[DataRequired(),Length(1, 255)], render_kw={"placeholder": "请输入组描述"})

    def verify_name(self, field):
        group = Group.query.filter_by(name=field.data).all()
        if group:
            field.errors = ("用户组名称已存在", )
        return field


class AddRoleForm(FlaskForm):
    name = StringField('角色名称', validators=[DataRequired(), Length(1, 32)], render_kw={"placeholder": "请输入角色名称"})
    desc = StringField('角色描述', validators=[DataRequired(), Length(1, 255)], render_kw={"placeholder": "请输入角色描述"})

    def verify_name(self, field):
        role = Role.query.filter_by(name=field.data).all()
        if role:
            field.errors = ("角色名称已存在",)
        return field


class AddPermissionForm(FlaskForm):
    name = StringField('权限名称', validators=[DataRequired(), Length(1, 64)], render_kw={"placeholder": "请输入权限名称"})
    dis_name = StringField('权限别名', validators=[DataRequired(), Length(1, 32)], render_kw={"placeholder": "请输入权限别名"})
    desc = StringField('权限描述', validators=[DataRequired(), Length(1, 255)], render_kw={"placeholder": "请输入权限描述"})

    def verify_field(self, form, field_name):
        if field_name == 'name':
            permission = Permission.query.filter_by(name=form.name.data).all()
            if permission:
                form.name.errors = ("权限名称已存在",)
            return form
        if field_name == 'dis_name':
            permission = Permission.query.filter_by(dis_name=form.dis_name.data).all()
            if permission:
                form.dis_name.errors = ("权限别名",)
            return form
