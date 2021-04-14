import * as essentials from "./essentials.js"
import * as constants from "./constants.js"
const DEBUG      = true;//process.cwd().includes("test");
const PORT_HTTPS = DEBUG? 3002 : 443;
const PORT_HTTP  = DEBUG? 3000 : 80;
const API_PATH = "";
var httpServer, httpsServer;

console.log("Launching in debug setting: " + DEBUG);

var db = new (require('./minidb.js'))(constants.DB_PATH);
db.open();

httpsServer = https.createServer(httpsOptions, app);
httpsServer.listen(PORT_HTTPS, function(err) {
	if (err) return;
	console.log('HTTPS started, Server\'s UID is now ' + process.getuid());
});

if (DEBUG) {
	httpServer = http.createServer(app);
	httpServer.listen(PORT_HTTP, function(err) {
		if (err) return;
		console.log('HTTP started, Server\'s UID is now ' + process.getuid());
	});
} else {
	http.createServer(function (req, res) {
		res.writeHead(301, { "Location": "https://" + req.headers['host'] + req.url });
		
	}).listen(PORT_HTTP, function(err) {
		if (err) return;
		console.log('HTTP->HTTPS started, Server\'s UID is now ' + process.getuid());
	});
}

/*app.use(bodyParser.json({
    verify: function(req, res, buf, encoding) {

        // sha1 content
        var hash = crypto.createHash('sha1');
        hash.update(buf);
        req.hasha = hash.digest('hex');
        console.log("hash", req.hasha);

        // get rawBody        
        req.rawBody = buf.toString();
        console.log("rawBody", req.rawBody);

    }
}));*/
app.use(
  bodyParser.urlencoded({
    extended: true
  })
)
app.use('/', express.static(__dirname + '/public'));


function end_request(req, res, value) {
	if (typeof value === "string") res.write(value);
	else if (typeof value === "number") res.sendStatus(value);
	res.end();
	console.log(req.connection.remoteAddress + ": " + req.originalUrl.split("?")[0] + " ended with \"" + value + "\"");
}

app.get(API_PATH+'/create-license', function(req, res) {
	let req_ip = req.connection.remoteAddress;
	let req_code = req.query.code;
	let req_auth = req.query.auth;

	if (typeof req_code !== 'string' || !(/^[a-zA-Z0-9]+$/.test(req_code)) || req_code.length != constants.LENGTH_CODE || typeof req_auth !== 'string' || !(/^[a-zA-Z0-9]+$/.test(req_auth))) {
		end_request(req, res, constants.RES_BAD_SYNTAX);
		return;
	} else if (!valid_password(req)) {
		end_request(req, res, constants.RES_FORBIDDEN);
		return;
	}

	if (db.get(req_code)) {
		end_request(req, res, constants.RES_ALREADY_EXISTS);
		return;
	}

	db.set(req_code, {'users': {}, 'max_count': 1000});

	end_request(req, res, 201);
	
});

app.get(API_PATH+'/revoke-license', function(req, res) {
	let req_ip = req.connection.remoteAddress;
	let req_code = req.query.code;
	let req_auth = req.query.auth;

	if (typeof req_code !== 'string' || !(/^[a-zA-Z0-9]+$/.test(req_code)) || req_code.length != constants.LENGTH_CODE || typeof req_auth !== 'string' || !(/^[a-zA-Z0-9]+$/.test(req_auth))) {
		end_request(req, res, constants.RES_BAD_SYNTAX);
		return;
	} else if (!valid_password(req)) {
		end_request(req, res, constants.RES_FORBIDDEN);
		return;
	}

	if (!db.get(req_code)) {
		end_request(req, res, constants.RES_NOT_FOUND);
		return;
	}

	db.remove(req_code);

	end_request(req, res, 200);
	
});

function get_license(req, res) {
	console.log("Called get-license");
	let req_ip = req.connection.remoteAddress;
	let req_code = req.query.code;
	let req_imei = req.query.imei;
	let req_time = Date.now(); //unix time

	// additions for compatibility with legacy
	if (req.originalUrl.split("/").length == 4) {
		req_code = req.originalUrl.split("/")[2];
		req_imei = req.body.activation.device_uid;
	}

	if (typeof req_code !== 'string' || !(/^[a-zA-Z0-9]+$/.test(req_code)) || req_code.length != constants.LENGTH_CODE || typeof req_imei !== 'string' || !(/^[a-zA-Z0-9]+$/.test(req_imei))) {
		end_request(req, res, constants.RES_BAD_SYNTAX);
		return;
	}

	if (!db.get(req_code)) {
		end_request(req, res, constants.RES_FORBIDDEN);
		return;
	}

	let users = db.get(req_code+".users");
	let user = users[req_imei];
	if (!user) {
		if (Object.keys(users).length >= db.get(req_code+".max_count")) {
			end_request(req, res, constants.RES_TOO_MANY);
			return;
		}

		user = {last_login: 0, last_ip: ""};
	}

	user.last_login = req_time;
	user.last_ip = req_ip;

	end_request(req, res, generate_login_response(req_code, req_imei));

	db.set(req_code+".users."+req_imei, user);
}

app.get(API_PATH+'/get-license', function(req, res) {
	get_license(req, res);
});

app.post("/customers/*", function(req, res) {
	get_license(req, res);
});

app.put("/customers/*", function(req, res) {
	get_license(req, res);
});

app.get("*", function(req, res){
	end_request(req, res, constants.RES_NOT_FOUND);
});

process.on("uncaughtException", function (err) {
	console.log("Caught a fatal error:");
	console.log(err);
	console.log("Dumping memory...");
	heapdump.writeSnapshot(constants.LOGS_PATH+"/heap_"+Date.now()+".dump");
	db.close();
});
