const fs = require('fs');
const asynclock = require('async-lock');

function get(o, s) {
	if (!s.length) return o;
	s = s.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
	s = s.replace(/^\./, '');	   // strip a leading dot
	
	var a = s.split('.');
	for (var i = 0, n = a.length; i < n; ++i) {
		var k = a[i];
		if (k in o) {
			o = o[k];
		} else {
			return;
		}
	}
	return o;
}

function set(obj, path, value) {
	let schema = obj;
	let pList = path.split('.');
	let len = pList.length;
	let elem;
	for(let i = 0; i < len-1; i++) {
		elem = pList[i];
		if( !schema[elem] ) schema[elem] = {}
		schema = schema[elem];
	}

	schema[pList[len-1]] = value;
}

function remove(obj, path) {
	let schema = obj;
	let pList = path.split('.');
	let len = pList.length;
	let elem;
	for(let i = 0; i < len-1; i++) {
		elem = pList[i];
		if( !schema[elem] ) schema[elem] = {}
		schema = schema[elem];
	}

	if (len == 1) delete obj[path];
	else delete schema[pList[len-1]];
}

module.exports = function (location) {
	this.location = location;

	this.create = function() {
		if (!fs.existsSync(this.location)) {
			fs.writeFileSync(this.location, "{}");
		}
	}

	this.open = function() {
		if (fs.existsSync(this.location+"-LOCK")) {
			//throw "Remove lock before attempting to access path: " + this.location+"-LOCK";
		}
		if (!fs.existsSync(this.location)) {
			throw "Path not found: " + this.location;
		}
		fs.closeSync(fs.openSync(this.location+"-LOCK", 'w'));
		this.isOpen = true;
		this.lock = new asynclock();
	}

	this.close = function() {
		fs.unlinkSync(this.location+"-LOCK");
		this.isOpen = false;
	}

	this.read = function() {
		this.content = JSON.parse(fs.readFileSync(this.location));
	}

	this.write = function() {
		fs.writeFileSync(this.location, JSON.stringify(this.content));
	}

	this.get = function(path) {
		let that = this;
		this.lock.acquire("db_change", function() {});
		that.read();
		return get(that.content, path);
	}

	this.set = function(path, value) {
		let that = this;
		this.lock.acquire("db_change", function() {
			that.read();
			//console.log("Before: " + JSON.stringify(that.content));
			set(that.content, path, value);
			//console.log("Writing: " + that.content);
			that.write();
		});
	}

	this.remove = function(path) {
		let that = this;
		this.lock.acquire("db_change", function() {
			that.read();
			remove(that.content, path);
			that.write();
		});
	}
}
