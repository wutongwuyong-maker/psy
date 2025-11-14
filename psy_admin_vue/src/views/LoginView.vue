<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="clearfix">
          <span>心理检测管理后台</span>
        </div>
      </template>
      <el-form
        @submit.prevent="handleLogin"
        :model="loginForm"
        :rules="loginRules"
        ref="loginFormRef"
        label-width="0px"
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="el-icon-user"
          ></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            type="password"
            v-model="loginForm.password"
            placeholder="密码"
            prefix-icon="el-icon-lock"
          ></el-input>
        </el-form-item>
        <el-form-item class="login-button">
          <el-button type="primary" native-type="submit" :loading="loading"
            >登录</el-button
          >
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "LoginView",
  data() {
    return {
      loginForm: {
        username: "admin",
        password: "admin123",
      },
      loginRules: {
        username: [
          { required: true, message: "请输入用户名", trigger: "blur" },
        ],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }],
      },
      loading: false,
    };
  },
  methods: {
    handleLogin() {
      this.$refs.loginFormRef.validate(async (valid) => {
        if (valid) {
          this.loading = true;
          try {
            const API_BASE_URL =
              process.env.VUE_APP_API_BASE || "http://localhost:8000";
            const tokenUrl = `${API_BASE_URL}/token`;

            const params = new URLSearchParams();
            params.append("username", this.loginForm.username);
            params.append("password", this.loginForm.password);
            params.append("grant_type", "password");

            const response = await axios.post(tokenUrl, params, {
              headers: {
                "Content-Type": "application/x-www-form-urlencoded",
              },
            });

            // *** 调试点：打印后端返回的原始数据 ***
            console.log("后端响应数据:", response.data);

            // 确保 response.data 包含 access_token 和 token_type
            // 如果后端返回的JSON字段名与这里不符，这里会出错
            const { access_token, token_type } = response.data;

            localStorage.setItem("access_token", access_token);
            localStorage.setItem("token_type", token_type);

            this.$message.success("登录成功！");
            this.$router.push("/test-records");
          } catch (error) {
            console.error("登录失败:", error);
            let errorMessage = "登录失败，请检查网络或服务器。";
            if (error.response) {
              if (error.response.status === 401) {
                errorMessage = "用户名或密码不正确，请重试。";
              } else if (error.response.data && error.response.data.detail) {
                errorMessage = `登录失败: ${error.response.data.detail}`;
              }
            }
            this.$message.error(errorMessage);
          } finally {
            this.loading = false;
          }
        } else {
          this.$message.warning("请填写完整的登录信息！");
          return false;
        }
      });
    },
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both;
}

.login-form {
  padding: 20px;
}

.login-button {
  text-align: center;
}

.login-button .el-button {
  width: 100%;
}
</style>
