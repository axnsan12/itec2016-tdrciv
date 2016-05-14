'use strict';

angular.module('unitaste.version', [
  'unitaste.version.interpolate-filter',
  'unitaste.version.version-directive'
])

.value('version', '0.1');
