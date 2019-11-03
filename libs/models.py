#!/usr/local/bin/python3
# _*_ coding: utf-8 _*_


from app import db


class DbModels(object):

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self