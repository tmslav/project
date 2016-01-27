var myApp = angular.module('myApp',['ngResource','ngRoute','ng']);


myApp.config(['$routeProvider','$locationProvider',function($routeProvider,$locationProvider){
    $routeProvider.when('/',{
        templateUrl:"/static/app/tablerow.html",
        controller:"listsController",
    })
}]);

myApp.controller("listsController",["$scope",
    function($scope,$route,$resource,$location,listItems,Items){
        var self = this;

}]);