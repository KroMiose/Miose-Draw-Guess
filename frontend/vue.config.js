const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  publicPath:'./',
    //配置代理跨域  // 生产环境下无效
    devServer: {
      proxy: {
        "/api": {
            target: "http://localhost:2900",
            changeOrigin: true,
            ws: true,
            pathRewrite: {
              '^/api': ''
            }
        },
      },
    },
})
