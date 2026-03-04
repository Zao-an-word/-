<template>
  <div class="message-wrapper" :class="{ 'user-message': isUser, 'ai-message': !isUser }">
    <div class="avatar" v-if="!isUser">
      <img src="@/assets/img/ai_avatar.jpg" alt="AI头像" />
    </div>
    <div class="avatar" v-else>
      <img src="@/assets/img/userProfile.jpg" alt="用户头像" />
    </div>

    <div class="message-content">
      <div class="bubble"
           :class="{ 'user-bubble': isUser, 'ai-bubble': !isUser, 'glowing-border': isHighlighted }"
           @click="onBubbleClick"
      >
        <div class="message-text" v-html="formattedContent"></div>
      </div>
      <div class="timestamp" v-if="timestamp">
        {{ timestamp }}
      </div>
    </div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it'; // 引入 markdown-it 库

const md = new MarkdownIt({
  html: true,          // 允许 HTML 标签
  linkify: true,       // 自动识别链接
  breaks: true         // 换行转换为 <br>
});

export default {
  name: "ChatMessage",
  props: {
    content: {
      type: String,
      required: true
    },
    isUser: {
      type: Boolean,
      default: false
    },
    timestamp: {
      type: String,
      default: ''
    },
    isStreaming: {
      type: Boolean,
      default: true
    },
    isHighlighted: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    formattedContent() {
      // 使用 markdown-it 渲染 Markdown 文本为 HTML
      return md.render(this.content || '');
    }
  },
  methods: {
    onBubbleClick() {
      if(!this.isUser) {
        this.$emit('ai-bubble-clicked',this.content);
      }
    }
  }
};
</script>

<style scoped>
.message-wrapper {
  display: flex;
  margin-bottom: 16px;
  opacity: 0;
  transform: translateY(10px);
  animation: fadeIn 0.3s ease forwards;
  min-width: 300px; /* 设置整个对话项最小宽度 */
  width:100%;
}

@keyframes fadeIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  justify-content: flex-start;
  flex-direction: row-reverse;
}

.ai-message {
  justify-content: flex-start;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  margin: 0 10px;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  max-width: 75%;
}

.bubble {
  padding: 10px 16px;
  border-radius: 18px;
  position: relative;
  line-height: 1.5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2); /* 更柔和的阴影 */
  transition: transform 0.2s;
}

/* 用户消息气泡 */
.user-bubble {
  background: linear-gradient(135deg, #ff6ec4, #7873f5, #4ade80);
  background-size: 400% 400%; /* 扩展背景尺寸以支持动效 */
  animation: gradientFlow 8s ease infinite; /* 应用动画 */
  color: white;
  border-bottom-right-radius: 4px;
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.5); /* 蓝色外发光 */
}

/* AI消息气泡 */
.ai-bubble {
  background: linear-gradient(135deg, #f5f7fa, #fad0fa, #ffc0cb);
  background-size: 400% 400%; /* 扩展背景尺寸以支持动效 */
  animation: gradientFlow 8s ease infinite; /* 应用动画 */
  color: #333;
  border-bottom-left-radius: 4px;
  box-shadow: 0 0 10px rgba(199, 210, 254, 0.4); /* 紫白发光 */
}

/* 悬浮时微微放大 */
.bubble:hover {
  transform: scale(1.03);
}

@keyframes gradientFlow {
  0% {
    background-position: 0 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0 50%;
  }
}

/* 闪烁发光边框效果 */
.glowing-border {
  animation: glowing 2s infinite;
}

@keyframes glowing {
  0% {
    box-shadow: 0 0 5px rgba(255, 255, 255, 0.7),
    0 0 10px rgba(255, 255, 255, 0.5),
    0 0 15px rgba(255, 255, 255, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.5);
  }
  50% {
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.9),
    0 0 20px rgba(255, 255, 255, 0.7),
    0 0 30px rgba(255, 255, 255, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.8);
  }
  100% {
    box-shadow: 0 0 5px rgba(255, 255, 255, 0.7),
    0 0 10px rgba(255, 255, 255, 0.5),
    0 0 15px rgba(255, 255, 255, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.5);
  }
}

.user-bubble.glowing-border {
  animation: gradientFlow 8s ease infinite, glowing-user 2s ease-in-out infinite;
}

@keyframes glowing-user {
  0% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.7),
    0 0 10px rgba(59, 130, 246, 0.5),
    0 0 15px rgba(59, 130, 246, 0.3),
    inset 0 0 1px rgba(59, 130, 246, 0.5);
  }
  50% {
    box-shadow: 0 0 10px rgba(59, 130, 246, 0.9),
    0 0 20px rgba(59, 130, 246, 0.7),
    0 0 30px rgba(59, 130, 246, 0.5),
    inset 0 0 1px rgba(59, 130, 246, 0.8);
  }
  100% {
    box-shadow: 0 0 5px rgba(59, 130, 246, 0.7),
    0 0 10px rgba(59, 130, 246, 0.5),
    0 0 15px rgba(59, 130, 246, 0.3),
    inset 0 0 1px rgba(59, 130, 246, 0.5);
  }
}

.ai-bubble.glowing-border {
  animation: gradientFlow 8s ease infinite, glowing-ai 2s ease-in-out infinite;
}

@keyframes glowing-ai {
  0% {
    box-shadow: 0 0 5px rgba(255, 192, 203, 0.7),
    0 0 10px rgba(255, 182, 193, 0.5),
    0 0 15px rgba(255, 174, 185, 0.3),
    inset 0 0 1px  rgba(255, 192, 203, 0.5);
  }
  50% {
    box-shadow: 0 0 10px rgba(255, 182, 193, 0.9),
    0 0 20px rgba(255, 174, 185, 0.7),
    0 0 30px rgba(255, 160, 122, 0.5),
    inset 0 0 1px rgba(255, 182, 193, 0.8);
  }
  100% {
    box-shadow: 0 0 5px rgba(255, 192, 203, 0.7),
    0 0 10px rgba(255, 182, 193, 0.5),
    0 0 15px rgba(255, 174, 185, 0.3),
    inset 0 0 1px rgba(255, 192, 203, 0.5);
  }
}



.timestamp {
  font-size: 12px;
  color: #888;
  margin-top: 4px;
  text-align: right;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-6px);
  }
}

/* 使用一个deep伪选择器来穿透作用域，
清除markdown格式产生的额外上下边距 */
:deep(.message-text p) {
  margin: 0;
  padding: 0;
}
</style>