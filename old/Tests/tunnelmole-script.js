const { exec } = require('child_process');
const path = require('path');

function startTunnelmole() {
  const port = 8080; // Replace with the desired port number
  const domain = 'technikag.tunnelmole.com'; // Replace with your custom subdomain

  const tmolePath = path.join(__dirname, 'tunnelmole', 'tmole');

  exec(`"${tmolePath}" ${port} --domain ${domain}`, (error, stdout, stderr) => {
    if (error) {
      console.error('Failed to start Tunnelmole:', error);
      return;
    }
    console.log('Tunnelmole started successfully!');
    console.log(stdout);
  });
}

startTunnelmole();
