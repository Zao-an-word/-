export default {
  presets: [
    '@vue/cli-plugin-babel/preset'  // 保留原有的预设（不要删除）
  ],
  plugins: [
    // 在这里添加新插件
    '@babel/plugin-transform-class-static-block'
  ]
};