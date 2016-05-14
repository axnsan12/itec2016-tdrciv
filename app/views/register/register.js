/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.register', ['ngRoute'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/register', {
            templateUrl: 'views/register/register.html',
            controller: 'RegisterController'
        });
    }])

    .controller('RegisterController', function ($scope, UsersService) {
        $scope.waiting = false;
        $scope.success = false;
        $scope.model = {username:"", password:"", passwordAgain:"", email:""};
        
        $scope.doRegister = function () {
            console.log($scope.model);
            
        };


    });