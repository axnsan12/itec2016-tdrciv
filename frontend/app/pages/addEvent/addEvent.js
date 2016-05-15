/**
 * Created by NM on 5/14/2016.
 */


'use strict';

angular.module('unitaste.addEvent', ['ngRoute', 'ngSanitize', 'MassAutoComplete'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/addEvent', {
            templateUrl: 'pages/addEvent/addEvent.html',
            controller: 'AddEventController'
        });
    }])

    .controller('AddEventController', function ($scope, UsersService, InterestsService, EventsService) {
        $scope.model = {name:"", startDate:"11/18/2016 11:58", interests:[], comment: "" };

        $scope.loadedInterests = [];
        $scope.tmpResults = [];
        $scope.autoCompleteObject = {};
        $scope.selectedExistingInterests = [];
        $scope.selectedNonExistingInterests = [];
        $scope.currentFakeIndex = -1;

        injectInterestAutoComplete(this, $scope, UsersService, InterestsService);

        someLog("add event controller loaded");

        $scope.createEvent = function () {
            var model = {name: $scope.model.name, interests: [], comment:$scope.model.comment};
            $scope.model.interests = [];
            var i;
            for(i = 0; i < $scope.selectedExistingInterests.length; i++){
                model.interests.push({id:$scope.selectedExistingInterests[i].id});
            }
            for(i = 0; i < $scope.selectedNonExistingInterests.length; i++) {
                model.interests.push({name: $scope.selectedNonExistingInterests[i].name});
            }

            model.startTime = new Date($scope.model.startDate).getTime()/1000;

            someLog("adding event");
            someLog(model);
            EventsService.add(model).then(function (data) {
                someLog("event added");
                someLog(data);
            }).catch(function (data) {
                someLog("err add event");
                someLog(data);
            });
        };


        $scope.init = function () {

        };
        $scope.init();

    });
