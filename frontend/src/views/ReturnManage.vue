<template>
  <div class="page-container">
    <div class="center-wrapper">
      <el-card class="glass-card return-card">
        <template #header>
          <div class="card-header">
            <div class="icon-box-large warning-gradient">
              <el-icon><RefreshLeft /></el-icon>
            </div>
            <div>
              <div class="title-large">图书归还台</div>
              <div class="subtitle">Return Books & Check Status</div>
            </div>
          </div>
        </template>

        <el-form :model="form" label-position="top" size="large" class="return-form">
          
          <el-form-item label="选择待还图书">
            <el-select
              v-model="form.inventory_id"
              filterable
              placeholder="🔍 输入书名或条码搜索..."
              style="width: 100%"
              no-data-text="没有外借中的图书"
              class="custom-select"
            >
              <el-option
                v-for="item in returnOptions"
                :key="item.id"
                :label="item.searchLabel"
                :value="item.id"
              >
                <div class="book-option">
                  <div class="book-title">《{{ item.bookTitle }}》</div>
                  <div class="book-meta">
                    <span>ID: {{ item.id }}</span>
                    <el-tag size="small" type="warning" effect="dark">借出中</el-tag>
                  </div>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="图书状态检查" class="status-item">
            <div class="switch-container">
              <span class="switch-label">是否完好？</span>
              <el-switch
                v-model="form.is_damaged"
                style="--el-switch-on-color: #ff4949; --el-switch-off-color: #13ce66"
                active-text="已损坏 (Damaged)"
                inactive-text="完好 (Good)"
                inline-prompt
                width="150px"
              />
            </div>
            <div class="status-desc" v-if="form.is_damaged">
              <el-icon color="#ff4949"><Warning /></el-icon> 注意：这将自动产生赔偿罚款
            </div>
          </el-form-item>

          <el-form-item style="margin-top: 30px">
            <el-button type="success" class="gradient-btn-success" @click="handleReturn" :loading="submitLoading" round>
              确认归还 (Process Return)
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <transition name="el-zoom-in-bottom">
        <el-card v-if="resultInfo" class="glass-card result-card" :class="{'has-fine': resultInfo.isFine}">
          <div class="result-content">
            <el-icon class="result-icon" size="40" :color="resultInfo.isFine ? '#e6a23c' : '#67c23a'">
              <component :is="resultInfo.isFine ? 'WarningFilled' : 'CircleCheckFilled'" />
            </el-icon>
            <div class="result-text">
              <h3 :style="{color: resultInfo.isFine ? '#e6a23c' : '#67c23a'}">{{ resultInfo.title }}</h3>
              <p>{{ resultInfo.message }}</p>
            </div>
            <div class="result-actions">
               <el-button v-if="resultInfo.isFine" type="danger" size="small" @click="$router.push('/home/fines')">去缴费</el-button>
               <el-button @click="resetForm" size="small">继续</el-button>
            </div>
          </div>
        </el-card>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import request from '../utils/request'
import { ElMessage } from 'element-plus'
import { RefreshLeft, WarningFilled, CircleCheckFilled, Warning } from '@element-plus/icons-vue'

const submitLoading = ref(false)
const resultInfo = ref(null)
const rawBooks = ref([])
const rawInventory = ref([])

const form = reactive({ inventory_id: null, is_damaged: false })

const initData = async () => {
  const [resBooks, resInv] = await Promise.all([request.get('/books/'), request.get('/inventory/')])
  rawBooks.value = resBooks
  rawInventory.value = resInv
}
onMounted(() => initData())

const returnOptions = computed(() => {
  return rawInventory.value.filter(item => item.status === 0).map(inv => {
    const book = rawBooks.value.find(b => b.isbn === inv.isbn) || {}
    const title = book.title || '未知书名'
    return {
      id: inv.id, bookTitle: title, searchLabel: `${title} | ${inv.isbn} | #${inv.id}`
    }
  })
})

const handleReturn = async () => {
  if (!form.inventory_id) return ElMessage.warning('请选择图书')
  submitLoading.value = true
  resultInfo.value = null
  try {
    const res = await request.post('/return/', { inventory_id: form.inventory_id, is_damaged: form.is_damaged })
    const hasFine = res.message.includes('罚款')
    ElMessage({ message: '归还成功', type: hasFine ? 'warning' : 'success' })
    resultInfo.value = { isFine: hasFine, title: hasFine ? '产生罚款' : '归还成功', message: res.message }
    initData()
    form.inventory_id = null
    form.is_damaged = false
  } catch (err) {} finally { submitLoading.value = false }
}
const resetForm = () => { resultInfo.value = null }
</script>

<style scoped>
.page-container {
  display: flex;
  justify-content: center;
  padding-top: 40px;
}
.center-wrapper { width: 550px; }

.glass-card {
  border: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex; align-items: center; gap: 15px; padding-bottom: 10px; border-bottom: 1px solid #f0f0f0;
}
.title-large { font-size: 20px; font-weight: bold; color: #303133; }
.subtitle { font-size: 13px; color: #909399; margin-top: 2px; }

.icon-box-large {
  width: 50px; height: 50px; border-radius: 12px;
  display: flex; justify-content: center; align-items: center; color: white; font-size: 24px;
}
.warning-gradient {
  background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); /* 橙色渐变 */
  box-shadow: 0 4px 15px rgba(253, 160, 133, 0.4);
}

.book-option { padding: 5px 0; }
.book-title { font-weight: bold; font-size: 14px; }
.book-meta { display: flex; justify-content: space-between; margin-top: 4px; font-size: 12px; color: #909399; }

.switch-container {
  display: flex; align-items: center; justify-content: space-between;
  background: #f8faff; padding: 10px 15px; border-radius: 8px; border: 1px solid #eaeefb;
}
.switch-label { font-weight: bold; color: #606266; }
.status-desc { margin-top: 8px; font-size: 12px; color: #ff4949; display: flex; align-items: center; gap: 5px; }

.gradient-btn-success {
  width: 100%; height: 50px; font-size: 16px; font-weight: bold;
  background: linear-gradient(90deg, #67c23a 0%, #42d885 100%);
  border: none; box-shadow: 0 6px 20px rgba(103, 194, 58, 0.3);
}

.result-card { margin-top: 20px; background: #f0f9eb; }
.result-card.has-fine { background: #fdf6ec; }
.result-content { display: flex; align-items: center; gap: 15px; }
.result-text h3 { margin: 0; }
.result-text p { margin: 5px 0 0 0; color: #606266; font-size: 13px; max-width: 250px; }
.result-actions { margin-left: auto; display: flex; gap: 5px; }
</style>