angular.module('app', ['ngRoute']);

angular.module('app').config(function ($routeProvider) {
    $routeProvider.when('/home', {templateUrl: 'home.html'});
    $routeProvider.when('/expenses/edit', {templateUrl: 'expense_edit.html', controller: 'appExpenseEditCtrl'});
    $routeProvider.otherwise('/home');
});

angular.module('app').controller('appExpenseEditCtrl', function ($scope, $http) {
    $scope.data = {
        date: moment().format('YYYY-MM-DD'),
        gimmiAmount: 0,
        elenaAmount: 0,
        gimmiDebt: 0,
        elenaDebt: 0,
        description: '',
        categoryId: null
    };
    $scope.categories = [];

    $http.get('/api/expensecategories').then(function (ret) {
        $scope.categories = ret.data.data;
    });
});

angular.module('app').directive('appDatepicker', function () {
    return {
        restrict: 'A',
        link: function (scope, elem, attrs) {
            elem.datepicker({
                format: "yyyy-mm-dd",
                weekStart: 1,
                language: "it"
            });
        }
    };
});