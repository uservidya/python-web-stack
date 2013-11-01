#!/usr/bin/env python
# -*- coding: utf-8

import os
import re
from ..utils import chdir, pip_install, env
from . import Formula


class Django(Formula):
    """Django formula"""

    nginx_conf = """
server {
    listen localhost;

    location / {
        proxy_pass http://%(bind_to)s;
    }

    location /static/ {
        autoindex on;
        alias %(static_root)s;
    }

    location /media/ {
        autoindex on;
        alias %(media_root)s;
    }
}
    """

    def get_wsgi_env(self):
        return (
            self.project_root,
            '{name}.wsgi:application'.format(name=self.project_name)
        )

    def get_nginx_conf(self, bind_to):
        serve_dir = os.path.abspath(os.path.join(self.containing_dir, 'serve'))
        conf = self.nginx_conf % {
            'static_root': os.path.join(serve_dir, 'static'),
            'media_root': os.path.join(serve_dir, 'media'),
            'bind_to': bind_to
        }
        return conf

    def install(self):
        pip_install('django')

    def create_project(self):
        with chdir(self.containing_dir):
            admin_script = os.path.join(
                env.virtualenv_root, self.project_name,
                'bin', 'django-admin.py'
            )
            os.system('{admin_script} startproject {name}'.format(
                admin_script=admin_script, name=self.project_name
            ))

    def configure(self):
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