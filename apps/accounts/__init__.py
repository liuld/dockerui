#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from apps.accounts import user, group, permission, role


def register_blueprint(app):
    app.register_blueprint(user.blueprint, url_prefix='/accounts/users/')
    app.register_blueprint(group.blueprint, url_prefix='/accounts/groups/')
    app.register_blueprint(role.blueprint, url_prefix='/accounts/roles/')
    app.register_blueprint(permission.blueprint, url_prefix='/accounts/permission/')
