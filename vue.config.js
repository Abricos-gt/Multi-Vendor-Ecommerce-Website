const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  productionSourceMap: false,
  configureWebpack: config => {
    // Drop console/debugger in production and set performance budgets
    if (!config.optimization) config.optimization = {}
    config.optimization.splitChunks = {
      chunks: 'all',
      maxInitialRequests: 10,
      maxAsyncRequests: 20,
      cacheGroups: {
        vendors: { test: /[\\/]node_modules[\\/]/, name: 'chunk-vendors', chunks: 'all', priority: -10 },
        common: { name: 'chunk-common', minChunks: 2, priority: -20, chunks: 'all', reuseExistingChunk: true }
      }
    }
    config.performance = {
      hints: 'warning',
      maxEntrypointSize: 250 * 1024,
      maxAssetSize: 250 * 1024
    }
  },
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
