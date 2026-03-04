// src/main.js（在挂载 axios 之后添加）
import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import SakuraTailPlugin from './plugins/cherry-blossoms'

const app = createApp(App);
axios.defaults.baseURL = 'http://localhost:8000';

// 添加请求拦截器：自动携带 token
axios.interceptors.request.use(
  (config) => {
    // 从 localStorage 中获取 token（登录时需保存 token 到这里）
    const token = localStorage.getItem('token');
    if (token) {
      // 格式：Bearer <token>（后端通常要求这种格式）
      config.headers.Authorization = `Bearer ${token}`;
      console.log('请求拦截器 - 添加的 Token:', token);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 添加响应拦截器：统一处理错误
axios.interceptors.response.use(
  (response) => {
    return response; // 成功响应直接返回
  },
  (error) => {
    // 处理 401 未授权（token 无效或过期）
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token'); // 清除无效 token
      router.push('/login'); // 跳转到登录页
      alert('登录已过期，请重新登录');
    }
    return Promise.reject(error);
  }
);

app.config.globalProperties.$axios = axios;
app.use(router);
app.use(SakuraTailPlugin)
app.mount('#app');