/**
 * Created by NM on 5/14/2016.
 */

'use strict';

angular.module('unitaste.register', ['ngRoute', 'ngSanitize', 'MassAutoComplete'])

    .config(['$routeProvider', function($routeProvider) {
        $routeProvider.when('/register', {
            templateUrl: 'views/register/register.html',
            controller: 'RegisterController'
        });
    }])

    .controller('RegisterController', function ($scope, UsersService, InterestsService) {
        $scope.waiting = false;
        $scope.success = false;
        $scope.errorMessage = false;
        $scope.successMessage = false;
        $scope.model = {username:"tdr", password:"parola", passwordAgain:"parola", email:"denis.tdr@gmail.com", displayName:"Denis TDR"};
        $scope.loadedInterests = [];
        $scope.tmpResults = [];
        $scope.autoCompleteObject = {};
        $scope.selectedExistingInterests = [];
        $scope.selectedNonExistingInterests = [];
        $scope.currentFakeIndex = -1;
        
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
                $scope.successMessage = "Registration successfully. You will be redirected to login in a few seconds ...";
                
                setTimeout(function() {
                    window.location.href = "#/login";
                }, 3000);
            }).catch(function (data) {
                $scope.waiting = false;
                switch (data.status) {
                    case 400:
                        $scope.errorMessage = "Invalid field values!";
                        break;
                    default:
                        $scope.errorMessage = data.message;
                        break;
                }

            });
        };

        var addInterest = function(interest) {
            console.log("adding interest: ");
            console.log(interest);
            var index;
            if(interest.id == -1) {
                index = searchInterestInArrayByName($scope.selectedNonExistingInterests, interest);
                if(index == -1){
                    interest.id = $scope.currentFakeIndex--;
                    $scope.selectedNonExistingInterests.push(interest);
                }
            }
            else {
                index = searchInterestInArrayById($scope.selectedExistingInterests, interest);

                if (index == -1) {
                    $scope.selectedExistingInterests.push({id: interest.id, name: interest.name});
                }
            }
        };

        $scope.removeInterest = function(interest) {
            //console.log("removing interest");
            //console.log(interest);

            var index = searchInterestInArrayById($scope.selectedExistingInterests, interest);
            if(index != -1){
                $scope.selectedExistingInterests.splice(index, 1);
            }
            else{
                index = searchInterestInArrayById($scope.selectedNonExistingInterests, interest);
                if(index != -1) {
                    $scope.selectedNonExistingInterests.splice(index, 1);
                }
            }
        };

        var searchInterestInArrayById = function(arr, interest) {
            for(var i = 0; i < arr.length; i++) {
                if(arr[i].id == interest.id) {
                    return i;
                }
            }
            return -1;
        };

        var searchInterestInArrayByName = function(arr, interest) {
            for(var i = 0; i < arr.length; i++) {
                if(arr[i].name == interest.name) {
                    return i;
                }
            }
            return -1;
        };

        $scope.init = function () {
            InterestsService.getAll().then(function (data) {
                $scope.loadedInterests = data.data.data.interests;
                console.log("interests loaded");
                //console.log($scope.loadedInterests);
                //console.log(data);

            }).catch(function (data) {
                console.log("cant load interests");
            })
        };

        $scope.init();

        var suggest_interest = function (term) {
            var q = term.toLowerCase().trim();
            var results = [];
            //console.log("search!");
            // Find first 10 states that start with `term`.
            for (var i = 0; i < $scope.loadedInterests.length && results.length < 10; i++) {
                var state = $scope.loadedInterests[i];
                if (state.name.toLowerCase().indexOf(q) !== -1) {
                    results.push({id: state.id, label: state.name, name: state.name});
                    //console.log(state);
                }
            }

            return $scope.tmpResults = results;
        };

        $scope.autocomplete_options = {
            suggest: suggest_interest,
            on_select: addInterest
        };

        $scope.enterPressedInAutComplete = function() {
            var _registerAutocomplete = $("#registerAutocomplete");
            if($scope.tmpResults.length) {
                var selected = _registerAutocomplete.find(".ac-state-focus");
                if(selected){
                    var index = selected.index();
                    console.log("index=" + index);
                    if(index !== -1) {
                        return;
                    }
                }
            }
            console.log($scope.autoCompleteObject.value);
            addInterest({name: $scope.autoCompleteObject.value, id:-1});
            $scope.autoCompleteObject.value = "";
        };
    });