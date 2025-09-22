// psy_admin_vue/src/router/index.js

import { createRouter, createWebHistory } from "vue-router";
import LoginView from "../views/LoginView.vue";
import TestRecordsView from "../views/TestRecordsView.vue"; // <<<<<<< 导入 TestRecordsView
import StudentManagement from "../views/StudentManagement.vue";
import ReportsHome from "../views/ReportsHome.vue";
import ReportView from "../views/ReportView.vue";
import DashboardView from "../views/DashboardView.vue";
import TestRecordDetailView from "../views/TestRecordDetailView.vue";
import { isTokenExpired } from "../utils/auth.js";

const routes = [
  {
    path: "/",
    name: "dashboard",
    component: DashboardView,
    meta: { requiresAuth: true }, // 首页设置为仪表板
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/dashboard",
    name: "DashboardView",
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: "/test-records",
    name: "TestRecords",
    component: TestRecordsView,
    meta: { requiresAuth: true },
  },
  {
    path: "/test-records/:id",
    name: "TestRecordDetail",
    component: TestRecordDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: "/student-management",
    name: "StudentManagement",
    component: StudentManagement,
    meta: { requiresAuth: true },
  },
  {
    path: "/reports",
    name: "ReportsHome",
    component: ReportsHome,
    meta: { requiresAuth: true },
  },
  {
    path: "/reports/:student_id",
    name: "ReportView",
    component: ReportView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL), // 使用 process.env.BASE_URL 以更好地处理部署路径
  routes,
});

// 全局路由守卫：检查路由是否需要认证
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("access_token");

  // 检查token是否过期
  if (token) {
    if (isTokenExpired(token)) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_info");
    }
  }

  // 检查目标路由是否需要认证
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!token || isTokenExpired(token)) {
      // 需要认证但没有有效token，重定向到登录页
      next({ name: "login" });
    } else {
      // 有有效token，允许导航
      next();
    }
  } else {
    // 不需要认证的路由，直接允许导航
    next();
  }
});

export default router;
