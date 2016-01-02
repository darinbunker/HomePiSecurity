
var app = angular.module('auth', ['ngRoute', 'ngMaterial', 'ngCookies']).config(function(){
	});

app.factory('AuthenticationService', function($http, $cookies, $window){
	return {
		login: function(credentials, authtoken){
			// First send the credentials to the service for checking
			var submission = {};
			submission["username"] = credentials.username;
			submission["password"] = credentials.password;
			
			$http({
				method: 'POST',
				url: url + '/authenticate',
				data: submission
			}).then(function(response){
				authtoken = response;

				if (authtoken.data.authorized){					
					//set cookies with auth token
					var cookieDate = new Date();
					$cookies.hssid = authtoken.data.authToken.token;

					//$location.path('/app');
					$window.location.href = 'index.html';
				};
				credentials.password = undefined;
			});
		}
	};
});

app.controller('LoginController', function($scope, AuthenticationService){

	init();

	function init(){
		//window.scope = $scope;
		$scope.credentials = { username: "", password: ""};
		$scope.authtoken = {authorized: "", username: "", token: ""};

		$scope.login = login;
	}

	function login(){
		AuthenticationService.login($scope.credentials, $scope.authtoken);
	}

});


















