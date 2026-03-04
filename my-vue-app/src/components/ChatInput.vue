<template>
  <div class="chat-input-container" :style="styleObject">
    <!-- 上传预览展示区（移至文本框上方） Upload preview area (above the text area) -->
    <div class="upload-preview" v-if="uploadedFiles.length || uploadedImages.length">
      <div class="preview-content">
        <!-- 展示上传的文件 File items -->
        <div class="file-item" v-for="(file, index) in uploadedFiles" :key="index">
          <span>{{ getFileIcon(file.name) }} {{ file.name }}</span>
          <button class="remove-btn" @click="removeFile(index)">❌</button>
        </div>
        <!-- 展示上传的图片缩略图 Image thumbnails -->
        <div class="image-item" v-for="(image, index) in uploadedImages" :key="`img-${index}`">
          <div class="image-preview-wrapper">
            <img :src="image.url" alt="uploaded" class="image-thumbnail" />
          </div>
          <button class="remove-btn" @click="removeImage(index)">❌</button>
        </div>
      </div>
    </div>

    <!-- 输入行：上传按钮，文本框，发送按钮 Input row: upload buttons, textarea, send button -->
    <div class="input-row">
      <!-- 左侧上传按钮区域（横向排列） Upload buttons on the left -->
      <div class="upload-buttons-horizontal">
        <button class="upload-btn-transparent" @click="triggerFileUpload">📁</button>
        <button class="upload-btn-transparent" @click="triggerImageUpload">🖼️</button>
        <input type="file" ref="fileInput" style="display: none" @change="handleFileSelected" />
        <input type="file" ref="imageInput" accept="image/*" style="display: none" @change="handleImageSelected" />
      </div>

      <!-- 文本输入框 Textarea -->
      <textarea
          v-model="localText"
          class="chat-textarea"
          :rows="rows"
          :placeholder="placeholder"
          @keydown.enter.exact="handleEnter"
          @keydown.shift.enter="handleShiftEnter"
          :disabled="loading"
      ></textarea>

      <!-- 发送按钮 Send button -->
      <button class="send-btn" :disabled="loading || !localText.trim()" @click="handleSend">
        {{ loading ? '发送中...' : '发送' }}
        <span class="ripple"></span>
      </button>
    </div>
  </div>
</template>

<script>
/**
 * 聊天输入组件
 * 提供文本输入和发送功能，支持Enter和Shift+Enter不同行为
 */
import axios from 'axios';
export default {
  name: "ChatInput",
  /**
   * 组件属性
   * @property {string} modelValue - 输入框的当前值
   * @property {boolean} loading - 是否处于加载状态
   * @property {string} placeholder - 输入框占位符文本
   * @property {number} leftOffset - 左侧偏移量用于定位
   * @property {number} width - 组件宽度用于布局计算
   */
  props: {
    modelValue: String,
    loading: Boolean,
    placeholder: {
      type: String,
      default: "Enter 发送 / Shift+Enter 换行",
    },
    leftOffset: Number,
    width: Number,
    },
  data() {
    return {
      localText: this.modelValue || "",
      uploadedFiles: [],                // 存储上传的文件
      uploadedImages: [],               // 存储上传的图片（含预览地址）
      fileIds:[],
    };
  },
  /**
   * 计算属性
   * @property {Object} styleObject - 动态计算的样式对象，用于组件定位和外观
   * @property {number} rows - 动态计算的文本区域行数，最大为5行
   */
  computed: {
    styleObject() {
      return {
        position: 'fixed',
        bottom: '20px',
        left: `calc(${this.leftOffset}px + ${this.width * 0.2}px)`,
        width: `${this.width * 0.7}px`,
        display: 'flex',
        flexDirection: 'column',      // 使预览区在上方 make preview above
        backdropFilter: 'blur(12px)',
        borderRadius: '16px',
        boxShadow: '0 0 20px rgba(0,0,0,0.2)',
        padding: '10px',
        zIndex: 9999,
        background: 'linear-gradient(to right, rgba(255, 154, 158, 0.1), rgba(250, 208, 196, 0.1))',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        animation: 'fadeInUp 0.5s ease',
      };
    },
    rows() {
      return Math.min(5, this.localText.split('\n').length || 1);
    },
  },
  /**
   * 监听器
   * 监听localText变化以更新父组件
   * 监听modelValue变化以同步本地值
   */
  watch: {
    localText(val) {
      this.$emit('update:modelValue', val);
      this.reportHeight();
      console.log(this.$el.offsetHeight);
    },
    modelValue(val) {
      if (val !== this.localText) this.localText = val;
    },
  },
  /**
   * 方法集合
   * @method handleEnter - 处理Enter键按下事件
   * @param {Event} e - 键盘事件对象
   * @method handleShiftEnter - 处理Shift+Enter键按下事件（预留）
   * @method handleSend - 处理发送按钮点击事件
   */
  methods: {
    // 上传文件到后端
    async uploadToServer(file) {
      try {
        const formData = new FormData();
        formData.append('files', file);
        
        // 如果有活跃对话ID，可以添加进来（根据实际情况调整）
        // formData.append('chat_id', this.currentChatId);
        
        const response = await axios.post('/api/upload-files', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            // 上传进度显示逻辑
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            console.log(`上传进度: ${percentCompleted}%`);
          }
        });
        
        if (response.data.results && response.data.results.length > 0) {
          const result = response.data.results[0];
          if (result.status === 'success' && result.file_id) {
            // 保存文件ID用于后续查询
            this.fileIds.push(result.file_id);
            return { success: true, fileId: result.file_id };
          } else {
            console.error('文件上传失败:', result.reason);
            return { success: false, error: result.reason };
          }
        }
      } catch (error) {
        console.error('上传请求失败:', error.response?.data || error.message);
        return { 
          success: false, 
          error: error.response?.data?.detail || '上传失败，请重试' 
        };
      }
    },
    handleEnter(e) {
      if (this.localText.trim()||this.fileIds.length > 0) {
        e.preventDefault();
        this.handleSend();
      }
    },
    handleShiftEnter() {},
    // 发送消息方法，附有文件ID传递
    async handleSend() {
      const text = this.localText.trim();
      if (!text && this.fileIds.length === 0) return;
      
      // 通知父组件开始加载
      this.$emit('update:loading', true);
      console.log('发送数据:', { question: text, file_ids: this.fileIds }); // 新增日志
      try {
        // 直接将用户输入和文件ID传递给主界面，由主界面处理后续逻辑
        this.$emit('send-data', {
          question: text,
          file_ids: this.fileIds
        });
        
        // 清空输入和文件数据
        this.localText = '';
        this.uploadedFiles = [];
        this.uploadedImages = [];
        this.fileIds = [];
        
      } finally {
        this.$emit('update:loading', false);
      }
    },
    reportHeight() {
      this.$nextTick(() => {
        const height = this.$el.offsetHeight;
        this.$emit('height-change', height);
      });
    },

    // 新增上传逻辑
    triggerFileUpload() {
      this.$refs.fileInput.click();
    },
    triggerImageUpload() {
      this.$refs.imageInput.click();
    },
    // 文件处理方法，添加上传到服务器的逻辑
    async handleFileSelected(event) {
      const file = event.target.files[0];
      if (file) {
        // 先添加到本地预览
        this.uploadedFiles.push(file);
        this.reportHeight();
        
        // 再上传到服务器
        const result = await this.uploadToServer(file, false);
        if (!result.success) {
          // 上传失败，从预览中移除
          const index = this.uploadedFiles.indexOf(file);
          if (index > -1) {
            this.uploadedFiles.splice(index, 1);
          }
          alert(result.error);
        }
      }
      // 重置input，允许重复选择同一文件
      event.target.value = '';
    },
    // 图片处理方法，添加上传到服务器的逻辑
    async handleImageSelected(event) {
      const file = event.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          // 先添加到本地预览
          const imageObj = { file, url: e.target.result };
          this.uploadedImages.push(imageObj);
          this.reportHeight();
          
          // 再上传到服务器
          const result = await this.uploadToServer(file, true);
          if (!result.success) {
            // 上传失败，从预览中移除
            const index = this.uploadedImages.indexOf(imageObj);
            if (index > -1) {
              this.uploadedImages.splice(index, 1);
            }
            alert(result.error);
          }
        };
        reader.readAsDataURL(file);
      }
      // 重置input，允许重复选择同一文件
      event.target.value = '';
    },
    // 移除文件
    removeFile(index) {
      // 找到对应的文件ID并移除（修正：移除未使用的id参数）
      const fileIndex = this.fileIds.findIndex((_, idx) => idx === index);
      if (fileIndex > -1) {
        this.fileIds.splice(fileIndex, 1);
      }
      
      this.uploadedFiles.splice(index, 1);
      this.reportHeight();
    },
    // 移除图片方法，同步移除fileIds
    removeImage(index) {
      // 找到对应的文件ID并移除（修正：移除未使用的id参数）
      const fileIndex = this.fileIds.findIndex((_, idx) => idx === index);
      if (fileIndex > -1) {
        this.fileIds.splice(fileIndex, 1);
      }
      
      this.uploadedImages.splice(index, 1);
      this.reportHeight();
    },

    getFileIcon(fileName) {
      const ext = fileName.split('.').pop().toLowerCase(); // 提取文件扩展名
      switch (ext) {
        case 'pdf': return '📄';        // PDF 文件
        case 'doc':
        case 'docx': return '📝';      // Word 文档
        case 'xls':
        case 'xlsx': return '📊';      // Excel 文件
        case 'ppt':
        case 'pptx': return '📽️';     // PPT 文件
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
        case 'bmp': return '🖼️';      // 图片
        case 'zip':
        case 'rar': return '🗜️';      // 压缩包
        case 'txt': return '📃';       // 纯文本
        case 'mp4':
        case 'mov':
        case 'avi': return '🎞️';     // 视频
        case 'mp3':
        case 'wav': return '🎵';      // 音频
        default: return '📁';         // 其他文件
      }
    },
  },
  mounted() {
    this.reportHeight();
  },
};
</script>

<style scoped>
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-input-container {
  display: flex;
  flex-direction: column;
}

/* 上传预览区 Upload preview area */
.upload-preview {
  width: 100%;
  margin-bottom: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}
.preview-content {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}
.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 12px; /* 缩小文件名称字体 smaller file name */
}
.file-name {
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.image-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
}
.image-preview-wrapper {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}
.image-thumbnail:hover { transform: scale(1.05); }
.remove-btn {
  background: transparent;
  border: none;
  color: #ff4d4f;
  cursor: pointer;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: background 0.2s;
}
.remove-btn:hover { background: rgba(255, 77, 79, 0.1); }

/* 输入行布局 Input row layout */
.input-row {
  display: flex;
  align-items: stretch;
  gap: 10px;
}
.upload-buttons-horizontal {
  display: flex;
  align-items: center;
  margin: 40px 0 0;
}
.upload-btn-transparent {
  background: transparent;
  border: none;
  font-size: 16px;
  padding: 5px;
  margin-right: 4px;
  cursor: pointer;
  transition: transform 0.2s ease, color 0.2s ease;
}
.upload-btn-transparent:hover {
  transform: scale(1.2);
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.1);
}
.chat-textarea {
  flex-grow: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 16px;
  padding: 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  min-height: 48px;
  max-height: 150px;
  overflow-y: auto;
  line-height: 1.5;
  transition: box-shadow 0.3s ease;
}
.chat-textarea:focus { box-shadow: 0 0 8px #00ffe1; }
.send-btn {
  margin-right: 0;
  position: relative;
  background: linear-gradient(135deg, #98f1db, #2fd5dc);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 10px 20px;
  font-weight: bold;
  cursor: pointer;
  overflow: hidden;
  transition: background 0.3s ease, transform 0.2s;
}
.send-btn:hover { transform: scale(1.05); }
.send-btn:disabled { background: #9e9e9e; cursor: not-allowed; }
/* 鼠标点击波纹效果 */
.send-btn .ripple {
  content: "";
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  width: 100px;
  height: 100px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0);
  animation: ripple-animation 0.6s linear;
  pointer-events: none;
}
@keyframes ripple-animation { to { transform: translate(-50%, -50%) scale(2.5); opacity: 0; } }
</style>
