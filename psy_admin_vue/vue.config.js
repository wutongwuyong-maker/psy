const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    // 关闭错误遮罩，避免 ResizeObserver 和 setAttribute 错误导致页面被遮罩覆盖
    // webpack-dev-server v4 必须使用 client.overlay
    client: {
      overlay: false,
      // 或精细控制：
      // overlay: {
      //   errors: false,
      //   warnings: false,
      // },
    },
    proxy: {
      "/api": {
        target: process.env.VUE_APP_API_BASE || "http://localhost:8002",
        changeOrigin: true,
      },
    },
  },
});
