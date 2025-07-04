const { app, BrowserWindow, ipcMain, screen, dialog } = require('electron');
const { exec } = require('child_process');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

let mainWindow = null;
let dataWindow = null;
let inputFilePath = null;



ipcMain.on('set-input-file-path', (event, path) => {
  console.log('Received input file path:', path);
  inputFilePath = path;
});

function createMainWindow() {
  const { width, height } = screen.getPrimaryDisplay().workAreaSize;

  mainWindow = new BrowserWindow({
    title: 'Main',
    width: width*0.95,
    height: height,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'), // ✅ POINT TO preload.js
      nodeIntegration: false,
      contextIsolation: true
    },
    autoHideMenuBar: true // ✅ This hides the menu bar!
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
}

//Try this to deactivate the flickers
app.disableHardwareAcceleration();

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


ipcMain.handle('run-simulation', async () => {
    return new Promise((resolve, reject) => {
        if (!inputFilePath) return reject(new Error('No input file set'));

        const py = spawn('python', ['app.py', inputFilePath]);

        let outputFilePath = '';

        py.stdout.on('data', (data) => {
            outputFilePath += data.toString();
        });

        py.stderr.on('data', (data) => {
            console.error('Python error:', data.toString());
        });

        py.on('close', (code) => {
            if (code === 0) {
                resolve(outputFilePath.trim()); // send the output file path back
            } else {
                reject(new Error('Simulation failed'));
            }
        });
    });
});

ipcMain.handle('read-csv', async (event, filePath) => {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return content;
  } catch (err) {
    console.error('Error reading file:', err);
    return null;
  }
});


ipcMain.handle('dialog:openFile', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [{ name: 'CSV Files', extensions: ['csv'] }],
  });
  if (result.canceled) {
    return null;
  } else {
    return result.filePaths[0];
  }
});

ipcMain.handle('reset', async () => {
    mainWindow.reload();
})