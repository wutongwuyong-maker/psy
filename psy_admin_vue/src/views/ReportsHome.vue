<template>
  <div class="reports-home">
    <h2 class="page-title">报告管理</h2>
    <el-card>
      <el-form>
        <el-form-item label="学号">
          <el-input v-model="studentId" placeholder="请输入学号"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="go">查看报告</el-button>
          <button v-if="false" @click="go" class="el-button el-button--primary">
            测试按钮
          </button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const studentId = ref("");

const go = () => {
  console.log("按钮被点击了");
  console.log("学号值:", studentId.value);
  if (!studentId.value) {
    console.log("学号为空，不执行跳转");
    return;
  }
  console.log("准备跳转到报告页面");
  router.push(`/reports/${encodeURIComponent(studentId.value)}`);
};
</script>

<style scoped>
.reports-home {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}
.page-title {
  text-align: center;
  margin-bottom: 16px;
}
</style>
