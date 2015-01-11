angular.module('app', ['ngRoute']);

angular.module('app').config(function ($routeProvider) {
    $routeProvider.when('/home', {templateUrl: 'home.html'});
    $routeProvider.when('/expenses/edit', {templateUrl: 'expense_edit.html', controller: 'appExpenseEditCtrl'});
    $routeProvider.otherwise('/home');
});

angular.module('app').controller('appExpenseEditCtrl', function ($scope, $http) {
    $scope.data = {};

    $scope.categories = [];

    $scope.succesfulExpenses = [];

    $scope.dateChanged = function () {
        if ($scope.data.date) {
            $scope.data.startMonth = moment($scope.data.date, 'YYYY-MM-DD').format('YYYY-MM');
        } else {
            $scope.data.startMonth = null;
        }
        $scope.startMonthChanged();
    };

    $scope.startMonthChanged = function () {
        $scope.data.endMonth = $scope.data.startMonth;
    };

    $scope.submit = function () {
        $http.post('/api/expenses', $scope.data).then(function (ret) {
            var str = [ret.data.date, ret.data.gimmiAmount + ret.data.elenaAmount].join('/');
            $scope.succesfulExpenses.unshift(ret.data);
            reset();
        });
    };

    reset();
    $http.get('/api/expensecategories').then(function (ret) {
        $scope.categories = ret.data.data;
    });

    function reset() {
        angular.extend($scope.data, {
            date: moment().format('YYYY-MM-DD'),
            dueDate: moment().format('YYYY-MM'),
            monthSpread: 1,
            gimmiAmount: 0,
            elenaAmount: 0,
            gimmiDebt: 0,
            elenaDebt: 0,
            description: '',
            categoryId: null
        });
    }
});

angular.module('app').directive('appDatepicker', function () {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, elem, attrs, ngModelController) {
            ngModelController.$validators.validDate = function (value) {
                return value && moment(value, 'YYYY-MM-DD', true).isValid();
            };

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
        link: function (scope, elem, attrs, ngModelController) {
            ngModelController.$validators.validMonth = function (value) {
                return value && moment(value, 'YYYY-MM', true).isValid();
            };

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
