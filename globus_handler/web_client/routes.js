/* eslint-disable import/first */

import router from '@girder/core/router';
import events from '@girder/core/events';
import { exposePluginConfig } from '@girder/core/utilities/PluginUtils';

exposePluginConfig('globus_handler', 'plugins/globus_handler/config');

import ConfigView from './views/ConfigView';
router.route('plugins/globus_handler/config', 'GlobusHandlerConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});
