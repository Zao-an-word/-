<template>
  <div class="register-page">
    <VideoBackground />
    <!--  左上角固定返回按钮 -->
    <button class="custom-return-btn" @click="goToLogin">返回登录</button>
    <h1 class="title-text">Register</h1>

    <form class="form-wrapper centered-form" @submit.prevent="handleRegister">
      <!-- 新账号输入组 -->
      <div class="form-group">
        <label for="newUsername">👤新账号</label>
        <input
            id="newUsername"
            v-model="username"
            type="text"
            placeholder="请输入新账号"
            required
        />
      </div>

      <!-- 密码输入组 -->
      <div class="form-group">
        <label for="newPassword">🔐设置密码</label>
        <input
            id="newPassword"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
        />
      </div>

      <!-- 确认密码输入组 -->
      <div class="form-group">
        <label for="confirmPassword">🔐确认密码</label>
        <input
            id="confirmPassword"
            v-model="confirmPwd"
            type="password"
            placeholder="请再次输入密码"
            required
        />
      </div>

      <div class="btn-group">
        <button type="submit">注册</button>
        <button @click="goToLogin" type="button">返回登录</button>
      </div>
    </form>
  </div>
</template>

<script>
import VideoBackground from "@/components/VideoBackground.vue";
import axios from "axios";

export default {
  components: { VideoBackground },
  data() {
    return {
      username: "",
      password: "",
      confirmPwd: ""
    };
  },
  methods: {
    async handleRegister() {
      if (this.password.length<6){
        alert("密码长度不能小于6");
        return;
      }
      if (this.password !== this.confirmPwd) {
        alert("两次密码不一致！");
        return;
      }
      try {
        await axios.post("http://localhost:8000/api/register", {
          username: this.username,
          password: this.password
        });
        alert("注册成功！");
        this.goToLogin();
      } catch (err) {
        // 输出报错信息
        console.error(err);

        alert("注册失败");
      }
    },
    goToLogin() {
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
.title-text {
  font-size: 64px;
  text-align: center;
  color: #f671f2;
  text-shadow: 2px 2px 5px #ffffffaa;
}

/* 新增：表单组样式 */
.form-group {
  margin-bottom: 15px;
}

/* 新增：标签样式 */
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

input {
  display: block;
  width: 100%;
  margin: 10px auto;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

input:focus {
  border: 2px solid #ff66cc;
  box-shadow: 0 0 10px #ff66cc;
  background-color: #fff0fa;
}

.btn-group {
  display: flex;
  justify-content: space-between;
}

.centered-form {
  width: 33.33%; /* 占据页面宽度的1/3 */
  /* 水平居中 */
  position: relative; /* 为了让表单在垂直方向上居中 */
  top: 50%; /* 移动到页面垂直方向的中间 */
  transform: translateY(-50%); /* 向上移动自身高度的一半，实现垂直居中 */
  margin: 200px auto 0;
}

button {
  padding: 10px 20px;
  border-radius: 12px;
  background: #dfaaaa;
  border: none;
  color: black;
  cursor: pointer;
  transition: background 0.3s ease; /* 添加过渡效果 */
}
.btn-group button:hover {
  background: #f1e1e1;
}
.btn-group button:active {
  background: #c78888; /* 点击时的背景颜色 */
}

.custom-return-btn {
  position: fixed; /* 固定在屏幕左上角 */
  top: 20px;
  left: 20px;
  width: 120px;
  height: 120px;
  border: none;
  border-radius: 12px; /* 圆角矩形 */
  background-image: url('../assets/img/whale.png'); /* 使用本地图片 */
  background-size: cover;
  background-position: center;
  color: #8a2be2; /* 紫色文字 */
  font-size: 16px;
  font-weight: bold;
  font-family: 'Arial', sans-serif;
  z-index: 9999;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
  transition: transform 0.2s ease;
}

.custom-return-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px #c285ff;
}

.custom-return-btn:active {
  transform: scale(0.95);
}

</style>