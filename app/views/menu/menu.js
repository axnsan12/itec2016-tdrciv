/**
 * Created by NM on 5/13/2016.
 */

unitaste.controller("MenuController", function($scope, UsersService) {
    console.log("menu loaded");
    $scope.menuFull = true;
    $scope.toggleMenu = function() {
        if($scope.menuFull) {
            $("#wrapper").addClass("semiToggled");
        }
        else {
            $("#wrapper").removeClass("semiToggled");
        }
        $scope.menuFull = !$scope.menuFull;
    };

    $scope.isLoggedIn = function () {
        return localStorage.getItem("loggedIn") != null;
    };

    $scope.doLogout = function () {
        UsersService.logout().then(function(data){
            localStorage.removeItem("loggedIn");
            console.log("logoutat");
        }).catch(function(data){
            console.log("cant logout");
        });
    };
});