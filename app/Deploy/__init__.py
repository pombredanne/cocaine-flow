#!/usr/bin/env python

from cocaine.worker import Worker
from deploy import get

W = Worker()

W.run({"get": get})