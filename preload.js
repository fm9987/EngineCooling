// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
    runSimulation: () => ipcRenderer.invoke('run-simulation')
});

