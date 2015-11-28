
var url = "https://SetServicePathVariable:SetServicePortVariable";
var app = angular.module('app', ['ngRoute', 'ngMaterial', 'ngCookies']).config(function($locationProvider, $routeProvider, $filterProvider){

		$routeProvider.when('/login', {
			templateUrl: 'templates/login.html',
			controller: 'LoginController'
		});
		$routeProvider.when('/state', {
			templateUrl: 'templates/state.html',
			controller: 'StateController'
		});
		$routeProvider.when('/schedules', {
			templateUrl: 'templates/schedules.html',
			controller: 'ScheduleController'
		});
		$routeProvider.when('/users', {
			templateUrl: 'templates/users.html',
			controller: 'UserController'
		});
		$routeProvider.when('/configuration', {
			templateUrl: 'templates/configuration.html',
			controller: 'ConfigurationController'
		});
		$routeProvider.otherwise({ redirectTo : '/login' });

		$filterProvider.register("schedule_day", function() {
	        return function(dayOfWeek) {
	            returnVal = "";
	            if(dayOfWeek === 0) {
	                returnVal = "Sunday";
	            } else if (dayOfWeek === 1) {
	                returnVal = "Monday";
	            } else if (dayOfWeek === 2) {
	                returnVal = "Tuesday";
	            } else if (dayOfWeek === 3) {
	                returnVal = "Wednesday";
	            } else if (dayOfWeek === 4) {
	                returnVal = "Thursday";
	            } else if (dayOfWeek === 5) {
	                returnVal = "Friday";
	            } else if (dayOfWeek === 6) {
	                returnVal = "Saturday";
	            } else {
	            	returnVal = "None";
	            }
	            return returnVal;
        	};
    	});

    	$filterProvider.register("schedule_minute", function() {
	        return function(inputMinute) {
	            returnVal = "";
	            if(inputMinute.toString().length == 2) {
	                returnVal = inputMinute;
	            } else if (inputMinute.toString().length == 1) {
	                returnVal = "0" + inputMinute;
	            } else {
	            	returnVal = inputMinute;
	            }
	            return returnVal;
        	};
    	});

	});

app.factory('AuthenticationService', function($location, $http, $cookies, NavigationService){
	return {
		login: function(credentials, authtoken){
			// First send the credentials to the service for checking
			$http.post(url + "/authenticate", {username: credentials.username, password: credentials.password})
			.success(function(response){
				authtoken = response;

				if (authtoken.authorized){
					NavigationService.setLoginStatus(true);
					//set cookies to show navigation
					var cookieDate = new Date();
					$cookies.showNavigation = true;
					$cookies.showNavigationExpire = cookieDate;

					$location.path('/state');
				};
				credentials.password = undefined;
			});
		},
		logout: function(authtoken){
			//authtoken = undefined;
			$cookies['navtab'] = 0;
			$cookies['navtabexpire'] = undefined;
			//NavigationService.setLoginStatus(false);
    		$location.path('/login');
		}
	};
});

app.service('TransferService', function() {
  var ItemList;

  var addItem = function(newObj) {
      //scheduleList.push(newObj);
      ItemList = newObj;
  }

  var getItem = function(){
      return ItemList;
  }

  return {
    addItem: addItem,
    getItem: getItem
  };
});

app.service('NavigationService', function() {
	var loginStatus = false;
	var currentTab = 0;

	var navTabs = [
		    { index: 0, type: 'state', route: '/state' },
		    { index: 1, type: 'schedules', route: '/schedules' },
		    { index: 2, type: 'users', route: '/users' },
		    { index: 3, type: 'configuration', route: '/configuration' },
		    { index: 4, type: 'logout', route: '/logout' }
		  ];

	var setLoginStatus = function(newObj) {
		loginStatus = newObj;
	}

	var getLoginStatus = function() {
		return loginStatus;
	}

	var getNavTabs = function() {
		return navTabs;
	}

	var setCurrentTab = function(newObj) {
		currentTab = newObj;
	}

	var getCurrentTab = function() {
		return currentTab;
	}

	return {
		setLoginStatus: setLoginStatus,
		getLoginStatus: getLoginStatus,
		getNavTabs: getNavTabs,
		setCurrentTab: setCurrentTab,
		getCurrentTab: getCurrentTab
	};
});

app.controller('StateController', function($scope, $http, $location, AuthenticationService, NavigationService){
	init();

	function init() {
	  	//$scope.logout = logout;
	  	$scope.setArmed = setArmed;
	    $scope.loadState = loadState;
	    $scope.loadBackground = loadBackground;
	    //$scope.routeNav = routeNav;

	    setLoginStatus();

	    //load state for first execution
    	$scope.loadState();
	}

	function setLoginStatus () {
		NavigationService.setLoginStatus(true);
		NavigationService.setCurrentTab(0);
	}

	// function logout(){
	// 	AuthenticationService.logout($scope.authtoken);
	// }

    function setArmed(state, type){
    	//get the module ID and state
    	//types:
    	// - 0: Disarm, 1: Arm and Hold, 2: Arm Temporary
    	var putURL = "";
    	// Determine the endpoint
    	if (type == 0){
    		// need to determine if disable is required
    		if (state.active_override > 0) {
    			putURL += "/state/override/" + state.id + "/0";	
    		} else if (state.active_schedule > 0) {
    			putURL += "/state/deactivate/" + state.id + "/1";
    		}
    	} else if (type == 1) {
    		putURL += "/state/override/" + state.id + "/1";
    	} else if (type == 2) {
    		putURL += "/state/override/" + state.id + "/2";
    	}
    	
    	$http.put(url + putURL)
			.success(function (data) {
    			//console.log('success: ' + data)
    			//Reload state
    			$scope.loadState();
			})
    }

    function loadState(){
    	$http.get(url + "/state")
	    .success(function(response) {
	    	$scope.states = response;
	    	//Load the current state of the system
	    	determineArmedState();
	    });
    }

    function loadBackground(){
    	$scope.showBackground = 1;
    }

 //    function routeNav(type){
	// 	var route = "";

	// 	if (type == 'state') {
	// 		route = "/state";
	// 	} else if (type == 'schedules') {
	// 		route = "/schedules";
	// 	} else if (type == 'users') {
	// 		route = "/users";
	// 	} else if (type == "configuration") {
	// 		route = "/configuration";
	// 	}

	// 	if (route != "") {
	// 		$location.path(route);	
	// 	}
		
	// }

    function determineArmedState(){
    	//Check the state object to determine the armed state - Loop through the state objects

		for (var i = 0; i < $scope.states.length; i++) {
			var armType;
		    // - First check if the active_override is set
		    $scope.states[i].armed = "not-armed";
	    	if ($scope.states[i].active_override == 1){
	    		$scope.states[i].armedDisplay = "ARMED - Hold";
	    		armType = "arm-hold";
	    	} else if ($scope.states[i].active_override == 2) {
	    		$scope.states[i].armedDisplay = "ARMED";
	    		armType = "arm-temp";
	    	} else if ($scope.states[i].active_schedule > 0) {
	    		// Check to make sure there isn't a deactivate set
	    		if ($scope.states[i].deactivate_override > 0){
	    			$scope.states[i].armedDisplay = "DISARMED";
	    		} else {
	    			$scope.states[i].armedDisplay = "ARMED";
	    			armType = "arm-schedule";
	    		}
	    	} else {
	    		$scope.states[i].armedDisplay = "DISARMED";
	    	}

	    	if (armType){
	    		$scope.states[i].armed = armType;
	    	}
		}
    }

});

app.controller('LoginController', function($scope, $http, AuthenticationService){

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

app.controller('ScheduleController', function($scope, $http, $location, $filter, $mdDialog, TransferService, AuthenticationService, NavigationService){

	init();

	function init() {
	  	$scope.loadSchedules = loadSchedules;
	  	//$scope.logout = logout;
	  	//$scope.routeNav = routeNav;
	    $scope.deleteSchedule = deleteSchedule;
	    $scope.toggleModal = toggleModal;
	    $scope.saveSchedule = saveSchedule;
	    $scope.createSchedule = createSchedule;
	    $scope.setCreate = setCreate;
	    $scope.showModifyDialog = showModifyDialog;
	    $scope.confirmRemove = confirmRemove;
	    
	    //Load the schedules for the first execution
		$scope.loadSchedules();
		setLoginStatus();
	}

	function setLoginStatus () {
		NavigationService.setLoginStatus(true);
		NavigationService.setCurrentTab(1);
	}

	// function logout(){
	// 	AuthenticationService.logout($scope.authtoken);
	// }

	function loadSchedules(){
		//Get the latest schedules and load them into scope
		$http.get(url + "/schedules")
			.success(function(response){
				$scope.schedules = response;
			});
	}

	// function routeNav(type){
	// 	var route = "";

	// 	if (type == 'state') {
	// 		route = "/state";
	// 	} else if (type == 'schedules') {
	// 		route = "/schedules";
	// 	} else if (type == 'users') {
	// 		route = "/users";
	// 	} else if (type == "configuration") {
	// 		route = "/configuration";
	// 	}

	// 	if (route != "") {
	// 		$location.path(route);	
	// 	}
	// }

	function deleteSchedule(id){
		var sendURL = "/schedule/delete/" + id;
		$http.get(url + sendURL)
			.success(function (data) {
	    		//Set the scope with the changed values
	    		loadSchedules();
			})
	}

	function toggleModal(schedule, ev){
		TransferService.addItem(angular.copy(schedule));
		showModifyDialog(ev);
	}

	function saveSchedule(schedule){
		
		//Determine type - if create then send to create new
		if (!schedule.id) {
			createSchedule(schedule);
		} else {
			//First create the JSON to be posted
			var submission = { id: schedule.id, start_day: schedule.start_day, 
				start_hour: schedule.start_hour, start_minute: schedule.start_minute, 
				end_day: schedule.end_day, end_hour: schedule.end_hour, 
				end_minute: schedule.end_minute, alert_rule_id: schedule.alert_rule_id, active: schedule.active };

			//Send submission to endpoint
			$http.post(url + "/schedule/update", submission)
				.success(function(response){
					//Redirect to schedule
					loadSchedules();
				});
		}
	}

	function createSchedule(schedule){
		//First create the JSON to be posted
		var submission = { app_module_id: schedule.app_module_id, 
			start_day: schedule.start_day, 
			start_hour: schedule.start_hour, 
			start_minute: schedule.start_minute, 
			end_day: schedule.end_day, 
			end_hour: schedule.end_hour, 
			end_minute: schedule.end_minute, 
			alert_rule_id: schedule.alert_rule_id, 
			active:1 };
		//Send submission to endpoint
		$http.post(url + "/schedule/create", submission)
			.success(function(response){
				//Redirect to schedule
				//$scope.modalShown = !$scope.modalShown;
				loadSchedules();
			});
	}

	function setCreate(ev) {
		TransferService.addItem({});
		showModifyDialog(ev);
	}

	function showModifyDialog(inputEvent) {
		$mdDialog.show({
	      controller: DialogController,
	      templateUrl: 'templates/schedulemodify.html',
	      targetEvent: inputEvent,
	    })
	    .then(function(answer) {
	      saveSchedule(answer);
	    }, function() {
	      //No action
	    });
	}

	function confirmRemove(schedule, ev) {

		// Appending dialog to document.body to cover sidenav in docs app
	    var confirm = $mdDialog.confirm()
	      .title('Confirm Deletion')
	      .content('Are you sure you want to delete this schedule?')
	      .ariaLabel('Confirm Delete')
	      .ok('Delete')
	      .cancel('cancel')
	      .targetEvent(ev);
	    $mdDialog.show(confirm).then(function() {
	      //Delete the schedule
	      deleteSchedule(schedule.id);
	    }, function() {
	      //No action
	    });
	}
	
	function DialogController($scope, $mdDialog, TransferService) {

	  init();

	  function init(){

	  	$scope.targetSchedule = TransferService.getItem();
	  	$scope.hide = hide;
	  	$scope.cancel = cancel;
	  	$scope.answer = answer;

	  	getAppModules();
	  	getAlertRules();
	  	loadDefaultData();
	  }

	  function getAppModules(){
		$http.get(url + "/state")
			.success(function(response){
			$scope.modules = response;
		});
	  }

	  function getAlertRules(){
			$http.get(url + "/rules")
				.success(function(response){
				$scope.alertRules = response;
			});
	  }

	  function loadDefaultData(){
			var weekDays = [
	        	{ id: 0, dayOfWeek: 'Sunday' },{ id: 1, dayOfWeek: 'Monday' },{ id: 2, dayOfWeek: 'Tuesday' },{ id: 3, dayOfWeek: 'Wednesday' },
	        	{ id: 4, dayOfWeek: 'Thursday' },{ id: 5, dayOfWeek: 'Friday' },{ id: 6, dayOfWeek: 'Saturday' }
	      	];
	      	var hoursInDay = [
	      		{ id: 0, hourInDay: '12:00 AM' },{ id: 1, hourInDay: '1:00 AM' },{ id: 2, hourInDay: '2:00 AM' },{ id: 3, hourInDay: '3:00 AM' },
	        	{ id: 4, hourInDay: '4:00 AM' },{ id: 5, hourInDay: '5:00 AM' },{ id: 6, hourInDay: '6:00 AM' },{ id: 7, hourInDay: '7:00 AM' },
	        	{ id: 8, hourInDay: '8:00 AM' },{ id: 9, hourInDay: '9:00 AM' },{ id: 10, hourInDay: '10:00 AM' },{ id: 11, hourInDay: '11:00 AM' },
	        	{ id: 12, hourInDay: '12:00 PM' },{ id: 13, hourInDay: '1:00 PM' },{ id: 14, hourInDay: '2:00 PM' },{ id: 15, hourInDay: '3:00 PM' },
	        	{ id: 16, hourInDay: '4:00 PM' },{ id: 17, hourInDay: '5:00 PM' },{ id: 18, hourInDay: '6:00 PM' },{ id: 19, hourInDay: '7:00 PM' },
	        	{ id: 20, hourInDay: '8:00 PM' },{ id: 21, hourInDay: '9:00 PM' },{ id: 22, hourInDay: '10:00 PM' },{ id: 23, hourInDay: '11:00 PM' }
	      	];
	      	var minutesInHour = [
	      		{ id: 0, minuteInHour: '00' },{ id: 5, minuteInHour: '05' },{ id: 10, minuteInHour: '10' },{ id: 15, minuteInHour: '15' },
	        	{ id: 20, minuteInHour: '20' },{ id: 25, minuteInHour: '25' },{ id: 30, minuteInHour: '30' },{ id: 35, minuteInHour: '35' },
	        	{ id: 40, minuteInHour: '40' },{ id: 45, minuteInHour: '45' },{ id: 50, minuteInHour: '50' },{ id: 55, minuteInHour: '55' }
	      	];
	      	$scope.daysOfWeek = weekDays;
	      	$scope.hoursInDay = hoursInDay;
	      	$scope.minutesInHour = minutesInHour;
	  }

	  function hide(){
	  	$mdDialog.hide();
	  }

	  function cancel(){
	  	$mdDialog.cancel();
	  }

	  function answer(answer){
	  	$mdDialog.hide(answer);
	  }

	}

});

app.controller('UserController', function($scope, $http, $location, $mdDialog, AuthenticationService, NavigationService, TransferService){
	
	var displayPass = "0000000000"
	init();

	function init(){
		$scope.loadUsers = loadUsers;
		//$scope.routeNav = routeNav;
		$scope.toggleModal = toggleModal;
		//$scope.logout = logout;
		$scope.setCreate = setCreate;
		$scope.saveUser = saveUser;
		$scope.createUser = createUser;
		$scope.deleteUser = deleteUser;
		$scope.showModifyDialog = showModifyDialog;
		$scope.confirmRemove = confirmRemove;

		setLoginStatus();
		loadUsers();
	}

	function processUserData(data){
		
		//Loop through the users and set display passwords
		for (var i = 0; i < data.length; i++) {
		    data[i].firstPassword = displayPass;
		    data[i].secondPassword = displayPass;
		}
		return data;
	}

	function setLoginStatus () {
		NavigationService.setLoginStatus(true);
		NavigationService.setCurrentTab(2);
	}

	// function logout(){
	// 	AuthenticationService.logout($scope.authtoken);
	// }

	function loadUsers(){
    	$http.get(url + "/users")
	    .success(function(response) {
	    	$scope.users = processUserData(response);
	    });
    }

 //    function routeNav(type){
	// 	var route = "";

	// 	if (type == 'state') {
	// 		route = "/state";
	// 	} else if (type == 'schedules') {
	// 		route = "/schedules";
	// 	} else if (type == 'users') {
	// 		route = "/users";
	// 	} else if (type == "configuration") {
	// 		route = "/configuration";
	// 	}

	// 	if (route != "") {
	// 		$location.path(route);	
	// 	}
		
	// }

	function toggleModal(user, ev){
		TransferService.addItem(angular.copy(user));
		showModifyDialog(ev);
	}

	function setCreate(ev) {
		TransferService.addItem({});
		showModifyDialog(ev);
	}

	function createUser(user){
		var outPassword;
		var outSMSNumber;
		var outSendEmail;
		var outSendSMS;
		var outActive;

		outPassword = user.firstPassword;
		if (user.sms_number){
			outSMSNumber = user.sms_number;
		} else {
			outSMSNumber = "";
		}
		if (user.send_email){
			outSendEmail = user.send_email;
		} else {
			outSendEmail = false;
		}
		if (user.send_smsl){
			outSendSMS = user.send_sms;
		} else {
			outSendSMS = false;
		}
		if (user.active){
			outActive = user.active;
		} else {
			outActive = true;
		}

		//First create the JSON to be posted
		var submission = { id:0, 
			user_name: user.user_name, 
			password: outPassword, 
			sms_number: outSMSNumber, 
			send_email: outSendEmail, 
			send_sms: outSendSMS, 
			active: outActive };
		//Send submission to endpoint
		$http.post(url + "/user/create", submission)
			.success(function(response){
				//reload users
				loadUsers();
			});
	}

	function saveUser(user){
		//Determine type - if create then send to create new
		if (!user.id) {
			createUser(user);
		} else {
			var submission;
			//check if password changed
			if (user.firstPassword != displayPass){
				//First create the JSON to be posted
				submission = { id: user.id, 
					password: user.firstPassword, 
					sms_number: user.sms_number, 
					send_email: user.send_email, 
					send_sms: user.send_sms, 
					active: user.active };
			} else {
				submission = { id: user.id,  
					sms_number: user.sms_number, 
					send_email: user.send_email, 
					send_sms: user.send_sms, 
					active: user.active };
			}

			//Send submission to endpoint
			$http.post(url + "/user/update", submission)
				.success(function(response){
					//Redirect to schedule
					loadUsers();
				});
		}
	}

	function deleteUser(id) {
		var submission = "/user/delete/" + id;
		//Send submission to endpoint
		$http.post(url + submission)
			.success(function(response){
				//reload users
				loadUsers();
			});
	}

	function showModifyDialog(inputEvent) {
		$mdDialog.show({
	      controller: DialogUserController,
	      templateUrl: 'templates/usermodify.html',
	      targetEvent: inputEvent,
	    })
	    .then(function(answer) {
	      saveUser(answer);
	    }, function() {
	      //No action
	    });
	}

	function confirmRemove(user, ev) {

		// Appending dialog to document.body to cover sidenav in docs app
	    var confirm = $mdDialog.confirm()
	      .title('Confirm Deletion')
	      .content('Are you sure you want to delete this user?')
	      .ariaLabel('Delete User')
	      .ok('Delete')
	      .cancel('cancel')
	      .targetEvent(ev);
	    $mdDialog.show(confirm).then(function() {
	      //Delete the schedule
	      deleteUser(user.id);
	    }, function() {
	      //No action
	    });
	}

	function DialogUserController($scope, $mdDialog, TransferService) {

	  init();

	  function init(){

	  	$scope.targetUser = TransferService.getItem();
	  	$scope.hide = hide;
	  	$scope.cancel = cancel;
	  	$scope.answer = answer;
	  	$scope.displayMessage = "";
	  	$scope.showMessage = false;

	  	//Determine status of user
	  	if (!$scope.targetUser.id){
	  		$scope.modifyState = "new";
	  	} else {
	  		$scope.modifyState = "update";
	  	}
	  }

	  function validateInput(input){
	  	var validated = false;
	  	if (input.firstPassword == input.secondPassword){
	  		validated = true;
	  		$scope.showMessage = false;
	  	} else {
	  		$scope.displayMessage = "input passwords must match";
	  		$scope.showMessage = true;
	  	}
	  	return validated;
	  }

	  function hide(){
	  	$mdDialog.hide();
	  }

	  function cancel(){
	  	$mdDialog.cancel();
	  }

	  function answer(answer){
	  	if (validateInput(answer)){
	  		$mdDialog.hide(answer);
	  	}
	  }

	}

});

app.controller('ConfigurationController', function($scope, $http, $location, AuthenticationService, NavigationService){
	
	init();

	function init(){
		//$scope.routeNav = routeNav;
		$scope.toggleModal = toggleModal;
		//$scope.logout = logout;
		$scope.loadState = loadState;
		$scope.resetViewState = resetViewState;
		$scope.setUpdate = setUpdate;
		$scope.updateAlerts = updateAlerts;
		$scope.loadRules = loadRules;

		setLoginStatus();
		loadRules();
		loadState();
	}

	function setLoginStatus () {
		NavigationService.setLoginStatus(true);
		NavigationService.setCurrentTab(3);
	}

	// function logout(){
	// 	AuthenticationService.logout($scope.authtoken);
	// }


 //    function routeNav(type){
	// 	var route = "";

	// 	if (type == 'state') {
	// 		route = "/state";
	// 	} else if (type == 'schedules') {
	// 		route = "/schedules";
	// 	} else if (type == 'users') {
	// 		route = "/users";
	// 	} else if (type == "configuration") {
	// 		route = "/configuration";
	// 	}

	// 	if (route != "") {
	// 		$location.path(route);	
	// 	}
		
	// }

	function toggleModal(user, type){
		
		if (type === "edit") {
			$scope.modalType = "edit";
		} else if (type === "delete") {
			$scope.modalType = "delete";
		} 

		$scope.targetUser = user;
		$scope.modalShown = !$scope.modalShown;
	}

	function loadState(){
    	$http.get(url + "/state")
	    .success(function(response) {
	    	$scope.state = response;
	    	$scope.viewType = "view";
	    });
    }

    function resetViewState() {
    	$scope.viewType = "view";
    	$scope.targetState = {};
    }

    function setUpdate(id) {
    	$scope.targetState = $scope.state[id];
    	$scope.viewType = "update";
    }

    function updateAlerts() {
    	//First create the JSON to be posted
		var submission = { id:$scope.targetState.id, override_alert_rule: $scope.targetState.override_alert_rule, general_alert_rule: $scope.targetState.general_alert_rule };
		//Send submission to endpoint
		$http.post(url + "/state/update/alerts", submission)
			.success(function(response){
				loadState();
				$scope.targetState = {};
				$scope.viewType = "view";
			});
    }

    function loadRules(){
    	$http.get(url + "/rules")
	    .success(function(response) {
	    	$scope.alertRules = response;
	    });
    }


});

app.controller('NavController', function($scope, $http, $location, $cookies, NavigationService, AuthenticationService){
	
	init();

	function init(){
		$scope.routeNav = routeNav;
		$scope.loggedIn = loggedIn;
		$scope.getSelectedIndex = getSelectedIndex;

		setTabNavigation();
		setNavItems();

		//Check to see if login has been completed to not show
		checkLoginStatus();
	}

	function determineDefaultTab(){
		// Check if cookie exists today
		var hasExpired = false;
		var returnTab = 0;

		if ($cookies['navtab']){
			//Check the expire
			if ($cookies['navtabexpire']){
				try {
					var setCookieExpireDate = new Date($cookies['navtabexpire']);

					if (setCookieExpireDate){
						var fourHours = 3600000;
						var currentDate = new Date();
						//var hours = Math.abs(date1 - date2) / 36e5;

						if ((currentDate - setCookieExpireDate) > fourHours) {
							//This means the date has expired - So reset the cookies
							hasExpired = true;
						}
					}
				} catch(err) {
					setTabCookieExpireDate();
				}
			} 
				
			//set tab for navigation
			if (hasExpired){
				resetTabCookie();
				returnTab = 0;
			} else {
				returnTab = $cookies['navtab'];
			}

		} else {
			// Set the cookies
			resetTabCookie();
		}

		return returnTab;
	}

	function setTabNavigation(){
		try {
		    //Get current selected tab
			var startTab = parseInt(determineDefaultTab());
			$scope.selectedIndex = startTab;
		}
		catch(err) {
		    $scope.selectedIndex = 0;
		}
	}

	function resetTabCookie(){
		setTabCookie(0);
		setTabCookieExpireDate();
	}

	function setTabCookie(selected_tab){
		$cookies.navtab = selected_tab;
	}

	function setTabCookieExpireDate(){
		var cookieDate = new Date();
	  	$cookies.navtabexpire = cookieDate;
	}

	function showNavigationCookie(value){
		var cookieDate = new Date();
		$cookies.showNavigation = value;
		$cookies.showNavigationExpire = cookieDate;
	}

	function checkLoginStatus() {
		if (NavigationService.getLoginStatus() == false) {
			//Set the scope variable to not show the navigation
			$scope.showNavigation = false;
		}
	}

	function setNavItems () {
		//$scope.navItems = [
		//    { type: 'state', route: '/state' },
		//    { type: 'schedules', route: '/schedules' },
		//    { type: 'users', route: '/users' },
		//    { type: 'configuration', route: '/configuration' },
		//    { type: 'logout', route: '/logout' }
		//  ];

		// var navTabs = [
		//     { index: 0, type: 'state', route: '/state' },
		//     { index: 1, type: 'schedules', route: '/schedules' },
		//     { index: 2, type: 'users', route: '/users' },
		//     { index: 3, type: 'configuration', route: '/configuration' },
		//     { index: 4, type: 'logout', route: '/logout' }
		//   ];

		$scope.navItems = NavigationService.getNavTabs(); 
	}

	function logout(){
		showNavigationCookie(false);
		resetTabCookie();
		AuthenticationService.logout($scope.authtoken);
	}

    function routeNav(type){
		var route = "";

		if (type == 'state') {
			route = "/state";
			setTabCookie(0);
		} else if (type == 'schedules') {
			route = "/schedules";
			setTabCookie(1);
		} else if (type == 'users') {
			route = "/users";
			setTabCookie(2);
		} else if (type == "configuration") {
			route = "/configuration";
			setTabCookie(3);
		} else if (type == "logout") {
			logout();
		}

		if (route != "") {
			$location.path(route);	
		}
		
	}

	function loggedIn() {
		// if (NavigationService.getLoginStatus()) {
		// 	return true;
		// } else {
		// 	return false;
		// }
		var hasExpired = false;
		//Check to see if cookie is set to show the navigation
		if ($cookies['showNavigation']) {
			// Now check to see if the cookie has expired
			try {
				var setCookieExpireDate = new Date($cookies['showNavigationExpire']);

				if (setCookieExpireDate){
					var fourHours = 3600000;
					var currentDate = new Date();

					if ((currentDate - setCookieExpireDate) > fourHours) {
						//This means the date has expired - So reset the cookies
						hasExpired = true;
					}
				}
			} catch(err) {
					//Nothing
			}

			if (hasExpired) {
				//clear cookies
				$cookies['showNavigation'] = false;
				$cookies['showNavigationExpire'] = undefined;
				return false;
			} else {
				//Check show navigation cookie
				var cookieValue = $cookies['showNavigation'];
				if (cookieValue === 'true'){
					return true;
				} else {
					return false;
				}
			}

		} else {
			return false;
		}

	}

	function getSelectedIndex() {
		return NavigationService.getCurrentTab();
	}

});

















