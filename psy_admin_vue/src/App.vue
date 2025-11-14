<template>
  <div id="app" class="app-container">
    <!-- 导航菜单 -->
    <NavigationMenu v-if="showNavigation" />

    <!-- 主要内容区域 -->
    <div class="main-content" :class="{ 'with-nav': showNavigation }">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import NavigationMenu from "@/components/NavigationMenu.vue";

const router = useRouter();

// 判断是否显示导航菜单
const showNavigation = computed(() => {
  const currentPath = router.currentRoute.value.path;
  return !currentPath.includes("/login");
});
</script>

<style>
/* 全局变量已放到 healing-theme.css */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-main);
  min-height: 100vh;
}

.app-container {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  transition: margin-left 0.3s ease;
}

.main-content.with-nav {
  margin-left: 250px;
}

/* 登录页面特殊样式 */
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

.login-page .main-content {
  margin-left: 0;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>

<style scoped>
/* 确保登录页面不显示导航 */
.login-page {
  margin-left: 0;
}
</style>
