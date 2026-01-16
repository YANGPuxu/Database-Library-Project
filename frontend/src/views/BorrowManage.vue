<template>
  <div class="page-container">
    <div class="center-wrapper">
      <el-card class="glass-card borrow-card">
        <template #header>
          <div class="card-header">
            <div class="icon-box-large">
              <el-icon><ShoppingCartFull /></el-icon>
            </div>
            <div>
              <div class="title-large">借阅办理台</div>
              <div class="subtitle">Search Reader & Book to Borrow</div>
            </div>
          </div>
        </template>
        
        <el-form :model="form" label-position="top" size="large" class="borrow-form">
          
          <el-form-item label="第一步：确认借阅人">
            <el-select
              v-model="form.card_id"
              filterable
              placeholder="🔍 输入姓名或学号搜索..."
              style="width: 100%"
              no-match-text="未找到该读者"
              class="custom-select"
            >
              <el-option
                v-for="item in readerOptions"
                :key="item.card_id"
                :label="item.displayLabel"
                :value="item.card_id"
              >
                <div class="option-item">
                  <span class="name">{{ item.name }}</span>
                  <el-tag size="small" effect="plain" round>{{ item.category }}</el-tag>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="第二步：扫描/选择图书">
            <el-select
              v-model="form.inventory_id"
              filterable
              placeholder="🔍 输入书名、ISBN 或 条码..."
              style="width: 100%"
              no-data-text="没有可借的在馆图书"
              class="custom-select"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
              <el-option
                v-for="item in inventoryOptions"
                :key="item.id"
                :label="item.searchLabel" 
                :value="item.id"
              >
                <div class="book-option">
                  <div class="book-title">《{{ item.bookTitle }}》</div>
                  <div class="book-meta">
                    <span class="isbn">{{ item.isbn }}</span>
                    <el-tag size="small" type="success" effect="light">在馆</el-tag>
                  </div>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item style="margin-top: 30px">
            <el-button type="primary" class="gradient-btn-large" @click="handleBorrow" :loading="submitLoading" round>
              确认借出 (Confirm)
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <transition name="el-zoom-in-top">
        <el-card v-if="lastSuccess" class="glass-card result-card">
          <div class="result-content">
            <el-icon class="success-icon" size="50" color="#67c23a"><CircleCheckFilled /></el-icon>
            <div class="result-text">
              <h3>办理成功</h3>
              <p>{{ lastSuccess }}</p>
            </div>
            <el-button @click="lastSuccess = ''" round>继续办理</el-button>
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
import { ShoppingCartFull, CircleCheckFilled, Search } from '@element-plus/icons-vue'

const dataLoading = ref(false)
const submitLoading = ref(false)
const lastSuccess = ref('')

const rawReaders = ref([])
const rawBooks = ref([])
const rawPublishers = ref([])
const rawInventory = ref([])

const form = reactive({ card_id: null, inventory_id: null })

const initData = async () => {
  dataLoading.value = true
  try {
    const [resReaders, resBooks, resPubs, resInv] = await Promise.all([
      request.get('/readers/'),
      request.get('/books/'),
      request.get('/publishers/'),
      request.get('/inventory/')
    ])
    rawReaders.value = resReaders
    rawBooks.value = resBooks
    rawPublishers.value = resPubs
    rawInventory.value = resInv
  } finally {
    dataLoading.value = false
  }
}

onMounted(() => initData())

const readerOptions = computed(() => rawReaders.value.map(r => ({ ...r, displayLabel: `${r.name} (ID: ${r.card_id})` })))

const inventoryOptions = computed(() => {
  const availableItems = rawInventory.value.filter(item => item.status === 1)
  return availableItems.map(inv => {
    const book = rawBooks.value.find(b => b.isbn === inv.isbn) || {}
    const pub = rawPublishers.value.find(p => p.id === book.publisher_id) || {}
    const bookTitle = book.title || '未知书名'
    return {
      id: inv.id,
      bookTitle: bookTitle,
      isbn: inv.isbn,
      searchLabel: `${bookTitle} | ${pub.name} | ${inv.isbn} | #${inv.id}`
    }
  })
})

const handleBorrow = async () => {
  if (!form.card_id || !form.inventory_id) return ElMessage.warning('请选择读者和图书')
  submitLoading.value = true
  try {
    await request.post('/borrow/', { card_id: form.card_id, inventory_id: form.inventory_id })
    ElMessage.success('借阅办理成功！')
    
    const readerName = readerOptions.value.find(r => r.card_id === form.card_id)?.name
    const bookTitle = inventoryOptions.value.find(i => i.id === form.inventory_id)?.bookTitle
    lastSuccess.value = `${readerName} 借阅了 《${bookTitle}》`
    
    initData() // 刷新库存
    form.inventory_id = null
  } catch (err) {} finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.page-container {
  display: flex;
  justify-content: center;
  padding-top: 40px;
}
.center-wrapper {
  width: 550px;
}

.glass-card {
  border: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.icon-box-large {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border-radius: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3);
}

.title-large { font-size: 20px; font-weight: bold; color: #303133; }
.subtitle { font-size: 13px; color: #909399; margin-top: 2px; }

.borrow-form {
  padding: 10px 0;
}

/* 下拉选项样式 */
.option-item { display: flex; justify-content: space-between; align-items: center; }
.book-option { padding: 5px 0; }
.book-title { font-weight: bold; color: #303133; font-size: 14px; }
.book-meta { display: flex; justify-content: space-between; margin-top: 4px; font-size: 12px; color: #909399; }

.gradient-btn-large {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: bold;
  background: linear-gradient(90deg, #409eff 0%, #3a8ee6 100%);
  border: none;
  box-shadow: 0 6px 20px rgba(64, 158, 255, 0.3);
  transition: transform 0.2s;
}
.gradient-btn-large:active { transform: scale(0.98); }

.result-card {
  margin-top: 20px;
  background: #f0f9eb; /* 浅绿背景 */
}
.result-content {
  display: flex;
  align-items: center;
  gap: 15px;
}
.result-text h3 { margin: 0; color: #67c23a; }
.result-text p { margin: 5px 0 0 0; color: #606266; font-size: 14px; }
</style>