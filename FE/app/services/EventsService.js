/**
 * Created by NM on 5/13/2016.
 */

unitaste.service("EventsService", function ($http) {
    this.getAll = function () {
        return $http.get(backend+"events");
    };

    this.get = function (id) {
        return $http.get(backend+"events/"+id);
    };
});