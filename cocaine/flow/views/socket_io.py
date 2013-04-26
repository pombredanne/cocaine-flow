from flask import json
from flask import jsonify
from flask import request
from flask import redirect
from flask import stream_with_context
from flask import session
from flask import Response
from flask import render_template
from flask import current_app

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin

from common import token_required_json
from common import logged_in
from common import logged_in_json
from .storages import ST

from pprint import pprint

from .jsonapi import *

class PingPong(BaseNamespace):
    def on_ping(self,attack):
        if attack['type'] == 'fireball':
            for i in range(10):
                self.emit('pong',{'sound':'bang!'})
        else:
            self.emit('pong',{'sound':'pong'})

class ApiSocket(BaseNamespace):

    def on_userinfo(self, *query):
        #user = query.get("username")
        #print "userinfo", user
        login = ST.instance().find_user_by_username(user)
        self.emit('userinfo', json.dumps({"result" : "ok", "ACL" : {}, "login" : "blabla"}))

    def on_summary(self, query):
        print "Summary"
        apps = ST.instance().read_manifests()
        res = []
        for app in apps.itervalues():
            tmp = dict()
            tmp['repository'] = app.get('url', '')
            tmp['dependencies'] = app.get('depends','')
            tmp["tracker"] = "Optional"
            tmp["developers"] = [ST.instance().get_username_by_token(app['developer'])]
            tmp['commits'] = list()
            for commit in app.get('changelog',[]):
                hash, date, other = commit.split(' ', 2)
                msg, author = other.rsplit('[', 1)
                tmp['commits'].append({
                    "hash" : hash,
                    "date" : date,
                    "commiter" : author.rstrip(']'),
                    "description" : msg.strip(),
                })
            res.append(tmp)
        self.emit('summary', json.dumps(res))



def main_page():
    return render_template('main_page.html')

def test(remaining):
    real_request = request._get_current_object()
    socketio_manage(request.environ, {'': ApiSocket}, request=real_request)
    return Response()
