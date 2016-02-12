var myApp = angular.module('myApp', ['ngResource', 'ngRoute', 'ng']);

myApp.config(['$routeProvider', '$locationProvider', function ($routeProvider, $locationProvider) {
    $routeProvider.when('/', {
        templateUrl: "/static/app/tablerow.html",
        controller: "Results",
    }).when("/items/:site_id", {
        templateUrl: "/static/app/products.html",
        controller: "ProductDetailController"
    })
}]);

//FACTORY RESOURCE
myApp.factory('Results', function ($resource) {
    return $resource('/results/');
});

myApp.factory("Items", function ($resource) {
    return $resource("/items/:site_id")
})

//CONTROLLERS
myApp.controller("ProductDetailController", function ($scope, $routeParams, Items) {
    var that = $scope.list = [];
    var scope = $scope;
    Items.get({'site_id': $routeParams.site_id}, function (data) {
        for (i = 0; i < data.items.length; i++) {
            push = data.items[i]
            push['search_name'] = data['search_name']
            that.push(push)
        }
        scope.search_name = data['search_name'];
        scope.timestamp = data['timestamp'].replace("T", " ");
        debugger;
    });
});

myApp.controller('MyCtrl', ['$scope', 'Upload', function ($scope, Upload) {
    // upload later on form submit or something similar
    $scope.submit = function () {
        if ($scope.form.file.$valid && $scope.file) {
            $scope.upload($scope.file);
        }
    };

    // upload on file select or drop
    $scope.upload = function (file) {
        Upload.upload({
            url: 'upload/url',
            data: {file: file, 'username': $scope.username}
        }).then(function (resp) {
            console.log('Success ' + resp.config.data.file.name + 'uploaded. Response: ' + resp.data);
        }, function (resp) {
            console.log('Error status: ' + resp.status);
        }, function (evt) {
            var progressPercentage = parseInt(100.0 * evt.loaded / evt.total);
            console.log('progress: ' + progressPercentage + '% ' + evt.config.data.file.name);
        });
    };
}]);
myApp.controller('Results', function ($scope, Results) {
    $scope.list = [];
    var that = $scope.list
    Results.get(function (data) {
        for (i = 0; i < data.results.length; i++) {
            that.push(data.results[i]);
        }
    });
});
