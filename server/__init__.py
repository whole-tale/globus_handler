#!/usr/bin/env python
# -*- coding: utf-8 -*-

from girder.constants import SettingDefault
from girder.utility import setting_utilities
from .constants import PluginSettings


@setting_utilities.validator({
    PluginSettings.GLOBUS_ROOT_PATH,
    PluginSettings.GLOBUS_CONNECT_DIR,
    PluginSettings.GLOBUS_ENDPOINT_ID,
    PluginSettings.GLOBUS_ENDPOINT_NAME
})
def validateOtherSettings(event):
    pass


def load(info):
    # set the Globus drop directory to /tmp/wt-globus. In production, this should
    # be an isolated directory that is on the same filesystem as the storage path in
    # order to allow files to be moved to the DM cache without actually copying the bytes
    SettingDefault.defaults[PluginSettings.GLOBUS_ROOT_PATH] = '/tmp/wt-globus'
