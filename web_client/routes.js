import router from 'girder/router';
import events from 'girder/events';
import { exposePluginConfig } from 'girder/utilities/PluginUtils';

import ConfigView from './views/ConfigView';

exposePluginConfig('globus_handler', 'plugins/globus_handler/config');

router.route('plugins/globus_handler/config', 'GlobusHandlerConfig', function () {
    events.trigger('g:navigateTo', ConfigView);
});
