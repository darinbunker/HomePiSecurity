var app = angular.module('app', ['ngRoute', 'ngMaterial', 'ngCookies']).config(function($locationProvider, $routeProvider, $filterProvider, $provide, $httpProvider, $cookiesProvider, $windowProvider){

    $routeProvider.when('/state', {
      templateUrl: 'templates/state.html'
    });
    $routeProvider.when('/schedules', {
      templateUrl: 'templates/schedules.html'
    });
    $routeProvider.when('/users', {
      templateUrl: 'templates/users.html'
    });
    $routeProvider.when('/configuration', {
      templateUrl: 'templates/configuration.html'
    });
    $routeProvider.otherwise({ redirectTo : '/state' });

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

    var $window = $windowProvider.$get();
    var $cookies = $cookiesProvider.$get();

    //Set Http Configurations and Common Error handling
    $httpProvider.defaults.headers.common['Authorization'] = $cookies['hssid'];

    $provide.factory('BaseHttpInterceptor', function ($q) {
      return {
        // On response failture
        responseError: function (rejection) {
          // Return the promise rejection.
          if (rejection.data.exception == 'javax.servlet.ServletException' && rejection.data.message == 'Missing or invalid Authorization header.'){
            //Clear cookies and logout
            delete $cookies['hssid'];
            $window.location.href = 'login.html';
          } else if (rejection.data.exception == 'io.jsonwebtoken.ExpiredJwtException') {
            delete $cookies['hssid'];
            $window.location.href = 'login.html';
          }
          return $q.reject(rejection);
        }
      };
    });

    $httpProvider.interceptors.push('BaseHttpInterceptor');

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

app.service('SessionService', function(){
  var logout = function($cookies, $window){
    //Invalidate the authentication token
    delete $cookies['hssid'];
    //Redirect to login
    $window.location.href = 'login.html';
  }

  return {
    logout: logout
  };
});

app.controller('BaseController', function($scope, $mdBottomSheet, $mdSidenav, $mdDialog, $location, $http, SessionService, $cookies, $window){
  init();

  function init() {
    $scope.toggleSearch = toggleSearch;
    $scope.toggleSidenav = toggleSidenav;
    $scope.loadBaseState = loadBaseState;
    $scope.navigateAction = navigateAction;
    $scope.logout = logout;

    //Load default data and users
    loadLoggedInUser();
    setDefaultData();

    //load first template
    loadBaseState();
  }

  function loadLoggedInUser(){
    //First load the data from the service
    $http({
        method: 'GET',
        url: url + '/api/user'
      }).then(function(response){
        $scope.loggedInUser = response.data;
      });
  }

  function logout(){
    SessionService.logout($cookies, $window);
  }

  function navigateAction(route){
    $scope.data.selectedIndex = 0;
    $location.path('/'+route);
  }

  function loadBaseState(){
    $location.path('/state');
  }

  function toggleSearch(element){
    $scope.showSearch = !$scope.showSearch;
  }

  function toggleSidenav(menuId){
    $mdSidenav(menuId).toggle();
  }

  function setDefaultData(){
    // Set default state:
    $scope.alert = '';

    $scope.showTabs = true;

    // Menu items
    $scope.menu = [
      {
        route : 'state',
        title: 'Status',
        icon: 'communication:ic_message_24px' 
      },
      {
        route : 'schedules',
        title: 'Schedules',
        icon: 'action:ic_dashboard_24px'
      },
      {
        route : 'users',
        title: 'Users',
        icon: 'social:ic_group_24px'
      },
      {
        route : 'configuration',
        title: 'Settings',
        icon: 'action:ic_settings_24px'
      }
    ];
  }

});

app.controller('StateController', function($scope, $http, $location, $cookies){
  init();

  function init() {
      $scope.setArmed = setArmed;
      $scope.loadState = loadState;
      $scope.loadBackground = loadBackground;

      $scope.$parent.showTabs = false;
      // if(!$scope.$$phase) {
      //   $scope.$parent.$apply();
      // }

      loadState();
  }

    function setArmed(state, type){
      //get the module ID and state
      //types:
      // - 0: Disarm, 1: Arm and Hold, 2: Arm Temporary
      var putURL = "";
      // Determine the endpoint
      if (type == 0){
        // need to determine if disable is required
        if (state.active_override > 0) {
          putURL += "/api/state/override/" + state.id + "/0"; 
        } else if (state.active_schedule > 0) {
          putURL += "/api/state/deactivate/" + state.id + "/1";
        }
      } else if (type == 1) {
        putURL += "/api/state/override/" + state.id + "/1";
      } else if (type == 2) {
        putURL += "/api/state/override/" + state.id + "/2";
      }

      $http({
        method: 'PUT',
        url: url + putURL
      }).then(function(response){
        $scope.loadState();
      });

    }

    function loadState(){
      // Get current state from api
      $http({
        method: 'GET',
        url: url + '/api/state'
      }).then(function(response){
        $scope.states = response.data;
        //Load the current state of the system
        determineArmedState();
      });

    }

    function loadBackground(){
      $scope.showBackground = 1;
    }

    function determineArmedState(){
      //Check the state object to determine the armed state - Loop through the state objects

      for (var i = 0; i < $scope.states.length; i++) {
        var armType = "";
          // - First check if the active_override is set
          $scope.states[i].armed = "not-armed";
          if ($scope.states[i].active_override == 1){
            $scope.states[i].armedDisplay = "ARMED & HOLD";
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

app.controller('ScheduleController', function($scope, $http, $location, $filter, $mdDialog, TransferService){

  init();

  function init() {
    $scope.loadSchedules = loadSchedules;
    $scope.deleteSchedule = deleteSchedule;
    $scope.saveSchedule = saveSchedule;
    $scope.createSchedule = createSchedule;
    $scope.confirmRemove = confirmRemove;
    $scope.configureUpdate = configureUpdate;
    $scope.getAppModules = getAppModules;
    $scope.getAlertRules = getAlertRules;
    $scope.cancel = cancel;
    $scope.resetSchedule = resetSchedule;
    $scope.addNew = addNew;

    $scope.$parent.showTabs = true;

      
    //Load the schedules and default data for the first execution
    loadSchedules();
    loadDefaultData();
  }

  function addNew(){
    //Clear out the target schedule
      if (!angular.isUndefined($scope.targetSchedule)){
        delete $scope.targetSchedule
      }
      //Change the tab to the update tab
      $scope.$parent.data.selectedIndex = 1;
  }

  function configureUpdate(schedule){
    //First load schedule into Target Schedule
    $scope.targetSchedule = angular.copy(schedule);
    //Change the tab to the update tab
    $scope.$parent.data.selectedIndex = 1;
  }

  function loadSchedules(){
    //Get the latest schedules and load them into scope
    $http({
        method: 'GET',
        url: url + '/api/schedules'
      }).then(function(response){
        $scope.schedules = response.data;
      });
  }

  function deleteSchedule(id){
    var sendURL = "/api/schedule/delete/" + id;
    $http({
        method: 'GET',
        url: url + sendURL
      }).then(function(response){
        loadSchedules();
        resetSchedule();
      });
  }

  function resetSchedule(){
    //Clear out the target schedule
      if (!angular.isUndefined($scope.targetSchedule)){
        delete $scope.targetSchedule
      }
      //Change the tab to the update tab
      $scope.$parent.data.selectedIndex = 0;
  }

  function saveSchedule(schedule){
    
    //Determine type - if create then send to create new
    if (!schedule.id) {
      createSchedule(schedule);
    } else {
      //First create the JSON to be posted
      var submission = { id: schedule.id, schedule_name: "", start_day: schedule.start_day, 
        start_hour: schedule.start_hour, start_minute: schedule.start_minute, 
        end_day: schedule.end_day, end_hour: schedule.end_hour, 
        end_minute: schedule.end_minute, alert_rule_id: schedule.alert_rule_id, active: schedule.active };

      //Send submission to endpoint
      $http({
          method: 'POST',
          url: url + '/api/schedule/update',
          data: submission
        }).then(function(response){
          loadSchedules();
          resetSchedule();
        });
    }
  }

  function createSchedule(schedule){
    //First create the JSON to be posted
    var submission = { app_module_id: schedule.app_module_id, 
      schedule_name: "",
      start_day: schedule.start_day, 
      start_hour: schedule.start_hour, 
      start_minute: schedule.start_minute, 
      end_day: schedule.end_day, 
      end_hour: schedule.end_hour, 
      end_minute: schedule.end_minute, 
      alert_rule_id: schedule.alert_rule_id, 
      active:1 };
    //Send submission to endpoint
    $http({
          method: 'POST',
          url: url + '/api/schedule/create',
          data: submission
        }).then(function(response){
          loadSchedules();
          resetSchedule();
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

  function getAppModules(){
      $http({
        method: 'GET',
        url: url + "/api/state"
      }).then(function(response){
        $scope.modules = response.data;
      });
    }

    function getAlertRules(){
      $http({
        method: 'GET',
        url: url + "/api/rules"
      }).then(function(response){
        $scope.alertRules = response.data;
      });
    }

    function loadDefaultData(){

      // Load data from db
      getAppModules();
      getAlertRules();

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

    function cancel(){
      resetSchedule();
    }

});

app.controller('UserController', function($scope, $http, $location, $mdDialog, TransferService){
  
  var displayPass = "0000000000"
  init();

  function init(){
    $scope.loadUsers = loadUsers;
    $scope.saveUser = saveUser;
    $scope.createUser = createUser;
    $scope.deleteUser = deleteUser;
    $scope.confirmRemove = confirmRemove;
    $scope.configureUpdate = configureUpdate;
    $scope.validateInput = validateInput;
    $scope.cancel = cancel;
    $scope.resetUser = resetUser;
    $scope.addNew = addNew;

    $scope.$parent.showTabs = true;

    loadUsers();
  }

  function addNew(){
    //Clear out the target schedule
      if (!angular.isUndefined($scope.targetUser)){
        delete $scope.targetUser
      }
      //Change the tab to the update tab
      $scope.$parent.data.selectedIndex = 1;
  }

  function resetUser(){
    //Clear out the target user
      if (!angular.isUndefined($scope.targetUser)){
        delete $scope.targetUser
      }
      //Change the tab to the update tab
      $scope.$parent.data.selectedIndex = 0;
  }

  function cancel(){
    resetUser();
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

  function configureUpdate(user){
    //First load schedule into Target Schedule
    $scope.targetUser = angular.copy(user);
    //Change the tab to the update tab
    $scope.$parent.data.selectedIndex = 1;
  }

  function processUserData(data){
    
    //Loop through the users and set display passwords
    for (var i = 0; i < data.length; i++) {
        data[i].firstPassword = displayPass;
        data[i].secondPassword = displayPass;
    }
    return data;
  }

  function loadUsers(){
    $http({
        method: 'GET',
        url: url + "/api/users"
      }).then(function(response){
        $scope.users = processUserData(response.data);
      });
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
      avatar_id: 0,
      send_email: outSendEmail, 
      send_sms: outSendSMS, 
      user_type: 0,
      active: outActive };
    //Send submission to endpoint
    $http({
        method: 'POST',
        url: url + '/api/user/create',
        data: submission
      }).then(function(response){
        loadUsers();
        resetUser();
      });
  }

  function saveUser(user){
    //First, validate input
    if (validateInput(user)){
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
            avatar_id: 0,
            send_email: user.send_email, 
            send_sms: user.send_sms, 
            user_type: 0,
            active: user.active };
        } else {
          submission = { id: user.id,  
            sms_number: user.sms_number, 
            avatar_id: 0,
            send_email: user.send_email, 
            send_sms: user.send_sms, 
            user_type: 0,
            active: user.active };
        }

        //Send submission to endpoint
        $http({
          method: 'POST',
          url: url + '/api/user/update',
          data: submission
        }).then(function(response){
          loadUsers();
          resetUser();
        });
      }
    }
  }

  function deleteUser(id){
    $http({
        method: 'POST',
        url: url + '/api/user/delete/' + id
      }).then(function(response){
        loadUsers();
        resetUser();
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

});

app.controller('ConfigurationController', function($scope, $http, $location){
  
  init();

  function init(){
    $scope.loadState = loadState;
    $scope.updateAlerts = updateAlerts;
    $scope.loadRules = loadRules;

    $scope.$parent.showTabs = false;

    loadRules();
    loadState();
  }

  function loadState(){
    $http({
        method: 'GET',
        url: url + "/api/state"
      }).then(function(response){
        $scope.state = response.data;
        $scope.viewType = "view";
      });
    }

  function loadRules(){
    $http({
      method: 'GET',
      url: url + "/api/rules"
    }).then(function(response){
      $scope.alertRules = response.data;
    });
  }

  function updateAlerts(alert) {
      //First create the JSON to be posted
    var submission = { id:alert.id, override_alert_rule: alert.override_alert_rule, general_alert_rule: alert.general_alert_rule };
    $http({
        method: 'POST',
        url: url + '/api/state/update/alerts',
        data: submission
      }).then(function(response){
        loadState();
      });
  }

    
});

app.config(function($mdThemingProvider) {
  var customBlueMap = 		$mdThemingProvider.extendPalette('light-blue', {
    'contrastDefaultColor': 'light',
    'contrastDarkColors': ['50'],
    '50': 'ffffff'
  });
  $mdThemingProvider.definePalette('customBlue', customBlueMap);
  $mdThemingProvider.theme('default')
    .primaryPalette('customBlue', {
      'default': '500',
      'hue-1': '50'
    })
    .accentPalette('pink');
  $mdThemingProvider.theme('input', 'default')
        .primaryPalette('grey')
});

app.config(function($mdIconProvider) {
    $mdIconProvider
      .iconSet('action', 'images/svg-sprite-action.svg', 24)
      .iconSet('alert', 'images/svg-sprite-alert.svg', 24)
      .iconSet('av', 'images/svg-sprite-av.svg', 24)
      .iconSet('communication', 'images/svg-sprite-communication.svg', 24)
      .iconSet('content', 'images/svg-sprite-content.svg', 24)
      .iconSet('device', 'images/svg-sprite-device.svg', 24)
      .iconSet('editor', 'images/svg-sprite-editor.svg', 24)
      .iconSet('file', 'images/svg-sprite-file.svg', 24)
      .iconSet('hardware', 'images/svg-sprite-hardware.svg', 24)
      .iconSet('image', 'images/svg-sprite-image.svg', 24)
      .iconSet('maps', 'images/svg-sprite-maps.svg', 24)
      .iconSet('navigation', 'images/svg-sprite-navigation.svg', 24)
      .iconSet('notification', 'images/svg-sprite-notification.svg', 24)
      .iconSet('social', 'images/svg-sprite-social.svg', 24)
      .iconSet('toggle', 'images/svg-sprite-toggle.svg', 24)
      .iconSet('avatars', 'images/avatar-icons.svg', 24)
      .defaultIconSet('images/svg-sprite-action.svg', 24);

});









