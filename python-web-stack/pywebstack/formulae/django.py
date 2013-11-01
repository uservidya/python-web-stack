#!/usr/bin/env python
# -*- coding: utf-8

import os
from ..utils import chdir
from . import Formula


class Django(Formula):
    """Django formula"""

    def get_wsgi_env(self):
        return (
            self.project_root,
            '{name}.wsgi:application'.format(name=self.project_name)
        )

    def install(self):
        self.pip_install('django')

    def create_project(self):
        with chdir(self.containing_dir):
            os.system('django-admin.py startproject {name}'.format(
                name=self.project_name
            ))
