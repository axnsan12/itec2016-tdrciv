/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.lounge', ['ngRoute', 'ngSanitize', 'MassAutoComplete'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/lounge', {
            templateUrl: 'pages/lounge/lounge.html',
            controller: 'LoungeController'
        });
    }])

    .controller('LoungeController', function ($scope, EventsService, InterestsService) {
        console.log("lounge loaded");

        $scope.events = [];
        $scope.joinComment = [];
        $scope.activeEventId = -1;

        $scope.join = function(event) {
            someLog("joining: "+event.id);
            EventsService.join(event.id, {comment: $scope.joinComment[event.id]}).then(function (data) {
                someLog("joined event");
                console.log(data);
                if(data.data.status != "success") {
                    someLog("something went wrong!");
                }
                else {
                    event.joined = true;
                }
                $scope.init();

            }).catch(function (data) {
                someLog("err join event");
                someLog(data);
                $scope.init();
            });
        };

        $scope.unJoin = function(event) {
            someLog("unjoining: "+event.id);
            EventsService.unJoin(event.id).then(function (data) {
                someLog("unjoined event");
                someLog(data);
                event.joined = false;
                $scope.init();
            }).catch(function (data) {
                someLog("err unjoin event");
                someLog(data);
                $scope.init();
            });

        };

        $scope.toggleActive = function (event) {
            $scope.activeEventId = $scope.activeEventId == event.id ? -1 : event.id;
        };

        $scope.init = function (){
            EventsService.getAll().then(function (data) {
                $scope.events = data.data.data.events;
                someLog("loaded events");
                someLog( data.data.data.events);
                $scope.activeEventId = -1;
            }).catch(function (data) {
                someLog("err getAll events");
                someLog(data);
                $scope.activeEventId = -1;
            });
        };
        $scope.init();

    });