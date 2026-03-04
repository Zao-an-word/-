<template>
  <div class="change-password-container">
    <h2>修改密码</h2>

    <form @submit.prevent="handleSubmit" class="password-form">
      <!-- 旧密码 -->
      <div class="form-group">
        <label for="oldPassword">旧密码</label>
        <input
          type="password"
          id="oldPassword"
          v-model="form.oldPassword"
          required
          :disabled="loading"
          placeholder="请输入旧密码(至少6位)"
        >
        <p class="error-message" v-if="errors.oldPassword">{{ errors.oldPassword }}</p>
      </div>

      <!-- 新密码 -->
      <div class="form-group">
        <label for="newPassword">新密码</label>
        <input
          type="password"
          id="newPassword"
          v-model="form.newPassword"
          required
          :disabled="loading"
          placeholder="请输出新密码（至少6位字符）"
        >
        <p class="error-message" v-if="errors.newPassword">{{ errors.newPassword }}</p>
      </div>

      <!-- 确认新密码 -->
      <div class="form-group">
        <label for="confirmPassword">确认新密码</label>
        <input
          type="password"
          id="confirmPassword"
          v-model="form.confirmPassword"
          required
          :disabled="loading"
          placeholder="再次输入新密码"
        >
        <p class="error-message" v-if="errors.confirmPassword">{{ errors.confirmPassword }}</p>
      </div>

      <!-- 提交按钮 -->
      <button
        type="submit"
        class="submit-btn"
        :disabled="loading"
      >
        <span v-if="loading">修改中...</span>
        <span v-else>确认修改</span>
      </button>

      <!-- 提示信息 -->
      <p class="message success" v-if="message && !isError">{{ message }}</p>
      <p class="message error" v-if="message && isError">{{ message }}</p>
    </form>

    <!-- 返回按钮 -->
    <button class="back-btn" @click="$router.go(-1)" :disabled="loading">
      返回
    </button>
  </div>
</template>

<script>
export default {
  name: "ChangePassword",
  data() {
    return {
      form: {
        oldPassword: "",
        newPassword: "",
        confirmPassword: ""
      },
      errors: {}, // 表单验证错误
      message: "", // 操作提示信息
      isError: false, // 是否为错误提示
      loading: false // 加载状态
    };
  },
  methods: {
    // 表单验证
    validateForm() {
      const errors = {};
      // 验证旧密码
      if (!this.form.oldPassword) {
        errors.oldPassword = "请输入旧密码";
      }
      // 验证新密码
      if (!this.form.newPassword) {
        errors.newPassword = "请输入新密码";
      } else if (this.form.newPassword.length < 6) {
        errors.newPassword = "新密码至少6位";
      }
      // 验证确认密码
      if (!this.form.confirmPassword) {
        errors.confirmPassword = "请确认新密码";
      } else if (this.form.newPassword !== this.form.confirmPassword) {
        errors.confirmPassword = "两次输入的密码不一致";
      }
      // 更新错误信息
      this.errors = errors;
      // 验证通过返回true
      return Object.keys(errors).length === 0;
    },

    // 提交表单
    async handleSubmit() {
      // 前端表单验证
      if (!this.validateForm()) return;

      this.loading = true;
      this.message = "";

      try {
        // 获取token
        const token = localStorage.getItem("token");
        if (!token) {
          this.$router.push("/login");
          return;
        }

        // 调用后端接口
        const response = await this.$axios.post(
          "/api/modify-password",
          {
            old_password: this.form.oldPassword,
            new_password: this.form.newPassword
          },
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        // 成功处理
        this.isError = false;
        this.message = response.data.message;
        // 清空表单
        this.form = {
          oldPassword: "",
          newPassword: "",
          confirmPassword: ""
        };
        // 3秒后跳转到登录页
        setTimeout(() => {
          localStorage.removeItem("token");
          this.$router.push("/login");
        }, 3000);

      } catch (error) {
        // 错误处理
        this.isError = true;
        this.message = error.response?.data?.detail || "修改密码失败，请重试";
        console.error("修改密码错误:", error);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.change-password-container {
  max-width: 500px;
  margin: 50px auto;
  padding: 20px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.password-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 500;
  color: #555;
}

input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.error-message {
  color: #ff4d4f;
  font-size: 14px;
  margin: 0;
  height: 14px;
}

.submit-btn {
  padding: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background-color: #096dd9;
}

.submit-btn:disabled {
  background-color: #8cc5ff;
  cursor: not-allowed;
}

.back-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: transparent;
  color: #1890ff;
  border: 1px solid #1890ff;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover:not(:disabled) {
  background-color: #e6f7ff;
}

.message {
  text-align: center;
  margin: 15px 0 0;
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
}

.success {
  color: #52c41a;
  background-color: #f6ffed;
  border: 1px solid #b7eb8f;
}

.error {
  color: #ff4d4f;
  background-color: #fff2f0;
  border: 1px solid #ffccc7;
}
</style>
