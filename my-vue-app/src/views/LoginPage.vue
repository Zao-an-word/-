<template>

  <MainPage ref="childRef" />
  <div class="login-page">
    <VideoBackground />
    <h1 class="title-text">文思成真</h1>

    <form class="form-wrapper centered-form" @submit.prevent="handleLogin">
      <!-- 账号输入组 -->
      <div class="form-group">
        <label for="username">👤账号</label>
        <input
            id="username"
            v-model="username"
            type="text"
            placeholder="请输入账号"
            required
        />
      </div>

      <!-- 密码输入组 -->
      <div class="form-group">
        <label for="password">🔐密码</label>
        <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
        />
      </div>

      <div class="btn-group">
        <button type="submit">登录</button>
        <button @click="goToRegister" type="button">注册</button>
      </div>
    </form>
  </div>
</template>

<script>
import VideoBackground from "@/components/VideoBackground.vue";
import axios from "axios";
import qs from "qs";
export default {
  components: { VideoBackground},
  data() {
    return {
      username: "",
      password: "",
      role: null,
    };
  },
  methods: {
    async handleLogin() {
      try {
        const response = await axios.post(
          "http://localhost:8000/api/login",
          qs.stringify({
            username: this.username,
            password: this.password,
          }),
          {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
          }
        );

        const { access_token, role } = response.data;
        localStorage.setItem("token", access_token);
        localStorage.setItem("userRole", role);
        this.role = role;

        if (this.role === 1) {
          alert(`管理员 ${this.username} 登录成功！`);
          this.$router.push("/admin");
        } else {
          alert(`欢迎回来，${this.username}！`);
          const response = await axios.post(`http://localhost:8000/api/get_conversations`);
          const result = response.data;
          const lenth = result.length;

          const token = localStorage.getItem('token');
          if(lenth==0){
            const response = await axios.post("http://localhost:8000/api/get_port", {},{
              headers: { Authorization: `Bearer ${token}` }
            });
            const port = response.data.port;
            this.$router.push(`/main/${port}`);
          }
          else{
            const response = await axios.post("http://localhost:8000/api/to_port?num=1", {},{
              headers: { Authorization: `Bearer ${token}` }
            });
            const port = response.data
            console.log("端口号", port);
            this.$router.push(`/main/${port}`);

          }
        }
      }  catch (err) {
        console.error("登录失败：", err);
        alert("账号或密码错误，请重试~");
      }
    },
    goToRegister() {
      this.$router.push("/register");
    },
  },
};
</script>

<style scoped>
.title-text {
  font-size: 64px;
  text-align: center;
  color: #004080;
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
  transition: background-color 0.3s ease;  /* 添加过渡效果 */
}
button:hover {
  background: #f1e1e1; /* 鼠标悬停时的背景颜色 */
}
button:active {
  background: #c78888; /* 点击时的背景颜色 */
}
</style>
