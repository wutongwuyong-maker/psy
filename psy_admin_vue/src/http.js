// src/http.js
import axios from "axios";
import { ElMessage as Message } from "element-plus";
import router from "./router";

const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE || "http://localhost:8000",
  timeout: 10000,
});

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
service.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_info");
      Message.error("登录状态已失效，请重新登录。");
      router.push("/login");
    } else if (error.response?.data?.detail) {
      Message.error(error.response.data.detail);
    } else if (error.code === "ECONNABORTED") {
      Message.error("请求超时，请检查网络连接。");
    } else if (!error.response) {
      Message.error("网络连接失败，请检查网络设置。");
    } else {
      Message.error("请求失败，请稍后再试。");
    }
    return Promise.reject(error);
  }
);

export default service;
