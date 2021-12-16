module.exports = {
    //publicPath: process.env.NODE_ENV === 'production' ? 'static/' : '/',
    devServer: {
      clientLogLevel: 'info',
      proxy: {
        '/': {
          target: 'http://192.168.178.64',
          changeOrigin: true,
          pathRewrite: {
            '^/': ''
          }
        }
      }
    }
  };