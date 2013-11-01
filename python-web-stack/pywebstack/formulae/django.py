#!/usr/bin/env python
# -*- coding: utf-8

import os
import re
from ..utils import chdir
from . import Formula


class Django(Formula):
    """Django formula"""

    nginx_conf = """
server {
    listen localhost:8000;

    location / {
        proxy_pass http://127.0.0.1:8001;
    }

    location /static/ {
        autoindex on;
        alias {static_root};
    }

    location /media/ {
        autoindex on;
        alias {media_root};
    }
}
    """

    def get_wsgi_env(self):
        return (
            self.project_root,
            '{name}.wsgi:application'.format(name=self.project_name)
        )

    def get_nginx_conf(self):
        serve_dir = os.path.abspath(os.path.join(self.containing_dir, 'serve'))
        conf = self.nginx_conf.format(
            static_root=os.path.join(serve_dir, 'static'),
            media_root=os.path.join(serve_dir, 'media')
        )
        return conf

    def install(self):
        self.pip_install('django')

    def create_project(self):
        with chdir(self.containing_dir):
            os.system('django-admin.py startproject {name}'.format(
                name=self.project_name
            ))

    def configure(self):
        """Patch settings.py for nginx"""
        settings = os.path.join(
            self.project_root, self.project_name, 'settings.py'
        )
        serve_dir = os.path.abspath(os.path.join(self.containing_dir, 'serve'))
        os.mkdir(serve_dir)
        with open(settings, 'rw') as f:
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
            f.write(s)
