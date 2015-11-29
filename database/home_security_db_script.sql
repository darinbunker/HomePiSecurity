/* Raspberry Home Security System - DB Install Script */

/* Create DB */
create database HomeSecuritySystem;

/* Set Database */
use HomeSecuritySystem;

/* Create tables for security system.  */
CREATE TABLE `alert_rules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(30) NOT NULL,
  `send_email` int(11) NOT NULL,
  `send_sms` int(11) NOT NULL,
  `send_siren` int(11) NOT NULL,
  `alert_start` int(11) NOT NULL,
  `alert_end` int(11) NOT NULL,
  `active` int(11) NOT NULL,
  `last_change_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `current_state` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pin_id` int(11) NOT NULL,
  `state` int(11) NOT NULL,
  `last_change_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `security_modules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_module_id` int(11) NOT NULL,
  `module_name` varchar(20) NOT NULL,
  `pin_id` int(11) NOT NULL,
  `message` varchar(150) NOT NULL,
  `active` int(11) NOT NULL,
  `last_change_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `security_schedules` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_module_id` int(11) NOT NULL,
  `start_day` int(11) NOT NULL,
  `start_hour` int(11) NOT NULL,
  `start_minute` int(11) NOT NULL,
  `end_day` int(11) NOT NULL,
  `end_hour` int(11) NOT NULL,
  `end_minute` int(11) NOT NULL,
  `alert_rule_id` int(11) NOT NULL,
  `active` int(11) NOT NULL,
  `deleted` int(11) NOT NULL,
  `create_date` datetime NOT NULL,
  `last_change_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `system_state` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_module` varchar(30) NOT NULL,
  `active` int(11) NOT NULL,
  `active_override` int(11) NOT NULL,
  `override_alert_rule` int(11) NOT NULL,
  `general_alert_rule` int(11) NOT NULL,
  `active_schedule` int(11) NOT NULL,
  `deactivate_override` int(11) NOT NULL,
  `last_change_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(100) NOT NULL,
  `password` char(255) NOT NULL,
  `sms_number` varchar(30) NOT NULL,
  `active` int(11) NOT NULL,
  `send_email` int(11) NOT NULL,
  `send_sms` int(11) NOT NULL,
  `deleted` int(11) NOT NULL,
  `create_date` datetime NOT NULL,
  `last_change_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

/* Create tables for security system.  */
CREATE TABLE `incident_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_module_id` int(11) NOT NULL,
  `pin_id` int(11) NOT NULL,
  `alert_actions_count` int(11) NOT NULL,
  `exception_event` int(11) NOT NULL,
  `exception_event_type` varchar(30) NOT NULL,
  `exception_event_type_id` int(11) NOT NULL,
  `start_event_date` datetime NOT NULL,
  `end_event_date` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;


/* Insert default data */

insert into system_state (`app_module`,`active`,`active_override`,`override_alert_rule`,`general_alert_rule`,`active_schedule`,`deactivate_override`,`last_change_date`) values ('door_security', 1, 0, 3, 3, 0, 0, now());

insert into users (`user_name`,`password`,`sms_number`,`active`,`send_email`,`send_sms`, `deleted`, `create_date`,`last_change_date`) values ('admin@admin.io', 'oMK+aYh5Hp/KdIWISbljvA2Oz68VUwsCKl/X5HUhSto=$L+kxRounHxTKKn4woxh/vQ8xNBtwHq5tgYqfYdhfsYg=', '+8015551234', 1, 1, 0, 0, now(), now());

insert into security_schedules (`app_module_id`,`start_day`,`start_hour`,`start_minute`,`end_day`,`end_hour`,`end_minute`,`alert_rule_id`,`active`, `deleted`, `create_date`,`last_change_date`) value (1, 0, 23, 0, 2, 6, 0, 1, 1, 0, now(), now());
insert into security_schedules (`app_module_id`,`start_day`,`start_hour`,`start_minute`,`end_day`,`end_hour`,`end_minute`,`alert_rule_id`,`active`, `deleted`,`create_date`,`last_change_date`) value (1, 1, 23, 0, 3, 6, 0, 1, 1, 0, now(), now());
insert into security_schedules (`app_module_id`,`start_day`,`start_hour`,`start_minute`,`end_day`,`end_hour`,`end_minute`,`alert_rule_id`,`active`, `deleted`,`create_date`,`last_change_date`) value (1, 2, 23, 0, 4, 6, 0, 1, 1, 0, now(), now());
insert into security_schedules (`app_module_id`,`start_day`,`start_hour`,`start_minute`,`end_day`,`end_hour`,`end_minute`,`alert_rule_id`,`active`, `deleted`,`create_date`,`last_change_date`) value (1, 3, 23, 0, 5, 6, 0, 1, 1, 0, now(), now());
insert into security_schedules (`app_module_id`,`start_day`,`start_hour`,`start_minute`,`end_day`,`end_hour`,`end_minute`,`alert_rule_id`,`active`, `deleted`,`create_date`,`last_change_date`) value (1, 4, 23, 0, 6, 6, 0, 1, 1, 0, now(), now());
insert into security_schedules (`app_module_id`,`start_day`,`start_hour`,`start_minute`,`end_day`,`end_hour`,`end_minute`,`alert_rule_id`,`active`, `deleted`,`create_date`,`last_change_date`) value (1, 5, 23, 0, 7, 6, 0, 1, 1, 0, now(), now());
insert into security_schedules (`app_module_id`,`start_day`,`start_hour`,`start_minute`,`end_day`,`end_hour`,`end_minute`,`alert_rule_id`,`active`, `deleted`,`create_date`,`last_change_date`) value (1, 6, 23, 0, 1, 6, 0, 1, 1, 0, now(), now());

insert into alert_rules (`rule_name`,`send_email`,`send_sms`,`send_siren`,`alert_start`,`alert_end`,`active`,`last_change_date`) values ('Full Send Alerts', 1, 1, 1, 1, 1, 1, now());
insert into alert_rules (`rule_name`,`send_email`,`send_sms`,`send_siren`,`alert_start`,`alert_end`,`active`,`last_change_date`) values ('Email and SMS Alerts', 1, 1, 0, 1, 1, 1, now());
insert into alert_rules (`rule_name`,`send_email`,`send_sms`,`send_siren`,`alert_start`,`alert_end`,`active`,`last_change_date`) values ('Email Only Alerts', 1, 0, 0, 1, 1, 1, now());
insert into alert_rules (`rule_name`,`send_email`,`send_sms`,`send_siren`,`alert_start`,`alert_end`,`active`,`last_change_date`) values ('SMS Only Alerts', 0, 1, 0, 1, 1, 1, now());
insert into alert_rules (`rule_name`,`send_email`,`send_sms`,`send_siren`,`alert_start`,`alert_end`,`active`,`last_change_date`) values ('Email and SMS Alerts - No Transition', 1, 1, 0, 0, 0, 1, now());
insert into alert_rules (`rule_name`,`send_email`,`send_sms`,`send_siren`,`alert_start`,`alert_end`,`active`,`last_change_date`) values ('Email Only Alerts - No Transition', 1, 0, 0, 0, 0, 1, now());
insert into alert_rules (`rule_name`,`send_email`,`send_sms`,`send_siren`,`alert_start`,`alert_end`,`active`,`last_change_date`) values ('SMS Only Alerts - No Transition', 0, 1, 0, 0, 0, 1, now());








