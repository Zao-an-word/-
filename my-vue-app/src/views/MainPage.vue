<template>
  <div
      class="main-container"
      :class="{ 'editor-open': isTextEditorOpen }"
  >
    <!-- 背景图层 -->
    <div class="background"></div>

    <!-- 内容层 -->
    <!-- 左侧：可拖动的侧边栏 -->
    <ResizableSidebar
        v-model:width="sidebarWidth"
        :side="'left'"
        :image-source="require('@/assets/img/side.png')"
        :use-white-overlay="true"
        @width-changed="onWidthChanged"
    >
      <!-- 插槽内容：固定区域 -->
      <template #fixed-content>
        <!-- 自定义按钮 -->
        <CustomButton
            label="newChat"
            :color="'linear-gradient(90deg, rgba(0,255,255,1) 0%, rgba(146,254,157,1) 100%)'"
            width="80px"
            height="32px"
            shape="rounded"
            text="+新对话"
            textColor="#000000"
            textSize="14px"
            :followScroll="false"
            style="position: absolute; top: 10px; right: 10px;"
            @custom-click="startNewChat"
        />
        <CustomButton
            label="go-to-platform"
            :color="'linear-gradient(90deg, rgba(0,255,255,1) 0%, rgba(146,254,157,1) 100%)'"
            width="100px"
            height="32px"
            shape="rounded"
            text="小说平台"
            textColor="#black"
            textSize="14px"
            :followScroll="false"
            style="position: absolute; top: 10px; left: 10px;"
            @custom-click="goToPlatformPage"
        />
        <!-- 生成地图按钮（居中） -->
        <CustomButton
            label="generateMap"
            :image-source="require('@/assets/img/map_create.png')"
            width="60px"
            height="60px"
            shape="circle"
            :followScroll="false"
            style="position: absolute; top: 60px; left: 50%; transform: translateX(-50%);"
            @custom-click="enterMapMode"
        />
        <!-- 作为标签的按键 -->
        <CustomButton
            label="generateMap_Text"
            :color="'linear-gradient(90deg, rgba(0,255,255,1) 0%, rgba(146,254,157,1) 100%)'"
            width="60px"
            height="35px"
            shape="rounded"
            text="地图
            生成"
            textColor="#000000"
            textSize="14px"
            :followScroll="false"
            style="position: absolute; top: 130px; left: 50%; transform: translateX(-50%);"
        />

        <!-- 文生图按钮（靠左） -->
        <CustomButton
            label="generatePhoto"
            :image-source="require('@/assets/img/text_to_picture.png')"
            width="60px"
            height="60px"
            shape="circle"
            :followScroll="false"
            style="position: absolute; top: 60px; left: 5px;"
            @custom-click="enterPhotoMode"
        />
        <!-- 作为标签的按键 -->
        <CustomButton
            label="generatePhoto_Text"
            :color="'linear-gradient(90deg, rgba(0,255,255,1) 0%, rgba(146,254,157,1) 100%)'"
            width="60px"
            height="35px"
            shape="rounded"
            text="文生图"
            textColor="#000000"
            textSize="14px"
            :followScroll="false"
            style="position: absolute; top: 130px; left: 5px;"
        />

        <!-- 生成人物关系图按钮（靠右） -->
        <CustomButton
            label="generateMermaid"
            :image-source="require('@/assets/img/relationship.png')"
            width="60px"
            height="60px"
            shape="circle"
            :followScroll="false"
            style="position: absolute; top: 60px; right: 5px;"
            @custom-click="enterMermaid"
        />
        <!-- 作为标签的按键 -->
        <CustomButton
            label="generateMermaid_Text"
            :color="'linear-gradient(90deg, rgba(0,255,255,1) 0%, rgba(146,254,157,1) 100%)'"
            width="60px"
            height="35px"
            shape="rounded"
            text="人物
            关系图"
            textColor="#000000"
            textSize="14px"
            :followScroll="false"
            style="position: absolute; top: 130px; right: 5px;"
        />
      </template>

      <!-- 侧边栏滚动内容 -->
       <!-- 新增一个按钮用于文生图 -->
        <!-- 文生图生成结果展示 -->
      <div v-if="imageUrl" class="photo-result">
        <h4 style="margin: 10px 0; text-align: center;">生成的文生图</h4>
        <img
          :src="imageUrl"
          style="width: 100%; border-radius: 8px; margin-bottom: 15px;"
          :alt="imageUrl ? '文生图预览' : '未生成文生图'"
          @error="handlephotoImageError"
        />
      </div>

      <!-- 文生图生成状态提示 -->
      <div v-if="isGeneratingPhoto" class="photo-loading">
        <p>正在生成文生图...</p>
      </div>

      <!-- 文生图生成错误提示 -->
      <div v-if="photoError" class="photo-error">
        <p style="color: red; font-size: 12px;">{{ photoError }}</p>
      </div>

      <!-- 地图生成结果展示 -->
      <div v-if="mapImageUrl" class="map-result">
        <h4 style="margin: 10px 0; text-align: center;">生成的地图</h4>
        <img
          :src="mapImageUrl"
          style="width: 100%; border-radius: 8px; margin-bottom: 15px;"
          :alt="mapImageUrl ? '地图预览' : '未生成地图'"
          @error="handleImageError"
        />
      </div>

      <!-- 地图生成状态提示 -->
      <div v-if="isGeneratingMap" class="map-loading">
        <p>正在生成地图...</p>
      </div>

      <!-- 地图生成错误提示 -->
      <div v-if="mapError" class="map-error">
        <p style="color: red; font-size: 12px;">{{ mapError }}</p>
      </div>

      <!-- 人物关系图生成结果展示 -->
      <!-- 替换原人物关系图容器 -->
      <div class="mermaid-result" v-if="mermaidCode">
        <h4 style="margin: 10px 0; text-align: center;">生成的人物关系图</h4>
        <div id="mermaid-container" style="
          width: 100%;
          min-height: 300px;
          display: block;
          visibility: visible;
          overflow: auto;
          border: 1px solid #eee;
        "></div>
      </div>

      <!-- 人物关系图生成状态提示 -->
      <div v-if="isGeneratingMermaid" class="mermaid-loading">
        <p>正在生成人物关系图...</p>
      </div>

      <!-- 人物关系图生成错误提示 -->
      <div v-if="mermaidError" class="mermaid-error">
        <p style="color: red; font-size: 12px;">{{ mermaidError }}</p>
      </div>

      <ChatHistoryList
        :chat-history="conversations"
        :selected-id="selectedId"
        @delete-chat="handleDelete"
        @rename-chat="handleRename"
        @fetch-history="fetchHistoryMessages"
      />,

    </ResizableSidebar>

    <!-- 右侧：主区域 -->
    <div class="main-content" :style="{ marginLeft: sidebarWidth + 'px' }">
      <!-- 顶部固定长条 -->
      <div class="fixed-header" :style="{ top: 0, left: sidebarWidth + 'px', width: mainContentWidth + 'px' }">
        <label for="options"> model：</label>
        <Multiselect v-model="selectedModel" :options="modelOptions" :searchable="false" :allow-empty="false" placeholder="请选择模型" class="model-select"/>
        <TagSelector v-model="selectedTags" style="margin-left: 16px;" />
        <img
            src="@/assets/img/title_wordart.png"
            class="wordart-image"
            alt="艺术字标题"
        />
      </div>

      <!-- 消息显示区域 -->
      <div
          ref="messageContainer"
          class="message-container"
          :class="{'editor-open': isTextEditorOpen }"
          :style="{
          'margin-top': '65px',
          'padding': '10px',
          'height': messageContainerHeight + 'px',
          'overflow-y': 'auto',
          'min-width': '600px'
        }"
      >
        <ChatMessage
            v-for="(message, index) in messages"
            :key="index"
            :content="message.content"
            :isUser="message.isUser"
            :timestamp="message.timestamp"
            :isStreaming="message.isStreaming"
            @ai-bubble-clicked="openTextEditor"

        />
      </div>
    </div>

    <!-- 右上角个人资料按钮 -->
    <CustomButton
        label="userProfile"
        :imageSource="userAvatar || defaultAvatar"
        width="50px"
        height="50px"
        shape="circle"
        :followScroll="false"
        :zIndex="99999"
        style="position: fixed; top: 2px; right: 5px;"
        @custom-click="goToPersonalInfo"
    />

    <!-- AI聊天输入框 -->
    <ChatInput
        ref="chatInput"
        v-model="inputText"
        :loading="isLoading"
        :leftOffset="inputPosition.leftOffset"
        :width="inputPosition.width"
        @send="sendMessage"
        :placeholder="inputPlaceholder"
        @height-change="onInputHeightChange"
        @send-data="handleChatInputData"  
    />

    <!-- 文本编辑器 -->
    <TextEditor
        ref="textEditor"
        @closed="closeTextEditor"
        @width-changed="textEditorWidth = $event"
    />
  </div>
</template>

<script>
import ResizableSidebar from "@/components/ResizableSidebar.vue";
import CustomButton from "@/components/CustomButton.vue";
import ChatInput from "@/components/ChatInput.vue";
import ChatMessage from "@/components/ChatMessage.vue";
import TagSelector from "@/components/TagSelector.vue";
import TextEditor from "@/components/TextEditor.vue";
import 'vue-multiselect/dist/vue-multiselect.css';
import Multiselect from 'vue-multiselect';
import axios from 'axios';
import ChatHistoryList from "@/components/ChatHistoryList.vue";
import mermaid from 'mermaid';

export default {
  name: "MainLayout",
  components: {
    ResizableSidebar,
    CustomButton,
    ChatInput,
    ChatMessage,
    TextEditor,
    TagSelector,
    Multiselect,
    ChatHistoryList
  },
  data() {
    return {
      currentMode:'chat',//模式 chat/generate-map/generate-photo/generate-mermaid
      savedInputText:'',
      inputPlaceholder: '请输入消息... \n', // 动态占位符
      selectedModel: 'qwen',
      modelOptions: ['qwen', 'deepseek','serpapi','gpt-4o-mini'],
      selectedTags: [],
      tagOptions: [
        { label: '玄幻', value: '玄幻' },
        { label: '修真', value: '修真' },
        { label: '武侠', value: '武侠' },
        { label: '都市', value: '都市' },
        { label: '历史', value: '历史' },
        { label: '科幻', value: '科幻' },
        { label: '悬疑', value: '悬疑' },
        { label: '游戏', value: '游戏' },
        { label: '言情', value: '言情' },
        { label: '重生', value: '重生' },
        { label: '穿越', value: '穿越' },
        { label: '系统', value: '系统' },
        { label: '无敌', value: '无敌' },
        { label: '甜宠', value: '甜宠' },
        { label: '搞笑', value: '搞笑' },
        { label: '热血', value: '热血' },
        { label: '励志', value: '励志' },
        { label: '高智商', value: '高智商' }
      ],
      sidebarWidth: 250,
      mainContentWidth: window.innerWidth - 250,
      selectedOption: 'A',
      inputText: '',
      isLoading: false, // 是否正在发送中
      messages: [], // 存储所有消息
      messageContainerHeight: 0, // 消息容器高度
      aiResponse: '', // AI回复内容
      isStreaming: false, // 是否正在流式输出
      streamTimer: null, // 流式输出定时器
      chatInputHeightFromChild: 0, // 存储从子组件传递过来的高度
      isTextEditorOpen: false,     // 文本编辑器是否打开
      textEditorWidth: this.$refs.textEditor?.$props.width || 400,        // 文本编辑器宽度
      userAvatar:null,
      defaultAvatar:require('@/assets/img/userProfile.jpg'),
      imageUrl:"", //文生图url
      isGeneratingPhoto: false, // 文生图生成状态
      photoError: '', // 文生图生成错误信息
      mermaidCode: '',//人物关系图代码
      mermaidError: '', // 人物关系图生成错误信息
      isGeneratingMermaid: false, // 人物关系图生成状态
      mapImageUrl: '', // 存储generate-map接口返回的图片URL
      mapError: '', // 地图生成错误信息
      isGeneratingMap: false, // 地图生成状态
      fileIds: [], // 存储文件ID列表
      conversations:[],
      selectedId: 1
    };
  },
  computed:{
    // 输入框实际位置和宽度（响应文本编辑器是否开启）
    inputPosition() {
      const editorWidth = this.isTextEditorOpen ? this.textEditorWidth : 0;
      const totalAvailable = window.innerWidth - this.sidebarWidth - editorWidth;
      const delta = this.isTextEditorOpen ? 50: 0;

      return {
        leftOffset: this.sidebarWidth + totalAvailable * 0.05 - delta,
        width: totalAvailable * 0.8
      };
    }
  },

  async created(){
    await this.fetchUserInfo();
  },

  methods: {
    handleDelete() {
    },
    handleRename({ id, newTitle }) {
      const chat = this.conversations.find(c => c.id === id);
      if (chat) chat.title = newTitle;
    },
    async renderMermaid() {
      try {
        await this.$nextTick();
        const container = document.getElementById('mermaid-container');
        if (!container) throw new Error('容器不存在');

        const index = this.mermaidCode.indexOf('g');
        if (index !== -1) {
          this.mermaidCode = this.mermaidCode.slice(index)
        } else 1;
        if(this.mermaidCode.endsWith(('```'))){
          this.mermaidCode = this.mermaidCode.slice(0,-3)
        }
        else 1;
        console.log(this.mermaidCode)
        // 插入代码后立即打印，确认内容
        container.innerHTML = `<div class="mermaid">${this.mermaidCode}</div>`;

        // 执行渲染
        await mermaid.run({
          nodes: container.querySelectorAll('.mermaid'),
          document: window.document
        });

      } catch (error) {
        console.error('渲染失败:', error);
      }
    },

    enterMermaid(){
      this.savedInputText = this.inputText; // 保存当前输入
      this.currentMode = 'generate-mermaid';
      this.inputPlaceholder = '请输入人物关系描述，例如：A是B的父亲';
      this.inputText = ''; // 清空输入框
    },
    //进入地图生成模式
    enterMapMode(){
      this.savedInputText = this.inputText; // 保存当前输入
      this.currentMode = 'generate-map';
      this.inputPlaceholder = '请输入地图描述，例如：天下三分为赵国、齐国、楚国，一条大江穿过...';
      this.inputText = ''; // 清空输入框
    },
    //进入文生图模式
    enterPhotoMode(){
      this.savedInputText = this.inputText; // 保存当前输入
      this.currentMode = 'generate-photo';
      this.inputPlaceholder = '请输入图片描述，例如：一只色彩斑斓的变色龙趴在树枝上...';
      this.inputText = ''; // 清空输入框
    },
    // 取消图片生成模式，返回聊天模式
    cancelMode() {
      this.inputText = this.savedInputText; // 恢复之前的输入
      this.currentMode = 'chat';
      this.inputPlaceholder = '请输入消息...';
    },
    // 统一处理发送事件
    handleSend() {
      if (this.currentMode === 'chat') {
        this.sendMessage(); // 正常聊天
      } else if (this.currentMode === 'generate-map') {
        this.generateMap(true); // 带自动切换模式参数
      } else if (this.currentMode === 'generate-photo') {
        this.generatePhoto(true); // 带自动切换模式参数
      } else if(this.currentMode === 'generate-mermaid'){
        this.generateMermaid(true);
      }
    },

    // 处理 ChatInput 传递的消息和文件ID
    handleChatInputData(data) {
      const { question, file_ids } = data;
      // 将接收的问题设置到输入框（用于显示和后续处理）
      this.inputText = question;
      // 将文件ID设置到主界面的 fileIds（确保 sendMessage 能获取到）
      this.fileIds = Array.isArray(file_ids) ? file_ids : [];
      // 触发发送逻辑
      this.handleSend();
    },


    async fetchUserInfo(){
        try{
            const token = localStorage.getItem('token');
            const response = await axios.get('/api/me',{
                headers:{Authorization: `Bearer ${token}`}
            });
            this.userAvatar = response.data.avatar_url;
        }catch(error){
            console.error("获取用户信息失败",error);
            this.userAvatar = this.defaultAvatar;
        }
    },
    onWidthChanged(newWidth) {
      this.sidebarWidth = newWidth;
      this.updateMainContentWidth();
    },
    updateMainContentWidth() {
      this.mainContentWidth = window.innerWidth - this.sidebarWidth  - (this.isTextEditorOpen ? this.textEditorWidth : 0);
      this.updateMessageContainerHeight();
    },
    goToPersonalInfo() {
      this.$router.push("/personalinformation");
    },
    onInputHeightChange(height) {
      this.chatInputHeightFromChild = height;
      this.updateMessageContainerHeight();
    },
    // 更新消息容器高度
    updateMessageContainerHeight() {
      // 计算消息容器高度：窗口高度 - 顶部固定栏高度 - 输入框高度 - 边距
      this.messageContainerHeight = window.innerHeight - 65 - this.chatInputHeightFromChild - 45;
    },
    // 滚动到底部
    scrollToBottom() {
      if (this.$refs.messageContainer) {
        this.$refs.messageContainer.scrollTop = this.$refs.messageContainer.scrollHeight;
      }
    },
    // 模拟流式输出
    async streamResponse(fullResponse) {
      this.isStreaming = true;
      this.aiResponse = '';
      const messageIndex = this.messages.length;
      this.messages.push({
        content: '',
        isUser: false,
        timestamp: this.formatTimestamp(new Date()),
        isStreaming: true
      });
      this.scrollToBottom();
      for (let i = 0; i < fullResponse.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 20));
        this.aiResponse += fullResponse[i];
        this.messages[messageIndex].content = this.aiResponse;
        this.scrollToBottom();
      }
      this.isStreaming = false;
      this.messages[messageIndex].isStreaming = false;
      this.isLoading = false;
    },
    formatTimestamp(date) {
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${hours}:${minutes}`;
    },
    async sendMessage() {
      // 当有用户输入时执行（包含文件ID逻辑）
      if (this.inputText.trim() || this.fileIds.length > 0) {
        // 添加用户消息到聊天记录
        const userMessage = {
          content: this.inputText,
          isUser: true,
          timestamp: this.formatTimestamp(new Date())
        };
        this.messages.push(userMessage);
        this.isLoading = true;

        // 保存当前用户输入和文件ID（发送后清空）
        const currentText = this.inputText.trim();
        const currentFileIds = [...this.fileIds]; // 从ChatInput传递的文件ID列表
        this.inputText = '';
        this.fileIds = []; // 清空文件ID，避免重复发送

        // 1. 先调用/api/query检索向量库
        let queryAnswer = '';
        try {
          const queryResponse = await axios.post('/api/query', {
            question: currentText,
            file_ids: currentFileIds, // 传递文件ID检索相关内容
            top_k: 3
          });
          queryAnswer = queryResponse.data.answer || ''; // 获取检索结果
        } catch (error) {
          console.error('向量库检索失败:', error);
          alert('检索文件内容失败，请重试');
          this.isLoading = false;
          return; // 检索失败则终止流程
        }

        // 2. 调用/api/chat，整合检索结果
        try {
          const tag = this.selectedTags.map(item => item.label).join('、');
          const path = window.location.pathname;
          const pathSegments = path.split('/').filter(segment => segment);
          let targetValue = pathSegments[1]

          // 调用对话接口，传入检索结果作为参考
          const response = await axios.post("/api/chat", {
            prompt: `参考信息：${queryAnswer}标签：${tag} 用户输入：${currentText} `,
            messages: this.messages.map(msg => ({
              role: msg.isUser ? "user" : "assistant",
              content: msg.content
            })),
            temperature: 0.7,
            max_tokens: 1000, // 增加token限制，避免回答被截断
            model: this.selectedModel,
            func: "novel",
            uuid: targetValue,
            time: this.formatTimestamp(new Date())
          });

          // 流式输出AI回答
          this.streamResponse(response.data);
          this.scrollToBottom();
        } catch (error) {
          console.error('对话接口调用失败:', error);
          alert('获取回答失败，请重试');
        } finally {
          this.isLoading = false;
        }
      }
    },
     // 点击“新对话”按钮
    async startNewChat() {
      const token = localStorage.getItem('token');
      const response = await axios.post("http://localhost:8000/api/get_port", {},{
        headers: { Authorization: `Bearer ${token}` }
      });
      const port = response.data.port;
      console.log(port);
      let nextId="1";
      nextId = port;
      this.fetchHistoryMessages();
      // 跳转到新路由
      //this.$router.push(`/main/${nextId}`);
      this.$router.push(`/main/${nextId}`);
      // 重置聊天数据
      this.messages = [];
      this.inputText = '';
      this.isLoading = false;
      this.aiResponse = '';
      this.isStreaming = false;

      // 清除流式输出定时器
      if (this.streamTimer) {
        clearTimeout(this.streamTimer);
        this.streamTimer = null;
      }
      // 滚动到底部
      this.scrollToBottom();
    },


    // 模拟从后端获取历史记录
    async fetchHistoryMessages() {
      let targetValue=0
      try {
        // 模拟后端响应
        const path = window.location.pathname;

        // 分割路径为数组（去掉空字符串）
        const pathSegments = path.split('/').filter(segment => segment);
        // 数组结果：['main', 'bc4b487ed67c4479a20839c1165af66b']

        // 获取目标值（假设它是路径中的第二个片段）
        targetValue = pathSegments[1];
        const history = await axios.post(`http://localhost:8000/api/get_history?uuid=${targetValue}`);
        const historyMessages = history.data.result// 输出到浏览器控制台

        // 将历史消息添加到 messages 数组中
        this.messages = historyMessages;


        const photo = await axios.post(`http://localhost:8000/api/get_photo?uuid=${targetValue}`);


        if (photo.data.url1 !='')
          this.mapImageUrl=photo.data.url1
        if(photo.data.url2 !='')
          this.mermaidCode=photo.data.url2
          this.renderMermaid();
        if(photo.data.url3 !='')
          this.imageUrl=photo.data.url3;

        const conversationshistory = await axios.post(`http://localhost:8000/api/get_conversations?uuid=${targetValue}`);
        this.conversations = conversationshistory.data// 输出到浏览器控制台

        const token = localStorage.getItem('token');
        const result = await axios.post(`http://localhost:8000/api/port_id?uuid=${targetValue}`, {},{
              headers: { Authorization: `Bearer ${token}` }
            });
        this.selectedId = result.data
        console.log("是滴几条",this.selectedId)
        // 滚动到底部
        this.scrollToBottom();
      } catch (error) {
        console.error('获取历史消息失败:', error);
      }

    },

    // 打开文本编辑器
    openTextEditor(text) {
      this.$refs.textEditor.open(text);
      this.isTextEditorOpen = true;
    },
    // 关闭文本编辑器
    closeTextEditor() {
      this.isTextEditorOpen = false;
    },
    goToPlatformPage() {
      this.$router.push("/platform");
    },

    //生成地图
    async generateMap(autoSwitchMode = true) {
      // 重置状态
      this.mapError = '';
      this.isGeneratingMap = true;
      const path = window.location.pathname;

      // 分割路径为数组（去掉空字符串）
      const pathSegments = path.split('/').filter(segment => segment);
      // 数组结果：['main', 'bc4b487ed67c4479a20839c1165af66b']

      // 获取目标值（假设它是路径中的第二个片段）
      const targetValue = pathSegments[1];
      console.log(targetValue)
      try {
        // 使用输入框的内容作为生成地图的提示
        const mapPrompt = this.inputText.trim()||"天下三分为赵国，齐国，楚国，一条大江穿过齐国，楚国，向东流去赵国独占大陆北方，齐楚平分南部，齐国居西。";

        // 调用generate-map接口
        const response = await axios.post('http://localhost:8000/api/generate-map', {
          text: mapPrompt,
          conversation_uuid: targetValue
        }, {
          // 如果需要认证，添加认证头
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type':'application/json'
          }
        });

        // 假设接口返回格式为 { map_url: "图片URL", ... }
        if (response.data && response.data.map_url) {
          this.mapImageUrl = response.data.map_url;
          this.mapError = '';
          if(autoSwitchMode){
            this.inputText='';
            this.cancelMode();
          }
        } else {
          this.mapError = '未获取到地图URL，请重试';
        }
      } catch (error) {
        console.error('生成地图失败:', error);
        this.mapError = `生成失败: ${error.response?.data?.detail || error.message}`;
        this.mapImageUrl = '';
      } finally {
        this.isGeneratingMap = false;
      }
    },
    // 处理图片加载错误
    handleImageError() {
      this.mapError = '图片加载失败，请重试';
    },
    //生成文生图
    async generatePhoto(autoSwitchMode = true) {
      // 重置状态
      this.photoError = '';
      this.isGeneratingPhoto = true;
      const path = window.location.pathname;

      // 分割路径为数组（去掉空字符串）
      const pathSegments = path.split('/').filter(segment => segment);
      // 数组结果：['main', 'bc4b487ed67c4479a20839c1165af66b']

      // 获取目标值（假设它是路径中的第二个片段）
      const targetValue = pathSegments[1];


      try {
        // 使用输入框内容作为生成地图的提示
        const photoPrompt = this.inputText.trim() || "变色龙";
        //调用文生图接口
        const response = await axios.post("http://localhost:8000/api/chat", {
          prompt: photoPrompt,
          messages: [], // 使用完整的消息历史而非空数组
          temperature: 0.7,
          max_tokens: 100,
          model:'qwen',
          func: "text2photo",
          uuid: targetValue,
          time: "01:00"
        }, {
          // 如果需要认证，添加认证头
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type':'application/json'
          }
        });


        // 假设接口返回格式为 { map_url: "图片URL", ... }
        if (response.data ) {
          this.imageUrl = response.data
          this.photoError = '';
          if(autoSwitchMode){
            this.inputText = '';
            this.cancelMode();
          }
        } else {
          this.photoError = '未获取到文生图URL，请重试';
        }
      } catch (error) {
        console.error('生成文生图失败:', error);
        this.photoError = `生成失败: ${error.response?.data?.detail || error.message}`;
        this.imageUrl = '';
      } finally {
        this.isGeneratingPhoto = false;
      }
    },
    // 处理图片加载错误
    handlephotoImageError() {
      this.photoError = '图片加载失败，请重试';
    },
        //生成人物关系图
    async generateMermaid(autoSwitchMode = true) {
      // 重置状态
      this.mermaidError = '';
      this.isGeneratingMermaid = true;
      const path = window.location.pathname;

      // 分割路径为数组（去掉空字符串）
      const pathSegments = path.split('/').filter(segment => segment);
      // 数组结果：['main', 'bc4b487ed67c4479a20839c1165af66b']

      // 获取目标值（假设它是路径中的第二个片段）
      const targetValue = pathSegments[1];
      const Photoprompt = this.inputText.trim() ||`深夜的灵堂里，檀香与阴谋一同盘旋,
  顾振山遗照下的黑檀木棺尚未封钉，他的第三任妻子林晚意着遗嘱复印件的手已微微发抖。纸页上“集团35%股权由私生子江屿继承”的字样像刀，割开了她维系二十年的体面。而此刻站在她对面的，正是她大学时代的前男友、如今的法律顾问沈确--他亲手起草了这份遗嘱。
  "你早知道他的存在?”林晚意声音淬冰。沈确推了推金丝眼镜，目光扫过角落阴影里沉默的青年。那青年眉眼像极了年轻时的顾振山，可右颊的烧伤疤痕却来自林晚意儿子顾明澈的“意外”纵火-十八年前那场烧死江屿生母的化工厂火灾。
  水晶吊灯骤亮，顾明澈推门而入，染血的拳套尚未摘下。他刚在车车殴打了江屿的资助人陆医生，只因发现此人竟是父亲的主治医师。“陆医生改了死亡时间报告。”他将u盘摔在供桌上，佛龛里的观音像应声碎裂。供桌旁跪着的少女突然抬头，她是顾振山第一任妻子的养女苏禾，正用直播镜头记录一切。屏幕那端，刚与顾明离婚的前妻疯狂刷着礼物:“捅出去!我帮你夺回股权!
  香灰簌簌落在遗嘱签名处。林晚意突然轻笑，染着丹的指甲划过江屿的伤疤:“你母亲没告诉你?当年是她先爬上沈确的床.”话音未落，沈确的钢笔已扎进她咽喉三厘米，鲜血喷上“股权”二字。江屿终于动了--他掏出陆医生给的药瓶倒空，三十粒白色药丸滚进香炉。那是顾振山临终前本该服用的救命药。
  门外警笛撕裂夜空时，苏禾的直播间冲上热搜榜首。
  标题猩红刺《豪门遗嘱现形记:生父死于长子?情夫弑主母?》。`;
      try{
          await axios.post("http://localhost:8000/api/chat", {
          prompt: Photoprompt,
          messages: [], // 使用完整的消息历史而非空数组
          temperature: 0.7,
          max_tokens: 100,
          model:this.selectedModel,
          func: "relationship_diagram",
          uuid: targetValue,
          time: this.formatTimestamp(new Date())
        });
        const photo = await axios.post(`http://localhost:8000/api/get_photo?uuid=${targetValue}`);
        if (photo.data.url1 !='')
          this.mapImageUrl=photo.data.url1
        if(photo.data.url2 !='')
          this.mermaidCode=photo.data.url2
          this.renderMermaid();
        if(photo.data.url3 !='')
          this.imageUrl=photo.data.url3;
        if(autoSwitchMode){
          this.inputText = '';
          this.cancelMode()
        }
      } catch (error) {
        console.error('生成人物关系图失败:', error);
        this.mermaidError = `生成失败: ${error.response?.data?.detail || error.message}`;
        this.mermaidCode= '';
      } finally {
        this.isGeneratingMermaid = false;
      }
    },
    // 处理图片加载错误
    handlemermaidError() {
      this.mermaidError = '人物关系图加载失败，请重试';
    },


  },
  watch: {
    $route(to) {
      // 路由变化时执行（包括首次加载）
      console.log("路由参数变化：", to.params);
      // 初始化Mermaid配置
      mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      document: window.document // 关键配置
      });


      window.addEventListener("resize", this.updateMainContentWidth);
      this.updateMessageContainerHeight();
      this.fetchHistoryMessages();

      if(this.isTextEditorOpen){
        this.textEditorWidth = this.$refs.textEditor.$props.width;
      }
    }
  },

  mounted() {
    // 初始化Mermaid配置
    mermaid.initialize({
    startOnLoad: false,
    theme: 'default',
    securityLevel: 'loose',
    document: window.document // 关键配置
    });


    window.addEventListener("resize", this.updateMainContentWidth);
    this.updateMessageContainerHeight();
    this.fetchHistoryMessages();

    if(this.isTextEditorOpen){
      this.textEditorWidth = this.$refs.textEditor.$props.width;
    }
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.updateMainContentWidth);
    if (this.streamTimer) clearTimeout(this.streamTimer);
  }
};
</script>

<style scoped>
.main-container {
  position: relative;
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;

  flex-direction: column;
  align-items: center;
}

.main-container.editor-open {
  flex-direction: row;    /* 横向排列 */
  align-items: flex-start; /* 顶部对齐 */
}

.background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/img/mainbk.png');
  background-size: cover;
  background-position: center;
  z-index: 0;
  opacity: 1;
}

/* 白色蒙版层 */
.background::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(255, 255, 255, 0.65); /* 白色半透明蒙版 */
  z-index: 1;
}

/* 主内容层（侧边栏和主区域）显示在蒙版之上 */
.main-content{
  position: relative;
  z-index: 2;

  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 顶部固定长条样式 */
.fixed-header {
  position: fixed;
  z-index: 1000;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 可保留阴影提升层次感 */
  display: flex;
  align-items: center;
  width: 100%;
  background-color: rgba(255, 255, 255, 0.85); /* 微微透明白色 */
  border-bottom: 1px solid #ddd; /* 添加底部边框 */
}

/* 消息容器样式 */
.message-container {
  position: relative;
  z-index: 2;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 10px;
  margin: 70px auto 10px auto;
  max-width: 90%;
  padding: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(155, 155, 155, 0.5) transparent;

}
/* 艺术字图片样式 */
.wordart-image {
  height: 100%;           /* 高度与 fixed-header 一致 */
  max-height: 45px;       /* 可限制最大高度 */
  object-fit: contain;    /* 保持宽高比例 */
  padding-left: 100px;
}
.message-container.editor-open{
  margin-left: 60px; /* 根据需要调整间距值 */
  margin-right: auto; /* 右侧自动计算，实现左对齐 */
}

.message-container::-webkit-scrollbar {
  width: 6px;
}

.message-container::-webkit-scrollbar-track {
  background: transparent;
}

.message-container::-webkit-scrollbar-thumb {
  background-color: rgba(155, 155, 155, 0.5);
  border-radius: 20px;
}

.model-select {
  width: 160px; /* 你可以根据需要改成140px、180px等 */
  display: inline-block;
  margin-left: 8px;
  margin-right: 16px;
}

/* 模型选择框的 hover 效果 */
:deep(.model-select .multiselect) {
  border: 2px solid transparent;
  border-radius: 6px;
  transition: all 0.3s ease;
  background-clip: padding-box;
}

:deep(.model-select .multiselect__option--highlight) {
  background: transparent !important; /* 去掉绿色/红色背景 */
  color: inherit !important;          /* 保持原字体颜色 */
}

:deep(.model-select .multiselect__option--selected) {
  background: transparent !important; /* 已选项不高亮 */
  color: inherit !important;
}

/* 鼠标悬停在选项上的高亮效果 */
:deep(.model-select .multiselect__content-wrapper .multiselect__option:hover) {
  background-color: rgba(246, 217, 180, 0.2) !important; /* 半透明浅蓝色背景 */
  transition: background-color 0.2s ease; /* 平滑过渡效果 */
}

/* 选中状态的选项样式 */
:deep(.model-select .multiselect__content-wrapper .multiselect__option--selected) {
  font-weight: bold;
  color: #000000;
}

:deep(.model-select .multiselect__option:after) {
  display: none !important; /* 去掉选项后的✔️勾勾图标 */
}

:deep(.model-select .multiselect__option[aria-label*="Press enter"])::after {
  content: none !important;
}

:deep(.model-select .multiselect__single) {
  background-color: transparent !important;
  color: inherit !important;
}

:deep(.model-select .multiselect__content-wrapper::before) {
  content: none !important;
}

/* 在 style 标签中添加 */
#mermaid-container {
  /* 强制显示内容 */
  overflow: visible !important;
  position: relative !important;
  z-index: 10 !important; /* 避免被其他元素覆盖 */
}

/* 给 SVG 添加明显边框和背景，便于观察 */
#mermaid-container svg {
  border: 2px solid red !important;
  background: white !important;
  width: 100% !important;
  height: auto !important;
  min-height: 200px !important;
}
</style>