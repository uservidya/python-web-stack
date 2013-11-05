#!/usr/bin/env python
# -*- coding: utf-8

import os
import collections
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

    def __init__(self, formula_name, env, project_name):
        self.env = env
        self.formula_name = formula_name
        self.template_dir = os.path.normpath(os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'templates',
            self.formula_name
        ))
        self.project_name = project_name
        self.containing_dir = os.path.join(
            env.virtualenv_root, project_name, env.project_container_name
        )

    @property
    def project_root(self):
        return os.path.join(self.containing_dir, self.project_name)

    def get_template(self, filename):
        with open(os.path.join(self.template_dir, filename), 'r') as f:
            content = f.read()
        return content

    def setup(self, cl_args):
        self.install(cl_args)
        with chdir(self.containing_dir):
            self.create_project(cl_args)
        self.configure(cl_args)

    def teardown(self, cl_args):
        self.deconfigure(cl_args)

    # The following methods MUST be implemented

    def get_wsgi_env(self):
        """Provide needed information about WSGI for the app server

        :returns: A 2-tuple. The first item indicates the directory to be when
            the server initiates the WSGI application. This is also where the
            PID file resides. The second item is the Python module path to the
            application instance.
        """
        raise NotImplementedError()

    def install(self, cl_args):
        raise NotImplementedError()

    def create_project(self, cl_args):
        raise NotImplementedError()

    # The following methods can be re-implemented for additional operations

    def configure(self, cl_args):
        pass

    def deconfigure(self, cl_args):
        pass

    def get_prompts(self):
        """Provide extra prompts for ``mksite``

        :returns: a ``dict``-like instance. Can be ``collections.OrderedDict``
            if you wish to force ordering or prompts. The values will be
            injected into ``cl_args`` with the key of each item. The value of
            each item should be a 2-tuple, specifying the text used when
            prompting, and a default value (or ``None`` if you don't want
            defaults). The second item can be a callable, in which case the
            default value will be the return value by calling it with
            ``cl_args`` as the only argument.
        """
        return collections.OrderedDict()

    def get_nginx_conf(self, cl_args):
        """Provide nginx configuration

        :param cl_args: arguments received from the setup command
        :rtype: str
        """
        return self.nginx_conf % {
            'bind_to': cl_args.bind_to, 'server_root': cl_args.server_root
        }
