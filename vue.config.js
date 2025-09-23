const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 8085, // Force frontend to run on port 8085
    host: 'localhost',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        pathRewrite: { '^/api': '' },
        ws: false,
        secure: false,
        logLevel: 'debug'
      }
    }
  }
})
