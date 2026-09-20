const http = require('node:http');
const port = process.env.PORT || 8080;
const createServer = () => http.createServer((req, res) => {
  res.setHeader('content-type', 'application/json');
  if (req.url === '/health') return res.end(JSON.stringify({ status: 'ok', service: 'portfolio-api' }));
  if (req.url === '/') return res.end(JSON.stringify({ message: 'DevOps portfolio API', version: '1.0.0' }));
  res.statusCode = 404; return res.end(JSON.stringify({ error: 'not found' }));
});
if (require.main === module) createServer().listen(port, () => console.log(`portfolio-api listening on ${port}`));
module.exports = createServer;
