from __future__ import absolute_import, unicode_literals
from celery import task
from celery.signals import celeryd_init,celeryd_after_setup

# @celeryd_init.connect
# def task_number_one(sender=None, conf=None, **kwargs):
# 	print("TASK DONEEEEEEEE")
# 	for i in range(0,1000):
# 		print(i)

# @celeryd_after_setup.connect
# def task_number_one(sender=None, conf=None, **kwargs):
# 	print("TASK DONEEEEEEEE")
# 	for i in range(0,1000):
# 		print(i)