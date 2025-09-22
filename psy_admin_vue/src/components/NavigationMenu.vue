<template>
  <div class="nav-menu">
    <div class="nav-header">
      <div class="logo">
        <i class="el-icon-s-data"></i>
        <span>心理检测管理系统</span>
      </div>
    </div>

    <el-menu
      :default-active="activeIndex"
      class="nav-menu-items"
      :router="true"
      background-color="transparent"
      text-color="#666"
      active-text-color="#409EFF"
    >
      <el-menu-item index="/dashboard">
        <i class="el-icon-s-home"></i>
        <span>系统概览</span>
      </el-menu-item>

      <el-menu-item index="/test-records">
        <i class="el-icon-document"></i>
        <span>检测记录</span>
      </el-menu-item>

      <el-menu-item index="/student-management">
        <i class="el-icon-user"></i>
        <span>学生管理</span>
      </el-menu-item>

      <el-menu-item index="/reports">
        <i class="el-icon-s-marketing"></i>
        <span>报告管理</span>
      </el-menu-item>
    </el-menu>

    <div class="nav-footer">
      <el-button type="text" @click="handleLogout" class="logout-btn">
        <i class="el-icon-switch-button"></i>
        <span>退出登录</span>
      </el-button>
    </div>
  </div>
</template>

<script>
import { computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";

export default {
  name: "NavigationMenu",
  setup() {
    const router = useRouter();
    const route = useRoute();

    const activeIndex = computed(() => route.path);

    const handleLogout = () => {
      localStorage.removeItem("access_token");
      ElMessage.success("退出登录成功");
      router.push("/login");
    };

    return {
      activeIndex,
      handleLogout,
    };
  },
};
</script>

<style scoped>
.nav-menu {
  width: 250px;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.nav-header {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: white;
  font-size: 18px;
  font-weight: 600;
}

.logo i {
  font-size: 24px;
}

.nav-menu-items {
  flex: 1;
  border: none;
}

.nav-menu-items :deep(.el-menu-item) {
  margin: 4px 10px;
  border-radius: 8px;
  margin-bottom: 4px;
}

.nav-menu-items :deep(.el-menu-item.is-active) {
  background-color: rgba(255, 255, 255, 0.2);
  border-left: 4px solid #409eff;
}

.nav-menu-items :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.logout-btn {
  width: 100%;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.1);
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.logout-btn i {
  margin-right: 8px;
}
</style>
