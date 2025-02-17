#!/usr/bin/env python
# encoding: utf-8
'''
@author: LoRexxar
@contact: lorexxar@gmail.com
@file: project.py
@time: 2021/7/20 15:50
@desc:

'''


import ast

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound
from django.views.generic import TemplateView
from django.views import View
from django.shortcuts import render, redirect

from Kunlun_M.settings import SUPER_ADMIN
from web.index.controller import login_or_token_required
from utils.utils import del_sensitive_for_config

from web.index.models import ScanTask, ScanResultTask, Rules, Tampers, NewEvilFunc, Project, ProjectVendors
from web.index.models import get_and_check_scanresult, get_and_check_evil_func


class ProjectListView(TemplateView):
    """展示当前用户的项目"""
    template_name = "dashboard/projects/projects_list.html"

    def get_context_data(self, **kwargs):
        context = super(ProjectListView, self).get_context_data(**kwargs)

        rows = Project.objects.all().order_by('-id')

        context['projects'] = rows

        for project in context['projects']:

            tasks = ScanTask.objects.filter(project_id=project.id).order_by('-id')
            tasks_count = len(tasks)

            vendors_count = ProjectVendors.objects.filter(project_id=project.id).count()

            results_count = ScanResultTask.objects.filter(scan_project_id=project.id, is_active=1).count()

            last_scan_time = 0
            if tasks:
                last_scan_time = tasks.first().last_scan_time

            project.tasks_count = tasks_count
            project.results_count = results_count
            project.last_scan_time = last_scan_time
            project.vendors_count = vendors_count

        context['projects'] = sorted(context['projects'], key=lambda x:x.last_scan_time)[::-1]

        return context


class ProjectDetailView(View):
    """展示当前项目细节"""

    @staticmethod
    @login_or_token_required
    def get(request, project_id):
        project = Project.objects.filter(id=project_id).first()

        tasks = ScanTask.objects.filter(project_id=project.id).order_by('-id')[:20]
        taskresults = ScanResultTask.objects.filter(scan_project_id=project.id, is_active=1).all()
        newevilfuncs = NewEvilFunc.objects.filter(project_id=project.id).all()
        pvs = ProjectVendors.objects.filter(project_id=project.id)

        for task in tasks:
            task.is_finished = int(task.is_finished)
            task.parameter_config = del_sensitive_for_config(task.parameter_config)

        for taskresult in taskresults:
            taskresult.is_unconfirm = int(taskresult.is_unconfirm)

        if not project:
            return HttpResponseNotFound('Project Not Found.')
        else:
            data = {
                'tasks': tasks,
                'taskresults': taskresults,
                'newevilfuncs': newevilfuncs,
                'project': project,
                'project_vendors': pvs,
            }
            return render(request, 'dashboard/projects/project_detail.html', data)
