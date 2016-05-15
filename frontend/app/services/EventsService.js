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

    this.get4Me = function (){
        return $http.get(backend+"events/me");
    };

    this.add = function(event) {
        return $http.post(backend + "events", event);
    };

    this.join = function(eventId, body) {
        return $http.post(backend+"events/"+eventId+"/join", body);
    };

    this.unJoin = function(eventId) {
        return $http.post(backend+"events/"+eventId+"/unjoin", {});
    };
});