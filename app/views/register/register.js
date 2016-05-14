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
        $scope.errorMessage = false;
        $scope.successMessage = false;
        $scope.model = {username:"", password:"", passwordAgain:"", email:""};
        
        $scope.doRegister = function () {
            if($scope.waiting) {
                return;
            }
            console.log($scope.model);
            $scope.waiting  = true;
            $scope.errorMessage = false;
            UsersService.register($scope.model).then(function(data) {
                $scope.waiting = false;
                $scope.successMessage = "Registration successfully. You will be redirected to login in a few seconds ...";
                
                setTimeout(function() {
                    $location.path( "/login" );
                }, 3000);
            }).catch(function (data) {
                $scope.waiting = false;
                switch (data.status) {
                    case 400:
                        $scope.errorMessage = "Invalid username or password!"
                        break;
                    default:
                        $scope.errorMessage = "Something went wrong!";
                }

            });
        };


    });