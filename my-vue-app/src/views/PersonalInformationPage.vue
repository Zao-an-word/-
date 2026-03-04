<template>
  <div class="personal-info-container">
    <!-- 顶部导航栏 -->
    <div class="info-header">
      <button class="back-btn" @click="goBack">
        <i class="back-icon">←</i> 返回
      </button>
      <h1 class="page-title">个人信息</h1>
      <div class="header-placeholder"></div> <!-- 占位元素保持标题居中 -->
    </div>

    <!-- 主要内容区 -->
    <div class="info-content">
      <!-- 头像与用户名区域 -->
      <div class="avatar-section">
        <div class="avatar-container">
          <img
              :src="userInfo.avatar || defaultAvatar"
              alt="用户头像"
              class="user-avatar"
              @click="previewAvatar"
          >
          <label class="avatar-upload-btn">
            <input type="file" accept="image/*" @change="handleAvatarUpload" class="avatar-file-input">
            <span class="upload-icon">📷</span>
          </label>
        </div>
        <div class="user-basic">
          <h2 class="username">{{ userInfo.name }}</h2>
          <p class="user-id">ID: {{ userInfo.userId }}</p>
        </div>
      </div>

      <!-- 信息卡片容器 -->
      <div class="info-cards">
        <!-- 基本信息卡片 -->
        <div class="info-card">
          <div class="card-header">
            <h3>基本信息</h3>
            <button
                class="edit-btn"
                :class="{ active: isEditing }"
                @click="toggleEdit"
                :disabled="isSaving"
            >
              {{ isSaving ? '保存中...' : (isEditing ? '完成' : '编辑') }}
            </button>
          </div>

          <div class="info-list">
            <div class="info-item">
              <span class="info-label">邮箱</span>
              <div class="info-value">
                <template v-if="isEditing">
                  <input
                      type="email"
                      v-model="tempUserInfo.mailbox"
                      class="edit-input"
                      placeholder="请输入邮箱"
                  >
                </template>
                <template v-else>{{ userInfo.email || '未设置' }}</template>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">手机号码</span>
              <div class="info-value">
                <template v-if="isEditing">
                  <input
                      type="tel"
                      v-model="tempUserInfo.phone"
                      class="edit-input"
                      placeholder="请输入手机号码"
                  >
                </template>
                <template v-else>{{ userInfo.phone || '未设置' }}</template>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">性别</span>
              <div class="info-value">
                <template v-if="isEditing">
                  <select v-model="tempUserInfo.gender" class="edit-select">
                    <option value="">请选择</option>
                    <option value="male">男</option>
                    <option value="female">女</option>
                    <option value="other">其他</option>
                  </select>
                </template>
                <template v-else>
                  {{ genderMap[userInfo.gender] || '未设置' }}
                </template>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">生日</span>
              <div class="info-value">
                <template v-if="isEditing">
                  <input
                      type="date"
                      v-model="tempUserInfo.birthday"
                      class="edit-input"
                  >
                </template>
                <template v-else>{{ userInfo.birthday || '未设置' }}</template>
              </div>
            </div>

            <div class="info-item">
              <span class="info-label">注册时间</span>
              <div class="info-value">{{ userInfo.registerTime || '未知' }}</div>
            </div>
          </div>
        </div>

        <!-- 账户安全卡片 -->
        <div class="info-card security-card">
          <div class="card-header">
            <h3>账户安全</h3>
          </div>

          <div class="security-options">
            <div class="security-item" @click="goToModifyPwd">
              <div class="option-icon">🔒</div>
              <div class="option-info">
                <p class="option-title">修改密码</p>
                <p class="option-desc">上次修改于2天前</p>
              </div>
              <div class="option-arrow">→</div>
            </div>

            <div class="security-item" @click="goToBindPhone">
              <div class="option-icon">📱</div>
              <div class="option-info">
                <p class="option-title">手机绑定</p>
                <p class="option-desc" :class="userInfo.phone ? 'completed' : 'incomplete'">
                  {{ userInfo.phone ? '未绑定' : '未绑定' }}
                </p>
              </div>
              <div class="option-arrow">→</div>
            </div>

            <div class="security-item" @click="goToPrivacySetting">
              <div class="option-icon">🛡️</div>
              <div class="option-info">
                <p class="option-title">隐私设置</p>
                <p class="option-desc">管理个人信息可见范围</p>
              </div>
              <div class="option-arrow">→</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 退出登录按钮 -->
      <button class="logout-btn" @click="confirmLogout">
        退出登录
      </button>
    </div>

    <!-- 编辑成功提示 -->
    <div class="toast" v-if="showToast">{{ toastMessage }}</div>

    <!-- 加载中提示 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner">加载中...</div>
    </div>
  </div> <!-- 已添加根元素的闭合标签 -->
</template>

<script>
import axios from 'axios';

export default {
  name: "PersonalInfo",
  data() {
    return {
      // 用户信息数据
      userInfo: {
        avatar: '',
        name: '',
        userId: '',
        email: '',
        phone: '',
        gender: 'other',
        birthday: null,
        registerTime: ''
      },
      // 编辑状态临时数据
      tempUserInfo: {},
      isEditing: false,
      // 性别映射
      genderMap: {
        male: "男",
        female: "女",
        other: "其他"
      },
      // 提示信息
      showToast: false,
      toastMessage: "",
      // 加载状态
      isLoading: false,
      isSaving: false,
      // 默认头像
      defaultAvatar: require('@/assets/img/userProfile.jpg')
    };
  },
  async created() {
    // 页面加载时获取用户信息
    await this.fetchUserInfo();
  },
  methods: {
    // 获取用户信息
    validateForm() {
        const { birthday, phone, email, gender } = this.tempUserInfo;
        // 验证生日格式（若填写）
        if (birthday) {
          const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
          if (!dateRegex.test(birthday)) {
            this.showToastMessage("生日格式应为 YYYY-MM-DD（如 1990-01-15）");
            return false;
          }
        }
        // 验证手机号（若填写）
        if (phone) {
          const phoneRegex = /^1[3-9]\d{9}$/;
          if (!phoneRegex.test(phone)) {
            this.showToastMessage("请输入有效的11位手机号");
            return false;
          }
        }
        // 验证邮箱（若填写）
        if (email) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(email)) {
            this.showToastMessage("请输入有效的邮箱地址（如 xxx@example.com）");
            return false;
          }
        }

        // 验证性别（确保不为空）
        if (!['male', 'female', 'other'].includes(gender)) {
          this.showToastMessage("请选择性别");
          return false;
        }

        // 所有验证通过返回 true
        return true;
    },

    async fetchUserInfo() {
      try {
        this.isLoading = true;
        const token = localStorage.getItem('token');
        // 仅调用 /api/me 接口，获取完整信息
        const response = await axios.get('/api/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const userData = response.data;

        console.log("后端返回的头像 URL:", userData.avatar_url); // 关键日志
        // 更新用户信息
        this.userInfo = {
          // 基础信息（原 /api/info 字段）
          userId: userData.id,  // 后端id → 前端userId
          name: userData.username,  // 后端username → 前端name
          avatar: userData.avatar_url || this.defaultAvatar,  // 头像URL（默认用本地图片）
          //扩展信息
          email: userData.mailbox,  // 邮箱
          phone: userData.phone || '未绑定',  // 手机号
          gender: userData.gender || 'other',  // 性别
          birthday: userData.birthday ? new Date(userData.birthday).toISOString().split('T')[0] : null,  // 生日格式化
          registerTime: userData.created_at ? new Date(userData.created_at).toLocaleDateString() : ''  // 注册时间
        };
        // 初始化临时数据（用于编辑）
        this.tempUserInfo = JSON.parse(JSON.stringify(this.userInfo));
      } catch (error) {
        console.error('获取用户信息失败:', error);
        this.showToastMessage('获取用户信息失败，请重试');
      } finally {
        this.isLoading = false;
      }
    },

    // 返回上一页
    goBack() {
      this.$router.go(-1);
    },

    // 切换编辑状态
    async toggleEdit() {
      if (this.isEditing) {
        // 保存编辑
        await this.saveUserInfo();
        await this.fetchUserInfo();
      }else{
        this.tempUserInfo = JSON.parse(JSON.stringify(this.userInfo));
      }
      this.isEditing = !this.isEditing;
    },

    // 保存用户信息
    async saveUserInfo() {
      // 1. 前端验证
      if (!this.validateForm()) {
        return;
      }
      try {
        this.isSaving = true;
        const token = localStorage.getItem('token');
        // 2. 处理提交数据
        const submitData = {
          ...this.tempUserInfo,
          // 生日为空字符串时转为null
          birthday: this.tempUserInfo.birthday?.trim() || null,
          // 确保gender不为空（后端枚举要求）
          gender: this.tempUserInfo.gender || 'male'
        };

        // 3. 发送请求
        const response = await axios.put('/api/profile', submitData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        // 4. 更新成功
        this.userInfo = { ...response.data };
        this.showToastMessage('信息保存成功');
      } catch (error) {
        console.error('保存用户信息失败:', error);
        // 提取后端详细错误信息
        const errorDetails = error.response?.data?.detail || [];
        const errorMsg = errorDetails.length
          ? errorDetails.map(item => item.msg).join('；')
          : '保存信息失败，请重试';
        this.showToastMessage(errorMsg);
      } finally {
        this.isSaving = false;
      }
    },

    // 处理头像上传
    async handleAvatarUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      try {
        this.isLoading = true;
        const formData = new FormData();
        formData.append('file', file);
        const token = localStorage.getItem('token');

        const response = await axios.post('/api/upload-avatar', formData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        });

        const newAvatarUrl = response.data.avatar;
        this.userInfo.avatar = newAvatarUrl;
        this.tempUserInfo.avatar = newAvatarUrl;
        this.showToastMessage('头像上传成功');
        await this.fetchUserInfo();
      } catch (error) {
        console.error('上传头像失败:', error);
        const errorMsg = error.response?.data?.detail || '上传头像失败，请重试';
        this.showToastMessage(errorMsg);
      } finally {
        this.isLoading = false;
        e.target.value = null;
      }
    },

    // 预览头像
    previewAvatar() {
      // 实现头像预览弹窗逻辑
      window.open(this.userInfo.avatar, "_blank", "width=500,height=500");

    },

    // 显示提示信息
    showToastMessage(message) {
      this.toastMessage = message;
      this.showToast = true;
      setTimeout(() => {
        this.showToast = false;
      }, 3000);
    },

    // 安全设置相关跳转
    goToModifyPwd() {
      this.$router.push("/modify-password");
    },
    goToBindPhone() {
      this.$router.push("/bind-phone").then(() => {
      this.fetchUserInfo(); // 重新调用获取用户信息的方法，更新 userInfo.phone
    });
    },
    goToPrivacySetting() {
      this.$router.push("/privacy-setting");
    },

    // 退出登录确认
    confirmLogout() {
      if (confirm("确定要退出登录吗？")) {
        // 清除登录状态
        localStorage.removeItem("token");
        this.$router.push("/login");
      }
    }
  }
};
</script>


<style scoped>
.personal-info-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 40px;
}

/* 顶部导航 */
.info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  display: flex;
  align-items: center;
  background: none;
  border: none;
  font-size: 16px;
  color: #333;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.back-btn:hover {
  background-color: #f5f5f5;
}

.back-icon {
  margin-right: 6px;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-placeholder {
  width: 60px; /* 与返回按钮宽度保持一致，确保标题居中 */
}

/* 主要内容区 */
.info-content {
  max-width: 700px;
  margin: 0 auto;
  padding: 20px;
}

/* 头像区域 */
.avatar-section {
  display: flex;
  align-items: center;
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  margin-bottom: 20px;
}

.avatar-container {
  position: relative;
  margin-right: 24px;
}

.user-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f0f0f0;
  cursor: pointer;
  transition: transform 0.2s;
}

.user-avatar:hover {
  transform: scale(1.03);
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 36px;
  height: 36px;
  background-color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: transform 0.2s;
}

.avatar-upload-btn:hover {
  transform: scale(1.1);
}

.avatar-file-input {
  display: none;
}

.upload-icon {
  font-size: 16px;
}

.user-basic {
  flex: 1;
}

.username {
  margin: 0 0 8px 0;
  font-size: 22px;
  color: #333;
}

.user-id {
  margin: 0;
  color: #888;
  font-size: 14px;
}

/* 信息卡片样式 */
.info-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  overflow: hidden;
  transition: box-shadow 0.3s;
}

.info-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f0f0f0;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.edit-btn {
  background: none;
  border: none;
  color: #409eff;
  font-size: 14px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 4px;
  transition: all 0.2s;
}

.edit-btn.active {
  background-color: #409eff;
  color: white;
}

.edit-btn:hover:not(.active) {
  background-color: #f0f7ff;
}

/* 信息列表 */
.info-list {
  padding: 10px 0;
}

.info-item {
  display: flex;
  padding: 14px 20px;
  border-bottom: 1px solid #f5f5f5;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  width: 100px;
  color: #888;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.info-value {
  flex: 1;
  font-size: 15px;
  color: #333;
  display: flex;
  align-items: center;
}

.edit-input, .edit-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.edit-input:focus, .edit-select:focus {
  border-color: #409eff;
}

/* 安全设置选项 */
.security-options {
  padding: 8px 0;
}

.security-item {
  display: flex;
  align-items: center;
  padding: 14px 20px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.security-item:hover {
  background-color: #f9f9f9;
}

.option-icon {
  font-size: 20px;
  width: 40px;
  color: #409eff;
}

.option-info {
  flex: 1;
}

.option-title {
  margin: 0 0 2px 0;
  font-size: 15px;
  color: #333;
}

.option-desc {
  margin: 0;
  font-size: 13px;
  color: #888;
}

.option-desc.completed {
  color: #52c41a;
}

.option-desc.incomplete {
  color: #faad14;
}

.option-arrow {
  color: #ddd;
  font-size: 18px;
}

/* 退出登录按钮 */
.logout-btn {
  width: 100%;
  margin-top: 30px;
  padding: 12px;
  background-color: white;
  border: 1px solid #ff4d4f;
  color: #ff4d4f;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background-color: #fff2f0;
}

/* 提示信息 */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  z-index: 1000;
  animation: toastFade 2s ease-in-out;
}

@keyframes toastFade {
  0% { opacity: 0; top: 10px; }
  10% { opacity: 1; top: 20px; }
  90% { opacity: 1; top: 20px; }
  100% { opacity: 0; top: 10px; }
}

/* 响应式设计 */
@media (max-width: 576px) {
  .avatar-section {
    flex-direction: column;
    text-align: center;
  }

  .avatar-container {
    margin-right: 0;
    margin-bottom: 16px;
  }

  .info-item {
    flex-direction: column;
  }

  .info-label {
    width: 100%;
    margin-bottom: 8px;
  }

  .security-item {
    padding: 12px 16px;
  }

  .option-icon {
    width: 30px;
  }
}
</style>