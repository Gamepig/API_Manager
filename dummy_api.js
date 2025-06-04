const http = require('http');

// 從命令行參數解析端口
const args = process.argv.slice(2);
let port = 3000; // 預設端口
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--port' && args[i + 1]) {
    port = parseInt(args[i + 1]);
    break;
  }
}

const server = http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello from Dummy API! Running on port ' + port);
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`Port ${port} is already in use. Please try another port.`);
  } else {
    console.error('Server error:', err.message);
  }
  process.exit(1);
});

server.listen(port, () => {
  console.log(`Dummy API running on port ${port}`);
}); 