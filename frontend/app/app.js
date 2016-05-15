'use strict';

// Declare app level module which depends on views, and components
var unitaste = angular.module('unitaste', [
  'ngRoute',
  'unitaste.view1',
  'unitaste.view2',
  'unitaste.login',
  'unitaste.register',
  'unitaste.profile',
  'unitaste.lounge',
  'unitaste.addEvent',
  'unitaste.version'
]).
config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
  $routeProvider.otherwise({redirectTo: '/view1'});
  $httpProvider.defaults.withCredentials = true;
}]);

