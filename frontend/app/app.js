'use strict';

// Declare app level module which depends on views, and components
var unitaste = angular.module('unitaste', [
  'ngRoute',
  'unitaste.view1',
  'unitaste.view2',
  'unitaste.login',
  'unitaste.register',
  'unitaste.profile',
  'unitaste.version'
]).
config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
  $routeProvider.otherwise({redirectTo: '/view1'});
  $httpProvider.defaults.withCredentials = true;
}]);

unitaste.directive('myEnter', function () {
  return function (scope, element, attrs) {
    element.bind("keydown keypress", function (event) {
      if(event.which === 13) {
        scope.$apply(function (){
          scope.$eval(attrs.myEnter);
        });
        event.preventDefault();
      }
    });
  };
});
