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

    .controller('LoungeController', function ($scope, EventsService, InterestsService, $location) {
        console.log("lounge loaded");

        $scope.joinErrorMessage = "";
        $scope.joinSuccesMessage = "";
        $scope.waiting = false;

        $scope.events = [];
        $scope.joinComment = "";
        $scope.activeEventId = -1;
        $scope.selectedEvent = null;

        $scope.join = function(event) {
            someLog("joining: "+event.id);
            $scope.joinErrorMessage = "";
            $scope.joinSuccesMessage = "";
            $scope.waiting = false;
            EventsService.join(event.id, {comment: $scope.joinComment}).then(function (data) {
                someLog("joined event");
                someLog(data);
                if(data.data.status != "success") {
                    someLog("something went wrong!");
                    $scope.joinErrorMessage = "Something went wrong. Please try again.";
                    return;
                }
                else {
                    event.joined = true;
                }
                $scope.init();
                $("#joinEventModal").modal('hide');

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
            if( $scope.activeEventId == event.id) {
                $("#event" + $scope.activeEventId + " .userComments").slideUp();
                $scope.activeEventId = -1;
                someLog(1);
            }
            else {
                $("#event" + $scope.activeEventId + " .userComments").slideUp();
                $("#event" + event.id + " .userComments").slideDown();
                $scope.activeEventId = event.id;
                someLog(2);
            }
        };

        $scope.showJoinModal = function (event){
            $scope.selectedEvent = event;
            $("#joinEventModal").modal('show');
        };
        

        $scope.init = function (){
            if(!$scope.isLoggedIn()) {
                $scope.changeRoute('#/login');
                return;
            }
            $scope.joinComment = "";
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
        $scope.isLoggedIn = function() {
            return localStorage.getItem("loggedIn") != null;
        };
        $scope.changeRoute = function(url, forceReload) {
            $scope = $scope || angular.element(document).scope();
            if(forceReload || $scope.$$phase) { // that's right TWO dollar signs: $$phase
                window.location = url;
            } else {
                $location.path(url);
                $scope.$apply();
            }
        };


        $scope.init();

    });