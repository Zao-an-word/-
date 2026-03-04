<template>
  <div class="bind-phone-container">
    <!-- 顶部导航栏 -->
    <div class="page-header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <h1 class="page-title">{{ isBinding ? '绑定手机号' : '修改手机号' }}</h1>
    </div>

    <!-- 表单主体 -->
    <div class="form-card">
      <!-- 手机号输入框 -->
      <div class="form-item">
        <label class="form-label">手机号码</label>
        <div class="input-group">
          <input
            type="tel"
            v-model="phone"
            class="form-input"
            placeholder="请输入11位手机号码"
            maxlength="11"
            @input="handlePhoneInput"
            :disabled="isSendingCode || isSubmitting"
          >
        </div>
        <p class="error-message" v-if="showPhoneError">{{ phoneErrorMsg }}</p>
      </div>

      <!-- 验证码输入框 + 发送按钮 -->
      <div class="form-item">
        <label class="form-label">验证码</label>
        <div class="input-group code-group">
          <input
            type="text"
            v-model="code"
            class="form-input code-input"
            placeholder="请输入6位验证码"
            maxlength="6"
            :disabled="isSubmitting"
          >
          <button
            class="send-code-btn"
            @click="sendVerificationCode"
            :disabled="!canSendCode || isSendingCode || isSubmitting"
          >
            {{ isSendingCode ? `重新发送(${countdown}s)` : '发送验证码' }}
          </button>
        </div>
        <p class="error-message" v-if="showCodeError">{{ codeErrorMsg }}</p>
      </div>

      <!-- 提交按钮 -->
      <button
        class="submit-btn"
        @click="submitForm"
        :disabled="isSubmitting || !isFormValid"
      >
        {{ isSubmitting ? '提交中...' : (isBinding ? '确认绑定' : '确认修改') }}
      </button>

      <!-- 安全提示 -->
      <p class="safety-tip">
        我们将发送验证码至您的手机，仅用于身份验证
      </p>
    </div>
  </div>

  <!-- 加载中遮罩 -->
  <div class="loading-overlay" v-if="isSubmitting || isSendingCode">
    <div class="loading-spinner"></div>
  </div>

  <!-- 操作结果提示 -->
  <div class="toast" v-if="showToast">
    {{ toastMessage }}
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'BindPhonePage',
  data() {
    return {
      // 表单数据
      phone: '', // 手机号
      code: '', // 验证码
      // 状态控制
      isBinding: true, // 区分"绑定"和"修改"模式（根据当前是否有手机号判断）
      isSendingCode: false, // 是否正在发送验证码
      isSubmitting: false, // 是否正在提交
      countdown: 60, // 验证码倒计时
      countdownTimer: null, // 倒计时定时器
      // 错误提示
      showPhoneError: false,
      phoneErrorMsg: '',
      showCodeError: false,
      codeErrorMsg: '',
      // 结果提示
      showToast: false,
      toastMessage: ''
    };
  },
  computed: {
    // 手机号格式是否正确
    isPhoneValid() {
      return /^1[3-9]\d{9}$/.test(this.phone);
    },
    // 验证码是否填写
    isCodeValid() {
      return this.code.length === 6;
    },
    // 表单是否可提交
    isFormValid() {
      return this.isPhoneValid && this.isCodeValid;
    },
    // 是否可以发送验证码
    canSendCode() {
      return this.isPhoneValid && !this.isSendingCode;
    }
  },
  async created() {
    // 初始化时判断当前是否已绑定手机号（从用户信息获取）
    await this.checkCurrentPhone();
  },
  beforeUnmount() {
    // 清除定时器
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
    }
  },
  methods: {
    // 返回上一页
    goBack() {
      this.$router.go(-1);
    },

    // 检查当前是否已绑定手机号
    async checkCurrentPhone() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('/api/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const currentPhone = response.data.phone;
        // 如果已有手机号，进入"修改"模式并预填（可编辑）
        if (currentPhone && currentPhone !== '未绑定') {
          this.isBinding = false;
          this.phone = currentPhone;
        }
      } catch (error) {
        console.error('获取当前手机号失败:', error);
        this.showToastMessage('加载失败，请重试');
      }
    },

    // 手机号输入处理（过滤非数字字符）
    handlePhoneInput(e) {
      // 只保留数字
      this.phone = e.target.value.replace(/\D/g, '');
      // 实时验证格式
      if (this.phone) {
        this.validatePhone();
      } else {
        this.showPhoneError = false;
      }
    },

    // 验证手机号格式
    validatePhone() {
      if (!this.phone) {
        this.showPhoneError = true;
        this.phoneErrorMsg = '请输入手机号码';
        return false;
      }
      if (!/^1[3-9]\d{9}$/.test(this.phone)) {
        this.showPhoneError = true;
        this.phoneErrorMsg = '请输入有效的11位手机号';
        return false;
      }
      this.showPhoneError = false;
      return true;
    },

    // 发送验证码
    async sendVerificationCode() {
      // 前置验证
      if (!this.validatePhone()) return;

      try {
        this.isSendingCode = true;
        const token = localStorage.getItem('token');
        // 调用发送验证码接口
        await axios.post('/api/send-sms', {
          phone: this.phone,
          type: this.isBinding ? 'bind' : 'change' // 区分绑定/修改类型
        }, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        this.showToastMessage('验证码已发送，请注意查收');
        this.startCountdown(); // 启动倒计时
      } catch (error) {
        console.error('发送验证码失败:', error);
        const errorMsg = error.response?.data?.detail || '发送验证码失败，请重试';
        this.showPhoneError = true;
        this.phoneErrorMsg = errorMsg;
      } finally {
        // 仅在失败时重置发送状态（成功时由倒计时控制）
        if (!this.countdownTimer) {
          this.isSendingCode = false;
        }
      }
    },

    // 验证码倒计时
    startCountdown() {
      this.countdown = 60;
      this.isSendingCode = true;
      // 清除已有定时器
      if (this.countdownTimer) {
        clearInterval(this.countdownTimer);
      }
      // 启动新定时器
      this.countdownTimer = setInterval(() => {
        this.countdown--;
        if (this.countdown <= 0) {
          clearInterval(this.countdownTimer);
          this.countdownTimer = null;
          this.isSendingCode = false;
        }
      }, 1000);
    },

    // 提交表单（绑定/修改手机号）
    async submitForm() {
      // 前置验证
      if (!this.validatePhone()) return;
      if (this.code.length !== 6) {
        this.showCodeError = true;
        this.codeErrorMsg = '请输入6位验证码';
        return;
      }

      try {
        this.isSubmitting = true;
        const token = localStorage.getItem('token');
        const apiUrl = this.isBinding ? '/api/bind-phone' : '/api/change-phone';

        // 调用绑定/修改接口
        await axios.post(apiUrl, {
          phone: this.phone,
          verification_code: this.code
        }, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        // 提交成功
        const successMsg = this.isBinding ? '手机号绑定成功' : '手机号修改成功';
        this.showToastMessage(successMsg);
        // 延迟返回上一页，确保用户看到提示
        setTimeout(() => {
          this.$router.go(-1);
        }, 1500);
      } catch (error) {
        console.error('提交失败:', error);
        const errorMsg = error.response?.data?.detail || '操作失败，请重试';
        this.showCodeError = true;
        this.codeErrorMsg = errorMsg;
      } finally {
        this.isSubmitting = false;
      }
    },

    // 显示提示消息
    showToastMessage(msg) {
      this.toastMessage = msg;
      this.showToast = true;
      setTimeout(() => {
        this.showToast = false;
      }, 3000);
    }
  }
};
</script>

<style scoped>
/* 基础样式 */
.bind-phone-container {
  padding: 20px;
  max-width: 500px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 头部导航 */
.page-header {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.back-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 5px 10px;
  color: #333;
}

.page-title {
  flex: 1;
  text-align: center;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #333;
}

/* 表单卡片 */
.form-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 30px 20px;
  margin-top: 30px;
}

/* 表单项目 */
.form-item {
  margin-bottom: 25px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.input-group {
  position: relative;
}

.form-input {
  width: 100%;
  height: 48px;
  padding: 0 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 验证码行特殊样式 */
.code-group {
  display: flex;
  gap: 10px;
}

.code-input {
  flex: 1;
}

.send-code-btn {
  width: 120px;
  height: 48px;
  border: none;
  border-radius: 8px;
  background: #409eff;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s;
}

.send-code-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 错误提示 */
.error-message {
  margin: 5px 0 0;
  font-size: 12px;
  color: #f56c6c;
  height: 16px;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 50px;
  border: none;
  border-radius: 8px;
  background: #409eff;
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 15px;
}

.submit-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.submit-btn:not(:disabled):hover {
  background: #66b1ff;
}

/* 安全提示 */
.safety-tip {
  margin-top: 20px;
  font-size: 12px;
  color: #999;
  text-align: center;
}

/* 加载遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 提示框 */
.toast {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 12px 20px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
  font-size: 14px;
  z-index: 1001;
  animation: fade 0.3s;
}

@keyframes fade {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>