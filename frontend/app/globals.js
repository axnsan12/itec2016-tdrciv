/**
 * Created by NM on 5/14/2016.
 */


var backend = "http://axnsan.no-ip.org:27015/api/";


var someLog = function (log) {
    console.log(log);
};


var clearInterstsAutoCompleteValues = function($scope) {
    $scope.loadedInterests = [];
    $scope.tmpResults = [];
    $scope.autoCompleteObject = {};
    $scope.selectedExistingInterests = [];
    $scope.selectedNonExistingInterests = [];
    $scope.currentFakeIndex = -1;
};

var injectInterestAutoComplete = function (_this, $scope, UsersService, InterestsService) {


    $scope.loadedInterests = [];
    $scope.tmpResults = [];
    $scope.autoCompleteObject = {};
    $scope.selectedExistingInterests = [];
    $scope.selectedNonExistingInterests = [];
    $scope.currentFakeIndex = -1;

    _this.addInterest = function(interest) {
        console.log("adding interest: ");
        console.log(interest);
        var index;
        if(interest.id == -1) {
            index = _this.searchInterestInArrayByName($scope.selectedNonExistingInterests, interest);
            if(index == -1){
                interest.id = $scope.currentFakeIndex--;
                $scope.selectedNonExistingInterests.push(interest);
            }
        }
        else {
            index = _this.searchInterestInArrayById($scope.selectedExistingInterests, interest);

            if (index == -1) {
                $scope.selectedExistingInterests.push({id: interest.id, name: interest.name});
            }
        }
    };

    $scope.removeInterest = function(interest) {
        //console.log("removing interest");
        //console.log(interest);

        var index = _this.searchInterestInArrayById($scope.selectedExistingInterests, interest);
        if(index != -1){
            $scope.selectedExistingInterests.splice(index, 1);
        }
        else{
            index = _this.searchInterestInArrayById($scope.selectedNonExistingInterests, interest);
            if(index != -1) {
                $scope.selectedNonExistingInterests.splice(index, 1);
            }
        }
    };

    _this.searchInterestInArrayById = function(arr, interest) {
        for(var i = 0; i < arr.length; i++) {
            if(arr[i].id == interest.id) {
                return i;
            }
        }
        return -1;
    };

    _this.searchInterestInArrayByName = function(arr, interest) {
        for(var i = 0; i < arr.length; i++) {
            if(arr[i].name == interest.name) {
                return i;
            }
        }
        return -1;
    };

    $scope.finit = function () {
        InterestsService.getAll().then(function (data) {
            $scope.loadedInterests = data.data.data.interests;
            console.log("interests loaded");
            //console.log($scope.loadedInterests);
            //console.log(data);

        }).catch(function (data) {
            console.log("cant load interests");
        })
    };

    $scope.finit();

    _this.suggest_interest = function (term) {
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
        suggest: _this.suggest_interest,
        on_select: _this.addInterest
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
        _this.addInterest({name: $scope.autoCompleteObject.value, id:-1});
        $scope.autoCompleteObject.value = "";
    };
};

//
// Date.prototype.getUnixTime = function() { return this.getTime()/1000|0 };
// if(!Date.now) Date.now = function() { return new Date(); }
// Date.time = function() { return Date.now().getUnixTime(); }