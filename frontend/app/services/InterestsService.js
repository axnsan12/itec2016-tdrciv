/**
 * Created by NM on 5/14/2016.
 */

unitaste.service("InterestsService", function ($http) {
    this.getAll = function () {
        return $http.get(backend+"interests");
    };

    this.get = function (id) {
        return $http.get(backend+"interests/"+id);
    };

    this.add = function (model) {
        return $http.post(backend+"interests/", model);
    }
});