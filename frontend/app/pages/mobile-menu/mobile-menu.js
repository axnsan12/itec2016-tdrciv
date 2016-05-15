/**
 * Created by NM on 5/15/2016.
 */


unitaste.controller("MobileMenuController", function($scope, UsersService) {
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
        localStorage.removeItem("loggedIn");
        UsersService.logout().then(function(data){
            localStorage.removeItem("loggedIn");
            console.log("logoutat");
        }).catch(function(data){
            someLog(data);
            console.log("cant logout");
        });
    };

    $scope.checkLogin = function () {
        UsersService.isUserLoggedIn().then(function (data) {
            console.log(dat);
        }).catch(function (data) {
            console.log("err");
            console.log(data);
        });
    };

    $scope.init = function() {
        console.log("asda");
        $('#slide-nav.navbar .container').append($('<div id="navbar-height-col"></div>'));

        // Enter your ids or classes
        var toggler = '.navbar-toggle';
        var pagewrapper = '#page-content';
        var navigationwrapper = '.navbar-header';
        var menuwidth = '100%'; // the menu inside the slide menu itself
        var slidewidth = '80%';
        var menuneg = '-100%';
        var slideneg = '-80%';


        $("#slide-nav").on("click", toggler, function (e) {

            var selected = $(this).hasClass('slide-active');

            $('#slidemenu').stop().animate({
                left: selected ? menuneg : '0px'
            });

            $('#navbar-height-col').stop().animate({
                left: selected ? slideneg : '0px'
            });

            $(pagewrapper).stop().animate({
                left: selected ? '0px' : slidewidth
            });

            $(navigationwrapper).stop().animate({
                left: selected ? '0px' : slidewidth
            });
            $(this).toggleClass('slide-active', !selected);
            $('#slidemenu').toggleClass('slide-active');
            $('#page-content, .navbar, body, .navbar-header').toggleClass('slide-active');
        });
        var selected = '#slidemenu, #page-content, body, .navbar, .navbar-header';
        $(window).on("resize", function () {

            if ($(window).width() > 767 && $('.navbar-toggle').is(':hidden')) {
                $(selected).removeClass('slide-active');
            }
        });

        $(".nav.navbar-nav").on("click", ">li>a", function () {
            $('.navbar-toggle.slide-active').click()
        });
    };
    $scope.init();
});
