var myApp = angular.module('myApp',['ngResource','ngRoute','ng','ngSanitize','ngCsv']);

myApp.factory('listItems',['$resource',function($resource){
    return $resource('api',{},{
        'post':{method:'POST'},
        'get':{method:'GET'}
    })
}]);


myApp.config(['$routeProvider','$locationProvider',function($routeProvider,$locationProvider){
    $routeProvider.when('/',{
        templateUrl:"/static/app/tablerow.html",
        controller:"listsController",
    }).when('/items/:item_id',{
        templateUrl:'/static/app/editrow.html',
        controller:'itemController'
    })
}]);

myApp.controller("listsController",["$scope",'$route',"$resource","$location","listItems","Items",
    function($scope,$route,$resource,$location,listItems,Items){
        var self = this;

}]);