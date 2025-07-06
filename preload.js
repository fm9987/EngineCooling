const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {  
    reset: () => ipcRenderer.invoke('reset'),
    openFileDialog: () => ipcRenderer.invoke('dialog:openFile'),
    setInputFilePath: (path) => ipcRenderer.send('set-input-file-path', path),
    runSimulation: (filePath) => ipcRenderer.invoke('run-simulation', filePath),
    readCSV: (filePath) => ipcRenderer.invoke('read-csv',filePath),
    openDataWindow: () => ipcRenderer.send('open-data-window')
});