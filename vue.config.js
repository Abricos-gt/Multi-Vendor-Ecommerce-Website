const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8080, // Force frontend to run on default port
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
        ws: false,
        secure: false,
        logLevel: 'debug' // Add debug logging
      }
    }
  }
})
