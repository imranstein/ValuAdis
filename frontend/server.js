const { createServer } = require('http')
const { exec } = require('child_process')

const port = process.env.NUXT_PORT || 3020
const host = process.env.NUXT_HOST || '0.0.0.0'

// Create a simple proxy server that forwards requests to Nuxt
const server = createServer((req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200)
    res.end()
    return
  }
  
  // Forward to Nuxt dev server
  const proxy = require('http').request({
    hostname: 'localhost',
    port: 3000,
    path: req.url,
    method: req.method,
    headers: req.headers
  }, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers)
    proxyRes.pipe(res)
  })
  
  proxy.on('error', (err) => {
    console.error('Proxy error:', err)
    res.writeHead(502)
    res.end('Bad Gateway')
  })
  
  req.pipe(proxy)
})

// Start Nuxt in background
console.log('Starting Nuxt development server...')
exec('npm run dev', (error, stdout, stderr) => {
  if (error) {
    console.error('Error starting Nuxt:', error)
    return
  }
  console.log('Nuxt stdout:', stdout)
  if (stderr) {
    console.error('Nuxt stderr:', stderr)
  }
})

// Wait a bit for Nuxt to start, then start proxy server
setTimeout(() => {
  server.listen(port, host, () => {
    console.log(`Frontend server running on http://${host}:${port}`)
  })
}, 5000)
