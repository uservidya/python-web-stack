#!/usr/bin/env python
# -*- coding: utf-8

import os
import re
from ..utils import pip_install, run
from . import Formula


class Django(Formula):
    """Django formula"""

    def get_wsgi_env(self):
        return (
            self.project_root,
            '{name}.wsgi:application'.format(name=self.project_name)
        )

    def get_nginx_conf(self, cl_args):
        serve_dir = os.path.abspath(os.path.join(self.containing_dir, 'serve'))
        return self.get_template('nginx.conf') % {
            'static_root': os.path.join(serve_dir, 'static'),
            'media_root': os.path.join(serve_dir, 'media'),
            'bind_to': cl_args.bind_to,
            'server_root': cl_args.server_root
        }

    def install(self, cl_args):
        pip_install('django')

    def create_project(self, cl_args):
        admin_script = os.path.join(
            self.env.virtualenv_root, self.project_name,
            'bin', 'django-admin.py'
        )
        cmd = '{admin_script} startproject {name}'.format(
            admin_script=admin_script, name=self.project_name
        )
        run(cmd)

    def configure(self, cl_args):
        """Patch settings.py for nginx"""
        settings = os.path.join(
            self.project_root, self.project_name, 'settings.py'
        )
        serve_dir = os.path.abspath(os.path.join(self.containing_dir, 'serve'))
        os.mkdir(serve_dir)
        with open(settings, 'r') as f:
            s = f.read()
            s = re.sub(
                r'STATIC_ROOT.+?\n',
                "STATIC_ROOT = '{p}'\n".format(
                    p=os.path.join(serve_dir, 'static')
                ),
                s
            )
            s = re.sub(
                r'MEDIA_ROOT.+?\n',
                "MEDIA_ROOT = '{p}'\n".format(
                    p=os.path.join(serve_dir, 'media')
                ),
                s
            )
        with open(settings, 'w') as f:
            f.write(s)
