<template>
  <div
      :style="wrapperStyle"
      v-show="visible"
      class="text-editor"
      @mousemove="onDrag"
      @mouseup="stopDragging"
      @mouseleave="stopDragging"
  >
    <!-- 编辑器内容区域 -->
    <div class="editor-content" :style="contentStyle">
      <!-- 顶部按钮栏 -->
      <div class="editor-header">
        <button class="toggle-btn" @click="togglePreview">
          {{ isPreview ? '📝 编辑' : '👁️ 预览' }}
        </button>
        <button class="close-btn" @click="close">✖</button>
      </div>

      <!-- 编辑区或预览区 -->
      <div v-if="!isPreview" style="flex: 1">
        <textarea v-model="editorText" :style="textareaStyle" class="editor-textarea"></textarea>
      </div>
      <div v-else class="preview-area" v-html="renderedMarkdown"></div>

      <!-- 底部功能栏 -->
      <div class="editor-footer">
        <button class="upload-btn" @click="handleUpload">⬆️ 上传</button>
        <button class="copy-btn" @click="copyText">📋 复制</button>
      </div>

    </div>
    <!-- 上传弹窗（默认隐藏） -->
    <div v-if="showUploadModal" class="upload-modal">
      <div class="modal-content">
        <h3>上传小说</h3>
        <input
          type="text"
          v-model="novelTitle"
          placeholder="请输入小说标题"
          class="novel-title-input"
        />
        <div class="modal-buttons">
          <button @click="confirmUpload">确认上传</button>
          <button @click="showUploadModal = false">取消</button>
        </div>
      </div>
    </div>

    <!-- 拖动条 -->
    <div class="resize-handle" @mousedown="startDragging"></div>

    <!-- 拖动遮罩层 -->
    <div v-if="isDragging" class="fullscreen-mask" @mousemove="onDrag" @mouseup="stopDragging"></div>
  </div>
</template>

<script>
import {marked} from 'marked'
import axios from 'axios';
export default {
  name: "TextEditor",
  props: {
    width: { type: String, default: "400px" }, // 初始宽度
    zIndex: { type: Number, default: 1001 },   // 层级
    top: { type: String, default: "60px" },    // 顶部偏移
    right: { type: String, default: "0px" },  // 右侧偏移
    initialText: { type: String, default: "" } // 初始文本
  },
  data() {
    return {
      visible: false,
      currentWidth: parseInt(this.width),
      isDragging: false,
      startX: 0,
      maxWidth: 0,

      editorText: this.initialText,
      // 优化：使用单独拖动宽度状态，避免触发响应式更新
      dragWidth: parseInt(this.width),
      // 优化：存储元素引用
      resizeHandle: null,
      textarea: null,
      isPreview: false,       // 是否为预览模式
      showUploadModal: false, // 是否显示上传弹窗
      novelTitle: '',         // 小说标题
    };
  },
  computed: {
    wrapperStyle() {
      return {
        position: "fixed",
        top: this.top,
        right: this.right,
        // 优化：根据是否拖动使用不同的宽度值
        width: `${this.isDragging ? this.dragWidth : this.currentWidth}px`,
        zIndex: this.zIndex,
        display: "flex",
        flexDirection: "row-reverse",
        borderRadius: "16px",
        overflow: "hidden",
        boxShadow: "0 8px 24px rgba(0, 0, 0, 0.15)",
        backgroundColor: "transparent",
        // 优化：添加过渡效果
        transition: this.isDragging ? 'none' : 'width 0.1s ease-out'
      };
    },
    contentStyle() {
      return {
        flex: 1,
        position: "relative",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        backgroundImage: `url(${require('@/assets/img/text_editor_bk.png')})`, // ✅ 背景图
        backgroundRepeat: "no-repeat",
        backgroundPosition: "left center", // 靠左居中对齐
        backgroundSize: "auto 100%",       // 高度自适应

        // 磨砂玻璃样式
        backgroundColor: "rgba(255, 255, 255, 0.2)",
        backdropFilter: "blur(10px)",
        WebkitBackdropFilter: "blur(10px)",
        border: "1px solid rgba(255, 255, 255, 0.1)",
        borderRadius: "8px",

        transition: "border 0.2s ease, box-shadow 0.2s ease"
      };
    },
    textareaStyle() {
      return {
        flex: 1,
        width: "100%",
        height: "100%",
        border: "none",
        padding: "12px",
        fontSize: "14px",
        fontFamily: "monospace",
        boxSizing: "border-box",
        resize: "none",
      };
    },

    renderedMarkdown() {
      return marked.parse(this.editorText); // 使用 marked 渲染 markdown 为 HTML
    }
  },
  mounted() {
    this.maxWidth = 2 * window.innerWidth / 5;
    window.addEventListener("resize", this.updateMaxWidth);
    // 优化：缓存DOM元素引用
    this.resizeHandle = this.$el.querySelector('.resize-handle');
    this.textarea = this.$el.querySelector('.editor-textarea');
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.updateMaxWidth);
  },

  watch: {
    currentWidth(newWidth) {
      this.$emit('width-changed', newWidth);
    }
  },
  methods: {
    
    updateMaxWidth() {
      this.maxWidth = window.innerWidth / 2;
      if (this.currentWidth > this.maxWidth) {
        this.currentWidth = this.maxWidth;
      }
    },
    startDragging(e) {
      // 优化：阻止事件冒泡和默认行为
      e.preventDefault();
      e.stopPropagation();

      this.isDragging = true;
      this.startX = e.clientX;
      this.dragWidth = this.currentWidth;

      // 优化：拖动时禁用文本选择和指针事件
      document.body.style.userSelect = 'none';
      document.body.style.pointerEvents = 'none';

      // 优化：拖动时临时禁用文本框的事件
      if (this.textarea) {
        this.textarea.style.pointerEvents = 'none';
      }

      // 优化：提高拖动条的z-index，确保交互顺畅
      if (this.resizeHandle) {
        this.resizeHandle.style.zIndex = 10000;
      }
    },
    onDrag(e) {
      if (!this.isDragging) return;

      const delta = this.startX - e.clientX;
      this.startX = e.clientX;

      // 直接更新dragWidth，不使用requestAnimationFrame
      this.dragWidth = Math.max(200, Math.min(this.dragWidth + delta, this.maxWidth));
      // 实时触发宽度变化事件
      this.$emit('width-changed', this.dragWidth);
    },
    stopDragging() {
      if (!this.isDragging) return;

      this.isDragging = false;
      // 将拖动宽度应用到实际宽度
      this.currentWidth = this.dragWidth;
      this.$emit('width-changed', this.currentWidth);

      // 恢复样式
      document.body.style.userSelect = '';
      document.body.style.pointerEvents = '';

      if (this.textarea) {
        this.textarea.style.pointerEvents = '';
      }

      if (this.resizeHandle) {
        this.resizeHandle.style.zIndex = '';
      }
    },
    open(text) {
      this.editorText = text;
      this.visible = true;
      this.$emit('opened');
    },
    close() {
      // 重置宽度
      this.currentWidth = 400;
      this.visible = false;
      this.$emit('closed');
    },
    copyText() {
      navigator.clipboard.writeText(this.editorText).then(() => {
      });
    },

    togglePreview() {
      this.isPreview = !this.isPreview;
    },

    // 点击上传按钮显示弹窗
    handleUpload() {
      if (!this.editorText.trim()) {
        alert('请先输入小说内容');
        return;
      }
      this.showUploadModal = true; // 显示弹窗让用户输入标题
      this.novelTitle = ''; // 重置标题输入框
    },
    // 确认上传
    async confirmUpload() {
      if (!this.novelTitle.trim()) {
        alert('请输入小说标题');
        return;
      }

      try {
        // 1. 获取上传所需数据
        const novelContent = this.editorText; // 编辑器中的小说内容
        const token = localStorage.getItem('token'); // 获取登录令牌（用于认证）
        const tags = this.$parent.selectedTags.map(tag => tag.label).join(','); // 从主界面获取选中的标签
        const requestData = {
          novel_data: {  // 对应后端的 novel_data: NovelCreate
            title: this.novelTitle,
            status: 0,
            cover_url: ''
          },
          upload_params: {  // 对应后端的 upload_params: NovelUploadParams
            prompt: novelContent,
            prompt_tags: tags
          }
        };
        // 2. 调用后端/novels接口上传
        const response = await axios.post(
          '/api/novels',
          requestData,
          {
            headers: {
              'Authorization': `Bearer ${token}`, // 携带认证令牌
              'Content-Type': 'application/json'
            }
          }
        );

        // 3. 上传成功处理
        alert('小说上传成功！');
        this.showUploadModal = false; // 关闭弹窗
        console.log('上传结果:', response.data);

      } catch (error) {
        // 4. 错误处理
        console.error('小说上传失败:', error.response?.data || error.message);
        alert(`上传失败: ${error.response?.data?.detail || '网络错误，请重试'}`);
      }
    },
    watch: {
      currentWidth(newWidth) {
        this.$emit('width-changed', newWidth);
      }
    }
  },
};
</script>

<style scoped>
.text-editor {
  /* 优化：调整过渡效果 */
  transition: width 0.1s ease-out;
  height: calc(100vh - 60px);
  min-height: 300px;
}

/* 文本框样式 */
.editor-textarea {
  flex: 1;
  width: 100%;
  height: 100%;
  padding: 12px;
  font-size: 14px;
  font-family: monospace;
  box-sizing: border-box;
  resize: none;

  background-color: rgba(255, 255, 255, 0.55);
  border: none;
}

/* 拖动条样式 */
.resize-handle {
  width: 3px;
  cursor: ew-resize;
  background-color: rgba(0, 0, 0, 0.05);
  transition: background-color 0.2s;
  /* 优化：添加绝对定位和高度设置 */
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
}
.resize-handle:hover {
  background-color: rgb(205, 243, 232);
  border-left: 2px solid #bbecb7;
}

/* 遮罩层 */
.fullscreen-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  cursor: ew-resize;
  background-color: transparent;
  pointer-events: all;
}

/* 按钮样式 */
.editor-header {
  display: flex;
  justify-content: flex-end;
  padding: 6px 8px;
  background-color: #ffeef0;
}
.editor-footer {
  display: flex;
  justify-content: space-between; /* 左右两边分布 */
  align-items: center;
  padding: 6px 8px;
  background-color: #f0f0f0;
}
.close-btn,
.copy-btn {
  border: none;
  background-color: rgb(47, 213, 220);
  color: white;
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.2s;
}
.close-btn:hover,
.copy-btn:hover {
  background-color: rgb(146, 221, 237);
}

.preview-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  font-size: 14px;
  line-height: 1.6;
  font-family: 'Segoe UI', sans-serif;
  background-color: rgba(255, 255, 255, 0.5);
  border: none;
}

/* 新增按钮样式 */
.upload-btn,
.toggle-btn {
  margin-right: auto;
  border: none;
  background-color: #a7dff5;
  color: #333;
  border-radius: 6px;
  padding: 4px 10px;
  cursor: pointer;
  font-size: 13px;
  transition: background-color 0.2s;
}
.upload-btn:hover,
.toggle-btn:hover {
  background-color: #87cfe2;
}
/* 上传弹窗样式 */
.upload-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1002; /* 确保在编辑器上方 */
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
}

.modal-content h3 {
  margin-top: 0;
  color: #333;
}

.novel-title-input {
  width: 100%;
  padding: 8px;
  margin: 10px 0 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-buttons button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-buttons button:first-child {
  background: #42b983;
  color: white;
}

.modal-buttons button:last-child {
  background: #f5f5f5;
  color: #333;
}
</style>