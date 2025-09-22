import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store"; // 如果你使用 Vuex

// 1. 导入 Element Plus（替代 Element UI）
import ElementPlus from "element-plus";
import "element-plus/dist/index.css"; // 核心样式
import "@/assets/css/healing-theme.css";
import * as ElementPlusIconsVue from "@element-plus/icons-vue"; // 图标
import "./assets/css/global.css"; // 确保路径正确
// 2. 导入 axios 配置（用于全局挂载）
import http from "./http";

// 3. 导入全局样式（如果需要，先创建文件）
// import "./assets/css/global.css";

// 创建 Vue 3 应用实例
const app = createApp(App);

// 注册路由和状态管理
app.use(router);
app.use(store);

// 注册 Element Plus 组件和图标
app.use(ElementPlus);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

// 4. 全局挂载 axios（替代 Vue.prototype.$http）
app.config.globalProperties.$http = http;

// 挂载应用到 DOM（替代 new Vue(...).$mount("#app")）
app.mount("#app");
