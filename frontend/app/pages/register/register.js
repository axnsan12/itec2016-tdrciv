/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.register', ['ngRoute', 'ngSanitize', 'MassAutoComplete'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/register', {
            templateUrl: 'pages/register/register.html',
            controller: 'RegisterController'
        });
    }])

    .controller('RegisterController', function ($scope, UsersService, InterestsService) {
        $scope.waiting = false;
        $scope.success = false;
        $scope.errorMessage = false;
        $scope.successMessage = false;
        // $scope.model = {username:"", password:"", passwordAgain:"", email:"", displayName:""};
        $scope.model = {username:"tdr", password:"parola", passwordAgain:"parola", email:"denis.tdr@gmail.com", displayName:"Denis TDR"};


        injectInterestAutoComplete(this, $scope, UsersService, InterestsService);

        $scope.doRegister = function () {
            if($scope.waiting) {
                return;
            }

            if($scope.model.password != $scope.model.passwordAgain) {
                $scope.errorMessage = "Passwords do not match!";
                return;
            }

            $scope.model.interests = [];
            for(var i = 0; i < $scope.selectedExistingInterests.length; i++){
                $scope.model.interests.push({id:$scope.selectedExistingInterests[i].id});
            }
            for(var i = 0; i < $scope.selectedNonExistingInterests.length; i++) {
                $scope.model.interests.push({name: $scope.selectedNonExistingInterests[i].name});
            }


            $scope.waiting  = true;
            $scope.errorMessage = false;

            UsersService.register($scope.model).then(function(data) {
                $scope.waiting = false;
                $scope.successMessage = "Registration successfully. Pleaase check your mail for activation link.";
                clearInterstsAutoCompleteValues($scope);
                $scope.model = {username:"", password:"", passwordAgain:"", email:"", displayName:""};
            }).catch(function (data) {
                $scope.waiting = false;
                switch (data.status) {
                    case 400:
                        $scope.errorMessage = "Invalid field values!";
                        break;
                    default:
                        $scope.errorMessage = data.data.message;

                        break;
                }

            });
        };
        $scope.isLoggedIn = function() {
            return localStorage.getItem("loggedIn") != null;
        };


    });