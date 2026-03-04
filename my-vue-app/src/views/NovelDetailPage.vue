<template>
  <!-- 背景图层 -->
  <div class="background-image"></div>

  <div class="novel-detail">
    <div v-if="loading" class="loading">正在加载小说内容...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <button class="back-btn" @click="goBack">← 返回首页</button>

      <!-- 新增：封面和标题区域布局 -->
      <div class="header-section">
        <div class="cover-container">
          <img :src="currentCoverUrl" alt="小说封面" class="cover" />
          
          <!-- 上传封面按钮（仅作者可见） -->
          <div v-if="isAuthor" class="upload-container">
            <label class="upload-btn">
              更换封面
              <input 
                type="file" 
                accept="image/jpeg, image/png, image/gif" 
                class="file-input"
                @change="handleFileChange"
              >
            </label>
          </div>
        </div>
        
        <div class="title-section">
          <h1 class="title">{{ novel.title }}</h1>
          <p class="author">作者：{{ novel.author_name || '未知' }}</p>
          
          <!-- 标签展示 -->
          <div class="tags-container" v-if="novel.tags && novel.tags.length">
            <span 
              v-for="tag in parsedTags" 
              :key="tag" 
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>

      <!-- 上传进度和状态提示 -->
      <div v-if="uploading" class="upload-progress">
        <div class="progress-bar" :style="{ width: uploadProgress + '%' }"></div>
        <span class="progress-text">{{ uploadProgress }}%</span>
      </div>
      
      <div v-if="uploadMessage" class="upload-message" :class="{ success: uploadSuccess }">
        {{ uploadMessage }}
      </div>

      <p class="intro">{{ novel.introduction }}</p>
      <div class="content">{{ novel.content }}</div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      novel: null,
      loading: true,
      error: null,
      isAuthor: false,         // 是否为小说作者
      currentCoverUrl: '',     // 当前封面URL
      uploading: false,        // 上传状态
      uploadProgress: 0,       // 上传进度
      uploadMessage: '',       // 上传提示信息
      uploadSuccess: false     // 上传是否成功
    };
  },
  computed: {
    resolvedCover() {
      return this.novel && this.novel.cover_url
          ? this.novel.cover_url
          : require('@/assets/img/cover1.jpg');
    },
    // 解析标签（支持多种分隔符）
    parsedTags() {
      if (!this.novel || !this.novel.tags) return [];
      return this.novel.tags.split(/[ ,，、|;；]+/).filter(tag => tag.trim());
    }
  },
  async mounted() {
    const id = this.$route.params.id;

    if (!id) {
      this.error = "URL 参数错误：缺少小说 ID";
      this.loading = false;
      return;
    }

    try {
      // 获取小说详情
      const res = await axios.get(`http://127.0.0.1:8000/api/novels/${id}`);
      this.novel = res.data;
      this.currentCoverUrl = this.resolvedCover;
      
      // 检查当前用户是否为作者
      await this.checkAuthorStatus();
    } catch (err) {
      this.error = "加载失败：" + (err.response?.data?.detail || err.message);
      console.error(err);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    goBack() {
      this.$router.push('/platform');
    },
    
    // 检查当前用户是否为小说作者
    async checkAuthorStatus() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          this.isAuthor = false;
          return;
        }
        
        // 获取当前用户信息
        const userRes = await axios.get('/api/me', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        // 验证作者身份（假设小说数据包含user_id字段）
        this.isAuthor = this.novel.user_id === userRes.data.id;
      } catch (err) {
        console.error('验证作者身份失败:', err);
        this.isAuthor = false;
      }
    },
    
    // 处理文件选择
    handleFileChange(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // 验证文件类型
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
      if (!allowedTypes.includes(file.type)) {
        this.showUploadMessage('只允许上传JPG、PNG、GIF格式的图片', false);
        return;
      }
      
      // 验证文件大小（限制10MB）
      if (file.size > 10 * 1024 * 1024) {
        this.showUploadMessage('文件大小不能超过10MB', false);
        return;
      }
      
      // 预览图片并上传
      const reader = new FileReader();
      reader.onload = (e) => {
        this.currentCoverUrl = e.target.result; // 临时预览
        this.uploadCoverImage(file);
      };
      reader.readAsDataURL(file);
      
      // 清空文件输入，允许重复选择同一文件
      event.target.value = '';
    },
    
    async uploadCoverImage(file) {
      this.uploading = true;
      this.uploadProgress = 0;
      this.uploadMessage = '';
      
      try {
        const formData = new FormData();
        formData.append('file', file); // 只需要传递文件
        
        const token = localStorage.getItem('token');
        // 在URL中添加novel_id作为查询参数
        const response = await axios.post(
          `/api/novels/cover?novel_id=${this.novel.id}`,
          formData,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: (progressEvent) => {
              this.uploadProgress = Math.round(
                (progressEvent.loaded / progressEvent.total) * 100
              );
            }
          }
        );
        
        // 上传成功处理
        this.novel.cover_url = response.data.cover_url;
        this.currentCoverUrl = response.data.cover_url;
        this.showUploadMessage('封面上传成功', true);
      } catch (err) {
        // 上传失败处理，恢复原封面
        this.currentCoverUrl = this.resolvedCover;
        this.showUploadMessage(
          // 处理详细错误信息（如果是数组的话）
          err.response?.data?.detail?.[0]?.msg || 
          err.response?.data?.detail || 
          '封面上传失败，请重试', 
          false
        );
        console.error('封面上传失败:', err);
      } finally {
        this.uploading = false;
      }
    },
    
    // 显示上传提示信息
    showUploadMessage(message, isSuccess) {
      this.uploadMessage = message;
      this.uploadSuccess = isSuccess;
      
      // 3秒后自动清除提示
      setTimeout(() => {
        this.uploadMessage = '';
      }, 3000);
    }
  },
};
</script>

<style scoped>
/* 背景图样式 */
.background-image {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-image: url('@/assets/img/detail_bk.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: -1;
}

.novel-detail {
  padding: 20px;
  max-width: 800px;
  margin: auto;
  font-family: "Microsoft YaHei", sans-serif;
  z-index: 1;
}

.loading {
  font-size: 18px;
  color: #999;
  text-align: center;
}

.error {
  color: red;
  text-align: center;
}

.back-btn {
  background: none;
  border: none;
  color: #007bff;
  font-size: 16px;
  margin-bottom: 20px;
  cursor: pointer;
}

/* 新增：头部区域布局 */
.header-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.cover-container {
  flex-shrink: 0;
}

.cover {
  width: 200px;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.title-section {
  flex-grow: 1;
}

.title {
  font-size: 28px;
  margin-bottom: 10px;
}

.author {
  color: #666;
  margin: 0 0 15px 0;
  font-size: 16px;
}

/* 标签样式 */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;
}

.tag {
  background-color: #f0f7ff;
  color: #0066cc;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

/* 上传按钮样式 */
.upload-container {
  text-align: center;
}

.upload-btn {
  display: inline-block;
  padding: 6px 12px;
  background-color: #007bff;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-btn:hover {
  background-color: #0056b3;
}

.file-input {
  display: none;
}

/* 上传进度样式 */
.upload-progress {
  height: 8px;
  background-color: #eee;
  border-radius: 4px;
  margin: 10px 0;
  overflow: hidden;
  position: relative;
}

.progress-bar {
  height: 100%;
  background-color: #28a745;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  right: 5px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 12px;
  color: #666;
}

/* 上传提示信息 */
.upload-message {
  padding: 8px 12px;
  border-radius: 4px;
  margin: 0 0 15px 0;
  font-size: 14px;
}

.upload-message.success {
  background-color: #d4edda;
  color: #155724;
}

.upload-message:not(.success) {
  background-color: #f8d7da;
  color: #721c24;
}

.intro {
  font-style: italic;
  color: #555;
  margin-bottom: 20px;
  line-height: 1.6;
}

.content {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 16px;
}

/* 响应式调整 */
@media (max-width: 600px) {
  .header-section {
    flex-direction: column;
  }
  
  .cover {
    max-width: 100%;
  }
}
</style>
