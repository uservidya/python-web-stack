#!/usr/bin/env python
# -*- coding: utf-8

import os
from ..utils import chdir


class Formula(object):
    """Abstract formula interface to be inherited by concrete formula classes
    """

    nginx_conf = """
server {
    listen 80;

    location %(server_root)s {
        proxy_pass http://127.0.0.1:%(bind_to)s;
    }
}
    """

    def __init__(self, env, project_name):
        self.project_name = project_name
        self.containing_dir = os.path.join(
            env.virtualenv_root, project_name, env.project_container_name
        )

    @property
    def project_root(self):
        return os.path.join(self.containing_dir, self.project_name)

    def setup(self):
        self.install()
        with chdir(self.containing_dir):
            self.create_project()
        self.configure()

    def teardown(self):
        self.deconfigure()

    # The following methods MUST be implemented

    def get_wsgi_env(self):
        """Provide needed information about WSGI for Gunicorn

        :returns: A 2-tuple. The first item indicates the directory to be when
            Gunicorn initiates the WSGI application. This is also where the
            Gunicorn PID file resides. The second item is the module path to
            the application.
        """
        raise NotImplementedError()

    def install(self):
        raise NotImplementedError()

    def create_project(self):
        raise NotImplementedError()

    # The following methods can be re-implemented for additional operations

    def configure(self):
        pass

    def deconfigure(self):
        pass

    def get_nginx_conf(self, args):
        """Provide nginx configuration

        :param args: arguments received from the setup command
        :rtype: str
        """
        return self.nginx_conf % {
            'bind_to': args.bind_to, 'server_root': args.server_root
        }
