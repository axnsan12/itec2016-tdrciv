/**
 * Created by NM on 5/13/2016.
 */

unitaste.service("UsersService", function ($http) {

    this.login = function (loginModel) {
        console.log("requesting login...");
        return $http.post(backend + "login", loginModel);
    };

    this.loggedInUser = function () {
        console.log("checking login");
        return $http.get(backend+"user");
    };

    this.logout = function(){
        return $http.post(backend + "logout", {});
    };

    this.register = function (registerModel) {
        console.log("requesting register ...");
        return $http.post(backend + "register", registerModel);
    }

});