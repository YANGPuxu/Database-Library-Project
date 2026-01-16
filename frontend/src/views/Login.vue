<template>
  <div class="login-container">
    <div class="shape shape-1"></div>
    <div class="shape shape-2"></div>

    <div class="login-content">
      <div class="glass-card">
        <div class="header">
          <div class="logo-circle">
            <el-icon size="30" color="#409eff"><Reading /></el-icon>
          </div>
          <h2>Library OS</h2>
          <p>新一代图书馆管理系统</p>
        </div>

        <el-form :model="form" size="large" class="login-form">
          <el-form-item>
            <el-input 
              v-model="form.username" 
              placeholder="管理员账号" 
              prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item>
            <el-input 
              v-model="form.password" 
              placeholder="密码" 
              prefix-icon="Lock" 
              type="password" 
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-button type="primary" class="login-btn" @click="handleLogin" :loading="loading" round>
            进入系统
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import request from '../utils/request'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Reading } from '@element-plus/icons-vue' // 引入图标

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  if (!form.username || !form.password) return ElMessage.warning('请输入账号密码')
  loading.value = true
  try {
    const res = await request.post('/login/', form)
    ElMessage.success('欢迎回来')
    localStorage.setItem('user_id', res.user_id)
    router.push('/home')
  } catch (e) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  width: 100%;
  /* 梦幻天蓝渐变背景 */
  background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  overflow: hidden;
}

/* 两个漂浮的圆球装饰 */
.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
}
.shape-1 {
  width: 300px;
  height: 300px;
  background: #4facfe;
  top: -50px;
  left: -50px;
  opacity: 0.6;
}
.shape-2 {
  width: 400px;
  height: 400px;
  background: #fff;
  bottom: -100px;
  right: -50px;
  opacity: 0.4;
}

.login-content {
  z-index: 1;
}

/* 毛玻璃卡片 */
.glass-card {
  width: 380px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.85); /* 半透明白 */
  backdrop-filter: blur(20px);            /* 模糊背景 */
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.5);
  text-align: center;
}

.logo-circle {
  width: 60px;
  height: 60px;
  background: #ecf5ff;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 auto 15px;
}

.header h2 {
  color: #303133;
  margin: 0;
  font-size: 24px;
}

.header p {
  color: #909399;
  font-size: 14px;
  margin-top: 5px;
  margin-bottom: 30px;
}

.login-form .el-input {
  margin-bottom: 5px;
}

/* 输入框样式重写，使其更通透 */
:deep(.el-input__wrapper) {
  background-color: #f5f7fa;
  box-shadow: none !important;
  border: 1px solid transparent;
  transition: all 0.3s;
}
:deep(.el-input__wrapper:hover),
:deep(.el-input__wrapper.is-focus) {
  background-color: #fff;
  border-color: #409eff;
  box-shadow: 0 0 0 1px #409eff !important;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
  font-weight: bold;
  height: 45px;
  background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
  border: none;
  transition: transform 0.2s;
}
.login-btn:hover {
  transform: scale(1.02);
  opacity: 0.9;
}
</style>