/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.login', ['ngRoute'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/login', {
            templateUrl: 'pages/login/login.html',
            controller: 'LoginController'
        });
    }])

    .controller('LoginController', function($scope, UsersService, $location) {
        $scope.waiting = false;
        $scope.success = false;
        $scope.errorMessage = false;
        $scope.model = {username:"tdr", password:"parola"};

        $scope.doLogin = function () {
            if($scope.waiting) {
                return;
            }
            $scope.waiting  = true;
            $scope.errorMessage = false;
            //$scope.waiting = true;
            UsersService.login($scope.model).then(function (data) {
                console.log(data);
                $scope.waiting = false;
                $scope.successMessage = "Successfully logged in! \n Checking things ...";
                console.log("sending login request ...");
                UsersService.isUserLoggedIn().then(function (data) {
                    console.log("you are logged bă");
                    console.log(data);
                    localStorage.setItem("loggedIn", "yes?");
                    $scope.successMessage = "You will be redirected to home page in a few seconds ...";

                    //$location.path( "/" );
                    setTimeout(function() {
                        console.log("redirect in plm");
                        window.location.href = "/";

                        console.log("redirect in plm");
                    }, 3000);
                }).catch(function (data) {
                    console.log("err2");
                    console.log(data);
                    $scope.errorMessage = "Something went very wrong!";
                });
            }).catch(function(data) {
                console.log("err");

                $scope.waiting = false;
                switch(data.status) {
                    case 401:
                        $scope.errorMessage = "Invalid username or password!"
                        break;
                    case 400:
                        $scope.errorMessage = "Invalid fields value!";
                        break;
                    default:
                        $scope.errorMessage = "An error occurred! Try again!";
                        break;
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