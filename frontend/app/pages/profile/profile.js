/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.profile', ['ngRoute', 'ngSanitize', 'MassAutoComplete'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/profile', {
            templateUrl: 'pages/profile/profile.html',
            controller: 'ProfileController'
        });
    }])

    .controller('ProfileController', function ($scope, UsersService, InterestsService) {
        $scope.loadedInterests = [];
        $scope.profile = {};
        $scope.initialInterests = [];
        $scope.toDeleteInterests = [];
        $scope.waiting = false;
        injectInterestAutoComplete(this, $scope, UsersService, InterestsService);

        $scope.doSaveProfile = function () {

            $scope.profile.interests = [];
            var i;
            for(i = 0; i < $scope.selectedExistingInterests.length; i++){
                if(!isIdInArray($scope.selectedExistingInterests[i].id, $scope.initialInterests)) {
                    $scope.profile.interests.push({id: $scope.selectedExistingInterests[i].id});
                }
            }
            for(i = 0; i < $scope.selectedNonExistingInterests.length; i++) {
                $scope.profile.interests.push({name: $scope.selectedNonExistingInterests[i].name});
            }
            for(i = 0; i < $scope.toDeleteInterests.length; i++) {
                $scope.profile.interests.push({id: $scope.toDeleteInterests[i].id, delete: true});
            }
            someLog("saving profile");
            someLog($scope.profile);
            $scope.waiting = true;
            // return;
            UsersService.saveProfile($scope.profile).then(function (data) {
                someLog("saved profile");
                someLog(data);
                $scope.waiting = false;
                $scope.toDeleteInterests = [];
                $scope.initialInterests = [];
                $scope.profile = data.data.data;
                $scope.selectedExistingInterests = $scope.profile.interests;
                for(var i = 0; i < $scope.profile.interests.length; i++) {
                    $scope.initialInterests.push({id: $scope.profile.interests[i].id});
                }
            }).catch(function (data) {
                someLog("st went wrong");
                someLog(data);
                $scope.waiting = false;
            });
        };

        var isIdInArray = function (id, arr) {
            for(var i = 0; i < arr.length; i++) {
                if(arr[i].id == id) {
                    return true;
                }
            }
            return false;
        };

        $scope.removeInterestNew = function (interest) {
            someLog("remove i new");
            $scope.removeInterest(interest);
            for(var i = 0; i < $scope.initialInterests.length; i++){
                if($scope.initialInterests[i].id == interest.id){
                    var ok = true;
                    for(var j = 0; j < $scope.toDeleteInterests.length; j++){
                        if($scope.toDeleteInterests[j].id == interest.id) {
                            ok = false;
                        }
                    }
                    if(ok) {
                        $scope.toDeleteInterests.push({id: interest.id, delete:true});
                        someLog("added interest in toDelete list");
                    }
                }
            }
        };

        this.addInterestOld = this.addInterest;
        this.addInterest = function (interest) {
            this.addInterestOld(interest);
            for(var i = 0; i < $scope.toDeleteInterests.length ;i++) {
                if($scope.toDeleteInterests[i].id == interest.id){
                    $scope.toDeleteInterests.slice(i, 1);
                    someLog("removed interest from delete list");
                }
            }
        };

        $scope.init = function() {
            InterestsService.getAll().then(function (data) {
                $scope.loadedInterests = data.data.data.interests;
            }).catch(function (data) {
                console.log("Something went wrong!");
                console.log(data);
            });
            UsersService.getProfile().then(function (data) {
                $scope.profile = data.data.data;
                $scope.selectedExistingInterests = $scope.profile.interests;
                for(var i = 0; i < $scope.profile.interests.length; i++) {
                    $scope.initialInterests.push({id: $scope.profile.interests[i].id});
                }
                console.log("loaded profile");
                console.log($scope.profile);
            }).catch(function (data) {
                console.log("St went wrong");
                console.log(data);
            });
            console.log($scope.isLoggedIn());
        };


        $scope.passwordModel = {};
        $scope.changePasswordError = false;
        $scope.changePasswordWaiting = false;
        $scope.changePasswordMessage = false;
        $scope.changePassword = function () {
            if($scope.passwordModel.password != $scope.passwordModel.passwordAgain){
                $scope.changePasswordError = "Passwords do not match!";
                return;
            }
            $scope.changePasswordWaiting = true;
            var model = {currentPassword: $scope.passwordModel.oldPassword, newPassword: $scope.passwordModel.password};
            someLog(model);
            UsersService.changePassword(model).then(function (data) {
                $scope.changePasswordWaiting = false;
                $scope.changePasswordMessage = "Something went wrong!";
                if(data.status == 200) {
                    $scope.changePasswordMessage = "Password changed!";
                }
                someLog(data);

            }).catch(function (data) {
                $scope.changePasswordWaiting = false;
                $scope.changePasswordMessage = "Something went wrong!";
            });
        };
        $scope.isLoggedIn = function() {
            return localStorage.getItem("loggedIn") != null;
        };
        $scope.init();
    });