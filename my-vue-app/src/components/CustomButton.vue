<template>
  <!-- 按钮组件模板部分，绑定样式和点击事件 -->
  <button
      :id="btnId"
      :style="[buttonStyle, isHover ? hoverStyle : {}]"
      @click="handleClick"
      @mouseenter="isHover = true"
      @mouseleave="isHover = false"
  >
    {{ text }}
  </button>
</template>

<script>
export default {
  name: "CustomButton",  // 组件名，Vue要求组件名最好是多词

  // 🧩 组件接收的参数（Props），父组件传入来定制按钮
  props: {
    label: String,      // 按钮唯一标识，生成按钮ID用

    imageSource: String,  // 远程图片URL，作为背景图
    localBase64: String,  // 本地图片的Base64编码，优先级高于远程图片

    width: { type: String, default: "100px" },  // 按钮宽度，默认100px
    height: { type: String, default: "100px" }, // 按钮高度，默认100px

    top: String,       // 距离页面顶部距离（如 "20px"）
    left: String,      // 距离页面左边距离
    right: String,     // 距离页面右边距离
    bottom: String,    // 距离页面底部距离

    followScroll: { type: Boolean, default: false }, // 是否固定定位(fixed)，否则绝对定位(absolute)

    zIndex: { type: Number, default: 9999 }, // CSS层级，值越大越靠前

    shape: { type: String, default: "rounded" }, // 按钮形状，circle圆形，square方形，rounded圆角矩形

    glowColor: { type: String, default: "#ffc0cb" }, // 悬停时的发光颜色，默认粉色

    color: { type: String, default: "#cccccc" },  // 无图片时的背景色，默认浅灰色

    text: { type: String, default: "" },          // 按钮显示的文字，默认空

    textSize: { type: String, default: "16px" },  // 文字大小，默认16像素

    textColor: { type: String, default: "#ffffff" }, // 文字颜色，默认白色

    textFont: { type: String, default: "Arial" }  // 文字字体，默认Arial
  },

  // 组件内部状态
  data() {
    return {
      isHover: false,    // 是否鼠标悬停状态，初始为false
    }
  },

  // 计算属性，根据状态计算样式
  computed: {
    // 生成按钮的唯一ID，如果传了label就用它，否则随机生成一个8位字符串
    btnId() {
      return `btn_${this.label || Math.random().toString(36).slice(2, 10)}`
    },

    // 按钮的正常样式
    buttonStyle() {
      // 定位类型，跟随滚动则fixed，否则absolute
      const position = this.followScroll ? "fixed" : "absolute";

      // 根据形状计算圆角半径
      const radius = this.shape === "circle"
          ? "50%"            // 圆形圆角为50%
          : this.shape === "square"
              ? "0"          // 方形圆角为0
              : "15px";      // 圆角矩形默认15px圆角

      // 决定背景样式，优先本地Base64图，次之远程图，否则用背景色
      let bg = this.color;
      if (this.localBase64) {
        bg = `url("data:image/png;base64,${this.localBase64}")`;
      } else if (this.imageSource) {
        bg = `url("${this.imageSource}")`;
      }

      // 返回最终style对象
      return {
        position,         // 定位方式
        top: this.top,    // 顶部距离（可为空）
        left: this.left,  // 左侧距离
        right: this.right,// 右侧距离
        bottom: this.bottom, // 底部距离
        width: this.width,   // 宽度
        height: this.height, // 高度

        // 如果是背景图片，则设置background属性，否则用背景色
        background: bg.includes("url") || bg.includes("gradient") ? bg : undefined,
        backgroundColor: bg.includes("url") || bg.includes("gradient") ? undefined : this.color,

        backgroundSize: "cover",      // 背景图覆盖整个按钮
        backgroundPosition: "center", // 背景图居中显示

        border: "2px solid transparent",           // 默认透明边框边框
        borderRadius: radius,     // 圆角

        color: this.textColor,    // 文字颜色
        fontSize: this.textSize,  // 文字大小
        fontFamily: this.textFont,// 文字字体

        display: "flex",          // flex布局，方便文字居中
        alignItems: "center",     // 垂直居中
        justifyContent: "center", // 水平居中
        textAlign: "center",      // 文字居中

        zIndex: this.zIndex,      // 层级
        cursor: "pointer",        // 鼠标悬停时手型

        boxShadow: "0 0 10px rgba(0,0,0,0.1)", // 默认轻微阴影
        transition: "all 0.3s ease",           // 动画过渡，方便悬停时缩放发光

      }
    },

    // 鼠标悬停时的样式，只做放大和发光阴影，不改背景
    hoverStyle() {
      return {
        transform: "scale(1.05)",    // 放大5%
        border: `2px solid ${this.glowColor}`,  // 鼠标悬停时边框变成发光颜色
        boxShadow: `0 0 8px ${this.glowColor}, 0 0 15px ${this.glowColor}`, // 边框发光效果
      }
    }
  },

  // 组件方法
  methods: {
    // 点击按钮时，向父组件发送click事件，并带上按钮ID
    handleClick() {
      this.$emit("custom-click", this.btnId);
    }
  }
}
</script>

<style scoped>
/* 点击时缩小效果 */
button:active {
  transform: scale(0.95);
}
</style>