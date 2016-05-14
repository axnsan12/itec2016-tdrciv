/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.profile', ['ngRoute', 'ngSanitize', 'MassAutoComplete'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/profile', {
            templateUrl: 'views/profile/profile.html',
            controller: 'ProfileController'
        });
    }])

    .controller('ProfileController', function ($scope, UsersService, InterestsService) {
        $scope.loadedInterests = [];
        $scope.profile = {};

        $scope.init = function() {
            InterestsService.getAll().then(function (data) {
                $scope.loadedInterests = data.data.data.interest;
            }).catch(function (data) {
                console.log("Something went wrong!");
                console.log(data);
            });
            UsersService.getProfile().then(function (data) {
                console.log("loaded profile");
                console.log(data);
            }).catch(function (data) {
                console.log("St went wrong");
                console.log(data);
            })

        };
        $scope.init();

    });