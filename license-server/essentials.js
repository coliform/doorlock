global.express = require("express");
global.fs = require('fs');
global.app = express();
global.https = require('https');
global.heapdump = require('heapdump');
global.moment = require('moment');
global.crypto = require('crypto');
global.now = moment();
global.bodyParser = require('body-parser');

global.escape_html = function escape_html(text) {
	if (typeof text === 'number') return text;
	if (typeof text !== 'string') return '';
	var escape_html_map = {
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#039;'
	};
	return text.replace(/[&<>"']/g, function(m) { return escape_html_map[m]; });
}

global.intersection = function intersection(array1, array2) {
	return array1.filter(value => -1 !== array2.indexOf(value));
}

global.mysql_escape = function mysql_escape(stringToEscape){
	if (stringToEscape == '') return stringToEscape;

	return stringToEscape
		.replace(/\\/g, "\\\\")
		.replace(/\'/g, "\\\'")
		.replace(/\"/g, "\\\"")
		.replace(/\n/g, "\\\n")
		.replace(/\r/g, "\\\r")
		.replace(/\x00/g, "\\\x00")
		.replace(/\x1a/g, "\\\x1a");
}

global.hex_encode = function(s){
	let hex, i;

	let result = "";
	for (i=0; i<s.length; i++) {
		hex = s.charCodeAt(i).toString(16);
		result += ("000"+hex).slice(-4);
	}

	return result;
};

global.hex_decode = function(s){
	let j;
	let hexes = s.match(/.{1,4}/g) || [];
	let back = "";
	for(j = 0; j<hexes.length; j++) {
		back += String.fromCharCode(parseInt(hexes[j], 16));
	}

	return back;
};

global.make_random = function makeid(len) {
	let result = [];
	for (let i = 0; i < len; i++) {
		result[i] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'.charAt(Math.floor(Math.random() * 62));
	}
	return result.join('');
}

global.getDateTime = function getDateTime() {

	let date = new Date();

	let hour = date.getHours();
	hour = (hour < 10 ? "0" : "") + hour;

	let min  = date.getMinutes();
	min = (min < 10 ? "0" : "") + min;

	let sec  = date.getSeconds();
	sec = (sec < 10 ? "0" : "") + sec;

	let year = date.getFullYear();

	let month = date.getMonth() + 1;
	month = (month < 10 ? "0" : "") + month;

	let day  = date.getDate();
	day = (day < 10 ? "0" : "") + day;

	return year + ":" + month + ":" + day + ", " + hour + ":" + min + ":" + sec;

}

global.valid_password = function valid_password(req) {
	let passwords_raw = global.fs.readFileSync('passwords.txt').toString();
	let passwords = passwords_raw.split("\n").filter(function (el) { return el.trim().length != 0 });
	let from_query = req.query? req.query['auth'] : undefined;
	let from_cookies = (req.headers && req.headers.cookie && req.headers.cookie.split("auth=").length==2)? 
		req.headers.cookie.split("auth=")[1].split(";")[0] : undefined;
	let pass = from_query || from_cookies;
	let pass_matches = passwords.includes(pass);
	return pass_matches;
}

global.generate_login_response = function generate_login_response(code, imei) {
	return "YES";
}

global.httpsOptions = {
	cert: fs.readFileSync('./certs/cert.crt'),
	ca: fs.readFileSync('./certs/ca.crt'),
	key: fs.readFileSync('./certs/private.key')
};

global.http = require('http');

//global.db = require('./minidb.js')(require('./constants.js').DB_PATH);
