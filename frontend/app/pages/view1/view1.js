'use strict';

angular.module('unitaste.view1', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/view1', {
    templateUrl: 'pages/view1/view1.html',
    controller: 'View1Ctrl'
  });
}])

.controller('View1Ctrl', function($scope, UsersService) {
  $scope.action = function() {
    console.log("an action?");
    UsersService.test().then(function(data) {
      console.log(data);
    });
  };
});