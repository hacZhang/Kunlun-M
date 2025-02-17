#!/usr/bin/env python
# encoding: utf-8
'''
@author: LoRexxar
@contact: lorexxar@gmail.com
@file: middleware.py
@time: 2020/12/4 17:02
@desc:

'''


from web.index.models import ScanTask, ScanResultTask, Rules, Tampers, Project


class SDataMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            request.session["rules_count"] = Rules.objects.all().count()
            request.session["project_count"] = Rules.objects.all().count()
            request.session["tasks_count"] = ScanTask.objects.all().count()
            request.session["tasks_finished_count"] = ScanTask.objects.filter(is_finished=True).count()
            request.session["tampers_count"] = Tampers.objects.all().count()

            request.session["vul_count"] = ScanResultTask.objects.all().count()

        return response
