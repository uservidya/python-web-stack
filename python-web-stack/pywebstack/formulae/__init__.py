#!/usr/bin/env python
# -*- coding: utf-8

import os
from ..utils import env


class Formula(object):
    """Abstract formula interface to be inherited by concrete formula classes
    """
    def __init__(self, project_name):
        self.project_name = project_name
        self.containing_dir = os.path.join(
            env.virtualenv_root, project_name, env.project_container_name
        )

    @property
    def project_root(self):
        return os.path.join(self.containing_dir, self.project_name)

    def pip(self, *cmd):
        os.system('pip ' + ' '.join(cmd))

    def setup(self):
        self.install()
        self.create_project()
        self.configure()

    def teardown(self):
        self.deconfigure()

    # The following methods MUST be implemented

    def get_wsgi_script(self):
        raise NotImplementedError()

    def install(self):
        raise NotImplementedError()

    def create_project(self):
        raise NotImplementedError()

    def configure(self):
        raise NotImplementedError()

    def deconfigure(self):
        raise NotImplementedError()

    # The following methods MAY be implemented as additional hooks

    def pre_setup(self):
        pass

    def post_setup(self):
        pass

    def pre_teardown(self):
        pass

    def post_teardown(self):
        pass
