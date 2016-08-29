var http = require('http');

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Test\n');
}).listen(8080);

console.log('Server running on port 8080.');