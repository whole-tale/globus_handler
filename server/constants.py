#!/usr/bin/env python
# -*- coding: utf-8 -*-


class PluginSettings:
    GLOBUS_ROOT_PATH = 'dm.globus_root_path'
    GLOBUS_CONNECT_DIR = 'dm.globus_gc_dir'
    # These are internal settings. Should not be set by the admin
    GLOBUS_ENDPOINT_ID = 'dm.globus_endpoint_id'
    GLOBUS_ENDPOINT_NAME = 'dm.globus_endpoint_name'


class GlobusEnvironmentVariables:
    GLOBUS_CLIENT_ID = 'GLOBUS_CLIENT_ID'
    GLOBUS_CLIENT_SECRET = 'GLOBUS_CLIENT_SECRET'
    GLOBUS_CONNECT_DIR = 'GLOBUS_CONNECT_DIR'
    ALL = [GLOBUS_CLIENT_ID, GLOBUS_CLIENT_SECRET, GLOBUS_CONNECT_DIR]
