angular.module('app', ['ngRoute']);

angular.module('app').config(function ($routeProvider) {
    $routeProvider.when('/home', {templateUrl: 'home.html'});
    $routeProvider.when('/expenses/edit', {templateUrl: 'expense_edit.html', controller: 'appExpenseEditCtrl'});
    $routeProvider.otherwise('/home');
});

angular.module('app').controller('appExpenseEditCtrl', function ($scope, $http) {
    $scope.data = {
        date: moment().format('YYYY-MM-DD'),
        startMonth: moment().format('YYYY-MM'),
        endMonth: moment().format('YYYY-MM'),
        gimmiAmount: 0,
        elenaAmount: 0,
        gimmiDebt: 0,
        elenaDebt: 0,
        description: '',
        categoryId: null
    };

    $scope.categories = [];

    $scope.dateChanged = function () {
        if ($scope.data.date) {
            $scope.data.startMonth = moment($scope.data.date, 'YYYY-MM-DD').format('YYYY-MM');
        } else {
            $scope.data.startMonth = null;
        }
    };

    $http.get('/api/expensecategories').then(function (ret) {
        $scope.categories = ret.data.data;
    });

});

angular.module('app').directive('appDaypicker', function () {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, elem, attrs, ngModelController) {
            elem.datepicker({
                format: "yyyy-mm-dd",
                weekStart: 1,
                language: "it",
                todayBtn: "linked",
                autoclose: true,
                todayHighlight: true
            });

            scope.$watch(attrs.ngModel, function () {
                elem.datepicker('update');
            });
        }
    };
});

angular.module('app').directive('appMonthpicker', function () {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, elem, attrs) {
            elem.datepicker({
                format: "yyyy-mm",
                language: "it",
                startView: 1,
                minViewMode: 1
            });

            scope.$watch(attrs.ngModel, function () {
                elem.datepicker('update');
            });
        }
    };
});
