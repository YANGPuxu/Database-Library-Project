<template>
  <div class="common-layout">
    <div class="bg-shape shape-1"></div>
    <div class="bg-shape shape-2"></div>

    <el-container class="layout-container">
      
      <el-aside width="240px" class="glass-aside">
        <div class="logo">
          <div class="logo-icon-box">
            <el-icon size="24" color="#fff"><Reading /></el-icon>
          </div>
          <span class="logo-text">Library OS</span>
        </div>
        
        <el-menu
          active-text-color="#409eff"
          background-color="transparent" 
          class="el-menu-vertical"
          :default-active="activePath"
          text-color="#505255"
          router
        >
          <el-menu-item index="/home/readers">
            <el-icon><User /></el-icon>
            <span>读者管理</span>
          </el-menu-item>

          <el-menu-item index="/home/books">
            <el-icon><Notebook /></el-icon>
            <span>图书资源</span>
          </el-menu-item>

          <el-menu-item index="/home/borrow">
            <el-icon><ShoppingCartFull /></el-icon>
            <span>借阅办理</span>
          </el-menu-item>

          <el-menu-item index="/home/return">
            <el-icon><RefreshLeft /></el-icon>
            <span>归还办理</span>
          </el-menu-item>

          <el-menu-item index="/home/fines">
            <el-icon><Money /></el-icon>
            <span>罚款中心</span>
          </el-menu-item>
        </el-menu>

        <div class="aside-footer">
           <p>© 2026 Library System</p>
        </div>
      </el-aside>

      <el-container class="main-container">
        <el-header class="glass-header">
          <div class="breadcrumb">
            <el-icon style="margin-right: 5px"><Monitor /></el-icon>
            <span>管理控制台</span>
          </div>
          <div class="user-info">
            <span class="welcome-text">Good Evening,</span>
            <span class="username">Admin</span>
            <el-avatar :size="36" class="user-avatar"> A </el-avatar>
            <el-button link type="danger" @click="handleLogout" style="margin-left: 10px">退出</el-button>
          </div>
        </el-header>

        <el-main>
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Notebook, ShoppingCartFull, RefreshLeft, Money, Reading, Monitor } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()

const activePath = computed(() => route.path)

const handleLogout = () => {
  localStorage.removeItem('user_id')
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<style scoped>
/* --- 全局大背景：柔和流体渐变 --- */
.common-layout {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%); /* 梦幻紫蓝渐变 */
  position: relative;
  overflow: hidden;
}

/* 背景装饰球 (不抢眼，增加氛围) */
.bg-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
}
.shape-1 {
  width: 500px;
  height: 500px;
  background: #fff;
  opacity: 0.4;
  top: -100px;
  left: -100px;
}
.shape-2 {
  width: 400px;
  height: 400px;
  background: #a18cd1;
  opacity: 0.3;
  bottom: -50px;
  right: -50px;
}

.layout-container {
  height: 100%;
  position: relative;
  z-index: 1; /* 保证内容在背景球之上 */
}

/* --- 侧边栏：毛玻璃 (Glassmorphism) --- */
.glass-aside {
  background: rgba(255, 255, 255, 0.55); /* 半透明白 */
  backdrop-filter: blur(12px);           /* 磨砂效果 */
  -webkit-backdrop-filter: blur(12px);   /* Safari 兼容 */
  border-right: 1px solid rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
  transition: all 0.3s;
  
  /* 核心：隐藏滚动条但保留滚动功能 */
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE/Edge */
}
/* Chrome/Safari 隐藏滚动条 */
.glass-aside::-webkit-scrollbar {
  display: none;
}

.logo {
  height: 80px;
  display: flex;
  align-items: center;
  padding-left: 25px;
}
.logo-icon-box {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 12px;
  box-shadow: 0 4px 10px rgba(118, 75, 162, 0.3);
}
.logo-text {
  font-size: 20px;
  font-weight: 800;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

/* 菜单样式重写 */
.el-menu-vertical {
  border: none !important;
  margin-top: 10px;
  padding: 0 10px;
}
:deep(.el-menu-item) {
  border-radius: 12px;
  margin-bottom: 8px;
  height: 50px;
  font-weight: 500;
}
:deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.6) !important;
}
:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #e0c3fc 0%, #8ec5fc 100%); /* 选中项也是渐变 */
  color: #2c3e50 !important;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(142, 197, 252, 0.3);
}
:deep(.el-menu-item .el-icon) {
  font-size: 18px;
}

.aside-footer {
  margin-top: auto;
  padding: 20px;
  text-align: center;
  color: #909399;
  font-size: 12px;
}

/* --- 顶栏：毛玻璃 --- */
.glass-header {
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.6);
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
}
.breadcrumb {
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 14px;
}

.user-info {
  display: flex;
  align-items: center;
}
.welcome-text {
  color: #909399;
  font-size: 12px;
  margin-right: 5px;
}
.username {
  font-weight: bold;
  color: #2c3e50;
  margin-right: 15px;
}
.user-avatar {
  background: #764ba2;
  color: #fff;
  font-weight: bold;
  border: 2px solid #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* --- 内容区 --- */
.el-main {
  padding: 20px 30px;
  /* 内容区不需要背景色，直接透出底层的渐变 */
}

/* 路由动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px); /* 稍微有个上浮效果 */
}
</style>