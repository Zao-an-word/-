<template>
  <!-- 外层容器 - 整个侧边栏可滚动 -->
  <div
      :style="wrapperStyle"
      v-show="visible"
      class="custom-sidebar"
      @mousemove="onDrag"
      @mouseup="stopDragging"
      @mouseleave="stopDragging"
  >
    <!-- 侧边栏内容容器 -->
    <div class="sidebar-content-wrapper" :style="contentWrapperStyle">
      <!-- 背景图固定层 -->
      <div class="sidebar-background" :style="backgroundStyle">
        <!-- 如果需要显示白色半透明遮罩 -->
        <div
            v-if="useWhiteOverlay"
            class="white-overlay"
        ></div>
      </div>

      <!-- 顶部固定区域（不随滚动） -->
      <div class="sidebar-fixed-top" :style="fixedTopStyle">
        <!-- 固定区域的命名插槽 -->
        <slot name="fixed-content"></slot>
      </div>


      <!-- 滚动容器（包含顶部高度偏移） -->
      <div class="sidebar-scroll-container" :style="scrollContainerStyle">
        <div class="scroll-inner" :style="scrollContentStyle">
          <!-- 顶部高度占位元素 -->
          <div class="fixed-top-placeholder" :style="fixedTopPlaceholderStyle"></div>

          <!-- 插槽内容 -->
          <slot></slot>
        </div>
      </div>
    </div>

    <!-- 🖱️ 拖动条 -->
    <div
        class="resize-handle"
        :class="side"
        @mousedown="startDragging"
    ></div>

    <!-- 遮罩层，仅在拖动中显示 -->
    <div
        v-if="isDragging"
        class="fullscreen-mask"
    ></div>
  </div>
</template>

<script>
export default {
  name: "ResizableSidebar", // 组件名称

  props: {
    // 📍 side：侧边栏位置，"left" 或 "right"
    side: { type: String, default: "left" },

    // 📏 侧边栏宽度
    width: { type: String, default: "250px" },

    // 🎨 背景颜色（没有图片时使用）
    color: { type: String, default: "#f0f0f0" },

    // 🌐 网络背景图
    imageSource: String,

    // 🖼️ 本地 base64 背景图
    localBase64: String,

    // 📐 层级 z-index
    zIndex: { type: Number, default: 1000 },

    // 🌫️ 是否添加白色蒙版
    useWhiteOverlay: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      visible: true, // 是否可见
      currentWidth: parseInt(this.width), // 当前宽度（支持动态变化）
      isDragging: false,   // 是否正在拖动中
      startX: 0,           // 拖动起始点
      maxWidth: 0,         // 最大宽度限制
      scrollbarWidth: 0    // 滚动条宽度
    };
  },

  computed: {
    // 🧮 外层容器样式
    wrapperStyle() {
      return {
        position: 'fixed',
        top: '0',
        bottom: '0',
        [this.side]: '0',
        width: this.currentWidth + 'px',
        zIndex: this.zIndex,
        display: 'flex',
        flexDirection: this.side === 'left' ? 'row' : 'row-reverse',
        borderRadius: '20px',
        overflow: 'hidden',
        boxShadow: '0 0 10px rgba(0,0,0,0.2)'
      };
    },

    // 🎨 内容包装器样式
    contentWrapperStyle() {
      return {
        flex: 1,
        position: 'relative',
        height: '100%'
      };
    },

    // 背景层样式
    backgroundStyle() {
      const bg = this.localBase64
          ? `url("data:image/png;base64,${this.localBase64}")`
          : this.imageSource
              ? `url("${this.imageSource}")`
              : undefined;

      return {
        position: 'fixed',
        top: 0,
        left: 0,
        width: this.currentWidth + 'px',
        height: '100%',
        background: bg ? bg : this.color,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        zIndex: 0, // 确保在内容下方
        pointerEvents: 'none',
        overflow: 'hidden' // 确保内部蒙版不会溢出
      };
    },

    // 滚动区域容器样式
    scrollContainerStyle() {
      return {
        position: 'absolute',
        top: 0,
        bottom: 0,
        left: 0,
        right: 0,
        overflowY: 'auto',
        zIndex: 1,
        backgroundColor: 'transparent', // 确保内容区域背景透明
        pointerEvents: 'auto' // 滚动区域允许鼠标事件
      };
    },

    // 内容区域样式
    scrollContentStyle() {
      return {
        minHeight: '100%',
        padding: '10px',
        boxSizing: 'border-box',
        backgroundColor: 'transparent' // 确保内容区域背景透明
      };
    },

    // 顶部固定区域样式 - 宽度减去滚动条宽度
    fixedTopStyle() {
      return {
        position: 'fixed',
        top: 0,
        [this.side]: 0,
        //width: (this.currentWidth - this.scrollbarWidth) + 'px',
        width: (this.currentWidth - 15) + 'px',
        height: '25%',
        backgroundColor: 'rgba(58,197,216,1)',
        backgroundImage: '',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        zIndex: 4, // 提高层级确保显示在最上方
        borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.05)',
        pointerEvents: 'auto' // 允许固定区域响应鼠标事件
      };
    },

    // 顶部占位元素样式
    fixedTopPlaceholderStyle() {
      return {
        height: '25vh', // 与固定顶部高度匹配
        pointerEvents: 'none'
      };
    }
  },

  mounted() {
    this.maxWidth = window.innerWidth / 2;
    this.calculateScrollbarWidth(); // 计算滚动条宽度

    window.addEventListener('resize', this.updateMaxWidth);
  },

  beforeUnmount() {
    window.removeEventListener('resize', this.updateMaxWidth);
  },

  methods: {
    // 计算滚动条宽度
    calculateScrollbarWidth() {
      // 创建临时元素测量滚动条宽度
      const div = document.createElement('div');
      div.style.overflowY = 'scroll';
      div.style.visibility = 'hidden';
      div.style.width = '100px';
      div.style.height = '100px';
      div.style.msOverflowStyle = 'scrollbar'; // 兼容IE

      document.body.appendChild(div);
      const scrollbarWidth = div.offsetWidth - div.clientWidth;
      document.body.removeChild(div);

      this.scrollbarWidth = scrollbarWidth;
    },

    updateMaxWidth() {
      this.maxWidth = window.innerWidth / 2;
      if (this.currentWidth > this.maxWidth) {
        this.currentWidth = this.maxWidth;
        this.$emit('width-changed', this.currentWidth);
      }

      // 更新固定顶部和背景宽度
      this.updateFixedElementsWidth();
    },

    startDragging(e) {
      this.isDragging = true;
      this.startX = e.clientX;

      const mask = document.querySelector('.fullscreen-mask');
      if (mask) {
        mask.style.zIndex = '99999';
      }
    },

    onDrag(e) {
      if (!this.isDragging) return;

      const delta = this.side === 'left'
          ? e.clientX - this.startX
          : this.startX - e.clientX;

      this.startX = e.clientX;
      this.currentWidth = Math.max(200, Math.min(this.currentWidth + delta, this.maxWidth));
      this.$emit('width-changed', this.currentWidth);

      // 更新固定顶部和背景宽度
      this.updateFixedElementsWidth();
    },

    // 更新固定元素宽度的方法
    updateFixedElementsWidth() {
      const fixedTop = document.querySelector('.sidebar-fixed-top');
      const background = document.querySelector('.sidebar-background');

      if (fixedTop) {
        fixedTop.style.width = (this.currentWidth - this.scrollbarWidth) + 'px';
      }

      if (background) {
        background.style.width = this.currentWidth + 'px';
      }
    },

    stopDragging() {
      this.isDragging = false;

      const mask = document.querySelector('.fullscreen-mask');
      if (mask) {
        mask.style.zIndex = '9999';
      }
    }
  }
};
</script>

<style scoped>
/* 🎨 美化滚动条 */
.sidebar-scroll-container::-webkit-scrollbar {
  width: 8px;
}
.sidebar-scroll-container::-webkit-scrollbar-thumb {
  background-color: #aaa;
  border-radius: 4px;
}
.sidebar-scroll-container::-webkit-scrollbar-track {
  background-color: transparent;
}

/* 拖动区域 */
.resize-handle {
  width: 6px;
  cursor: ew-resize;
  background-color: rgba(0, 0, 0, 0.1);
  transition: background-color 0.2s;
}
.resize-handle:hover {
  background-color: rgba(255, 182, 193, 0.6);
  border-left: 2px solid #ff69b4;
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
}

/* 顶部占位元素 */
.fixed-top-placeholder {
  pointer-events: none;
}

/* 白色半透明遮罩 */
.white-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.4); /* 白色 40% 透明 */
  pointer-events: none; /* 避免遮罩层阻挡鼠标事件 */
}


</style>
