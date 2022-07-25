const Pty = require('node-pty');
const fs = require('fs');
const path = require('path');


/* Total.js framework loads environment variables from a .env file into process.env variable automatically. 
   Framework doesn't overwrite values in process.env, only extends the variable.
    https://docs.totaljs.com/total4/7bf9f001fx51c/
*/

/** 
 * Relative path check
 * @param {string} p - path
 * @returns {boolean} true if relative path, false otherwise
 */
const isRelative = (p) => { return (!p.startsWith('/') && !p.match(/^[A-Za-z]:/g)); };

// set app location & python exe

// default location of app; '/app' on heroku
let appFolder = process.env.APP_PATH ? process.env.APP_PATH : '/app';
let pythonPath = '';        // path to python exe
let pythonExe = process.env.PYTHON_EXE ? process.env.PYTHON_EXE : 'python3';  // python exe
if (process.env.NODE_ENV === "development") {

    pythonPath = process.env.PYTHON_PATH ? process.env.PYTHON_PATH : '';
    if (isRelative(pythonPath)) {
        // convert relative path to absolute
        pythonPath = path.join(process.cwd(), pythonPath);
    }

    if (isRelative(appFolder)) {
        // convert relative path to absolute
        appFolder = path.join(process.cwd(), appFolder);
    }
}
pythonExe = path.join(pythonPath, pythonExe);

/**
 * Setup Total.js framework routing.
 */
exports.install = function () {

    ROUTE('/');
    WEBSOCKET('/', socket, ['raw']);
};

function socket() {

    this.encodedecode = false;
    this.autodestroy();

    this.on('open', function (client) {

        // Spawn terminal
        client.tty = Pty.spawn(pythonExe, ['run.py'], {
            name: 'xterm-color',
            cols: 80,
            rows: 24,
            cwd: process.env.PWD,
            env: process.env
        });

        client.tty.on('exit', function (code, signal) {
            client.tty = null;
            client.close();
            console.log("Process killed");
        });

        client.tty.on('data', function (data) {
            client.send(data);
        });

    });

    this.on('close', function (client) {
        if (client.tty) {
            client.tty.kill(9);
            client.tty = null;
            console.log("Process killed and terminal unloaded");
        }
    });

    this.on('message', function (client, msg) {
        client.tty && client.tty.write(msg);
    });
}

for (entry of [
    [process.env.CREDS, 'creds.json'],
    [process.env.RAPID_CREDS, 'rapid_creds.json'],
]) {
    if (entry[0]) {
        console.log("Creating " + entry[1] + " file.");
        fs.writeFile(entry[1], entry[0], 'utf8', function (err) {
            if (err) {
                console.log('Error writing file: ', err);
                socket.emit("console_output", "Error saving credentials: " + err);
            }
        });
    }
}