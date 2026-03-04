<template>
  <div class="resizable-sidebar" :style="{ width: width + 'px' }">
    <div class="sidebar-header">
      <h3>小说编辑</h3>
    </div>
    <div class="sidebar-content">
      <div class="editor-container">
        <textarea
          v-model="content"
          placeholder="请输入小说内容..."
          class="editor-textarea"
          @input="handleInput"
        ></textarea>
      </div>
      <div class="editor-footer">
        <button class="save-button" @click="saveNovel">保存小说</button>
        <button class="export-button" @click="exportToDoc">导出为DOC</button>
      </div>
    </div>
    <div
      class="resize-handle"
      :class="{ active: isResizing }"
      @mousedown="startResizing"
    ></div>
  </div>
</template>

<script>
export default {
  name: "ResizableRightSidebar",
  props: {
    width: {
      type: Number,
      default: 300,
    },
  },
  data() {
    return {
      content: "",
      isResizing: false,
      startX: 0,
      startWidth: 0,
    };
  },
  methods: {
    handleInput() {
      this.$emit("content-updated", this.content);
    },
    startResizing(e) {
      e.preventDefault();
      this.isResizing = true;
      this.startX = e.clientX;
      this.startWidth = this.width;

      document.addEventListener("mousemove", this.onMouseMove);
      document.addEventListener("mouseup", this.stopResizing);
    },
    onMouseMove(e) {
      if (!this.isResizing) return;
      const dx = e.clientX - this.startX;
      const newWidth = this.startWidth + dx;
      if (newWidth >= 200 && newWidth <= 600) {
        this.$emit("update:width", newWidth);
      }
    },
    stopResizing() {
      this.isResizing = false;
      document.removeEventListener("mousemove", this.onMouseMove);
      document.removeEventListener("mouseup", this.stopResizing);
    },
    saveNovel() {
      this.$emit("save-novel", this.content);
    },
    exportToDoc() {
      this.$emit("export-novel", this.content);
    },
  },
};
</script>

<style scoped>
.resizable-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  background-color: #fff;
  box-shadow: -2px 0 5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.sidebar-header {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-container {
  flex: 1;
  padding: 10px;
}

.editor-textarea {
  width: 100%;
  height: 100%;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  resize: none;
  font-family: Arial, sans-serif;
}

.editor-footer {
  padding: 10px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
}

.save-button,
.export-button {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-button {
  background-color: #4caf50;
  color: white;
}

.export-button {
  background-color: #2196f3;
  color: white;
}

.resize-handle {
  position: absolute;
  top: 0;
  left: 0;
  width: 5px;
  height: 100%;
  cursor: col-resize;
  background-color: #ddd;
}

.resize-handle.active {
  background-color: #aaa;
}
</style>