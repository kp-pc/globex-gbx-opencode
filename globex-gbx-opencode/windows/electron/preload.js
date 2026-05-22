const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('globex', {
  platform: process.platform,
  nodeVersion: process.versions.node,
  electronVersion: process.versions.electron,
});
