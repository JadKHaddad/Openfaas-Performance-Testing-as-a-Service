module.exports = {
    //publicPath: process.env.NODE_ENV === 'production' ? 'static/' : '/',
    devServer: {
      clientLogLevel: 'info',
      proxy: {
        '/': {
          target: 'http://localhost',
          changeOrigin: true,
          pathRewrite: {
            '^/': ''
          }
        }
      }
    }
  };