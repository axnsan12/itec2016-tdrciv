/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.login', ['ngRoute'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/login', {
            templateUrl: 'views/login/login.html',
            controller: 'LoginController'
        });
    }])

    .controller('LoginController', function($scope, UsersService, $location) {
        $scope.waiting = false;
        $scope.success = false;
        $scope.errorMessage = false;
        $scope.model = {username:"axnsan", password:"parola"};

        $scope.doLogin = function () {
            if($scope.waiting) {
                return;
            }
            //$scope.waiting = true;
            console.log(1);
            UsersService.login($scope.model).then(function (data) {
                console.log(data);
                UsersService.loggedInUser().then(function (data) {
                    console.log("loggedInUser");
                    console.log(data);
                    localStorage.setItem("loggedIn", "yes?");
                    $location.path( "/" );
                }).catch(function (data) {
                    console.log("err2");
                    console.log(data);
                });
            }).catch(function(data) {
                console.log("err");

                $scope.waiting = false;
                if(data.status == 401) {
                    $scope.errorMessage = "Invalid username or password!"
                }
                else {
                    $scope.errorMessage = "An error occurred!";
                }

            });
            
            console.log($scope.model);
        };

        

        $scope.doLogin2 = function () {
            console.log("zsdfsdfsdfsdfsdfsdfsd");
        };
        $scope.isLoggedIn = function() {
            return localStorage.getItem("loggedIn") != null;
        };

        console.log($scope.isLoggedIn());
    });