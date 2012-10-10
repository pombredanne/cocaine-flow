# -*- coding: utf-8 -*-
from time import time, sleep
from flask import request, current_app, flash, redirect, session, url_for
import zmq


def token_required(admin=False):
    def wrapper(func):
        def _wrapper(*args, **kwargs):
            token = request.values.get('token')
            if not token:
                return 'Token is required', 403

            user = current_app.mongo.db.users.find_one({'token': token})
            if user is None:
                return 'Valid token is required', 403

            if isinstance(admin, bool)  and admin and not user.get('admin', False):
                return 'Admin token is required for this operation', 403

            return func(*args, user=user, **kwargs)

        return _wrapper

    if callable(admin):
        return wrapper(admin)
    else:
        return wrapper


def uniform(func):
    def wrapper(*args, **kwargs):
        rv = func(*args, **kwargs)
        if isinstance(rv, basestring):
            code = 200
        else:
            rv, code = rv

        if request.referrer:
            if 200 <= code < 300:
                flash(rv, 'alert-success')
            elif 400 <= code < 600:
                flash(rv, 'alert-error')
            return redirect(request.referrer)

        return rv, code

    return wrapper


def logged_in(func):
    def wrapper(*args, **kwargs):
        username = session.get('logged_in')
        if not username:
            return redirect(url_for('login'))

        user = current_app.mongo.db.users.find_one({'_id': session['logged_in']})
        if user is None:
            session.pop('logged_in', None)
            return redirect(url_for('login'))

        return func(user, *args, **kwargs)

    return wrapper


def send_json_rpc(data, hosts, timeout=0.5):
    rv = {}
    context = zmq.Context()

    if isinstance(hosts, basestring):
        hosts = [hosts]

    for host in hosts:
        rv[host] = None
        request = context.socket(zmq.REQ)
        request.connect('tcp://%s:5000' % host)
        request.setsockopt(zmq.LINGER, 0)

        # Statistics
        request.send_json(data)

        poller = zmq.Poller()
        poller.register(request, zmq.POLLIN)
        start = time()
        while True:
            socks = dict(poller.poll(timeout=timeout / 10.))
            if request in socks and socks[request] == zmq.POLLIN:
                rv[host] = request.recv_json(zmq.POLLERR)
                break

            if (time() - start) > timeout:
                break
            sleep(timeout / 10.)

    return rv
