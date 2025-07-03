const { app, BrowserWindow, ipcMain, screen } = require('electron');
const { exec } = require('child_process');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

let mainWindow = null;
let dataWindow = null;

function createMainWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    title: 'Main',
    width: width*0.9,
    height: height*0.9,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // ✅ POINT TO preload.js
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
}

app.whenReady().then(createMainWindow);

// ✅ When "Data" is clicked
ipcMain.on('open-data-window', () => {

  const { width, height } = screen.getPrimaryDisplay().workAreaSize;
  if (dataWindow) {
    dataWindow.focus();
    return;
  }

  dataWindow = new BrowserWindow({
    width: width*0.5,
    height: height*0.5,
    title: "Simulation Data",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  dataWindow.loadFile(path.join(__dirname, 'simulation.html'));

  dataWindow.on('closed', () => {
    dataWindow = null;
  });
});


// Run the Python simulation when triggered
ipcMain.handle('run-simulation', async () => {
    return new Promise((resolve, reject) => {
        exec('python app.py', (error, stdout, stderr) => {
            if (error) return reject(stderr || error.message);

            const csvPath = stdout.trim(); // assume this is the path to output.csv
            fs.readFile(csvPath, 'utf8', (err, data) => {
                if (err) return reject(err);
                
                // Parse CSV
                const lines = data.trim().split('\n').slice(1); // skip header
                const numbers = lines.map(line => parseInt(line));
                resolve(numbers);
            });
        });
    });
});


