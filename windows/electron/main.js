const { app, BrowserWindow, dialog } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

const NODE_PORT = 8545;
const NODE_URL = `http://127.0.0.1:${NODE_PORT}/index.html`;

let mainWindow = null;
let nodeProcess = null;

function findPython() {
  const candidates = ['python', 'python3', 'py'];
  for (const cmd of candidates) {
    try {
      require('child_process').execSync(`${cmd} --version`, { stdio: 'ignore' });
      return cmd;
    } catch (_) {}
  }
  return 'python';
}

function startNode() {
  const python = findPython();
  const nodeDir = path.join(__dirname, '..', '..');

  nodeProcess = spawn(python, ['node.py'], {
    cwd: nodeDir,
    stdio: ['pipe', 'pipe', 'pipe'],
    windowsHide: true,
  });

  nodeProcess.stdout.on('data', (data) => {
    console.log(`[node] ${data}`);
  });

  nodeProcess.stderr.on('data', (data) => {
    console.error(`[node] ${data}`);
  });

  nodeProcess.on('exit', (code) => {
    console.log(`Node exited with code ${code}`);
    nodeProcess = null;
  });
}

function waitForNode(retries = 30) {
  return new Promise((resolve, reject) => {
    const check = (attempt) => {
      http.get(`http://127.0.0.1:${NODE_PORT}/`, (res) => {
        resolve();
      }).on('error', () => {
        if (attempt >= retries) {
          reject(new Error('Node failed to start'));
        } else {
          setTimeout(() => check(attempt + 1), 1000);
        }
      });
    };
    check(0);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    title: 'Globex GBX',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    show: false,
  });

  const loading = new BrowserWindow({
    width: 400,
    height: 200,
    frame: false,
    transparent: true,
    center: true,
    title: 'Starting Globex...',
  });

  loading.loadURL(`data:text/html,
    <html>
    <body style="display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background:#0a0e17;color:#00c853;font-family:sans-serif;">
    <div style="text-align:center;">
      <h2>Globex GBX</h2>
      <p style="color:#6b7280;">Starting node...</p>
      <div style="margin-top:16px;width:200px;height:3px;background:#1f2937;border-radius:2px;overflow:hidden;">
        <div style="width:30%;height:100%;background:#00c853;animation:load 1.5s infinite;">
      </div>
      <style>@keyframes load{50%{width:70%}100%{width:30%}}</style>
    </div>
    </body>
    </html>
  `);

  startNode();

  waitForNode()
    .then(() => {
      loading.close();
      mainWindow.loadURL(NODE_URL);
      mainWindow.show();
    })
    .catch((err) => {
      loading.close();
      dialog.showErrorBox('Connection Error', `Could not connect to the Globex node.\n\n${err.message}`);
      app.quit();
    });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (nodeProcess) {
    nodeProcess.kill();
    nodeProcess = null;
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (nodeProcess) {
    nodeProcess.kill();
    nodeProcess = null;
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
