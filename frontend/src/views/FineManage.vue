<template>
  <div class="page-container">
    <el-card class="glass-card">
      <template #header>
        <div class="card-header">
          <div class="left-panel">
            <div class="icon-box" style="background: #fef0f0; color: #f56c6c">
              <el-icon><Money /></el-icon>
            </div>
            <span class="title">罚款缴纳中心</span>
          </div>
        </div>
      </template>

      <div class="search-section">
        <el-select
          v-model="currentCardId"
          filterable
          placeholder="🔍 请搜索姓名/学号，或选择'显示所有欠款'"
          style="width: 450px"
          size="large"
          @change="handleReaderChange"
        >
          <el-option
            :value="-1"
            label="🔴 [管理员模式] 显示所有未缴纳罚款"
            style="color: #f56c6c; font-weight: bold; border-bottom: 1px dashed #eee"
          />
          
          <el-option
            v-for="item in readerOptions"
            :key="item.card_id"
            :label="item.displayLabel"
            :value="item.card_id"
          />
        </el-select>
      </div>

      <transition name="el-zoom-in-top">
        <div class="stats-row" v-if="currentCardId && currentCardId !== -1">
          <div class="stat-card red-card">
            <div class="stat-title">该读者未缴总额</div>
            <div class="stat-value">￥{{ totalUnpaid }}</div>
          </div>
          <div class="stat-card blue-card">
            <div class="stat-title">历史罚单总数</div>
            <div class="stat-value">{{ fineList.length }} <span class="unit">笔</span></div>
          </div>
        </div>
      </transition>
      
      <el-alert 
        v-if="currentCardId === -1"
        title="当前为全局视图：仅显示所有未缴纳的罚款记录"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />

      <el-table 
        :data="fineList" 
        style="width: 100%; margin-top: 10px" 
        stripe 
        border
        empty-text="暂无记录，请选择读者或模式"
      >
        <el-table-column prop="id" label="单号" width="80" align="center" />
        
        <el-table-column label="欠款人" width="120" v-if="currentCardId === -1">
          <template #default="scope">
             <el-tag effect="plain">{{ getReaderName(scope.row.card_id) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="amount" label="金额" width="120">
          <template #default="scope">
            <span style="font-weight: bold; color: #f56c6c; font-size: 16px">￥{{ scope.row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="罚款原因" />
        
        <el-table-column prop="is_paid" label="状态" width="100" align="center">
          <template #default="scope">
            <el-tag v-if="scope.row.is_paid === 1" type="success" effect="dark" round>已缴</el-tag>
            <el-tag v-else type="danger" effect="dark" round>未缴</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="150" align="center">
          <template #default="scope">
            <el-button 
              v-if="scope.row.is_paid === 0"
              type="primary" 
              size="small" 
              round
              @click="handlePay(scope.row)"
            >
              立即缴费
            </el-button>
            <span v-else style="color: #c0c4cc; font-size: 12px">已结清</span>
          </template>
        </el-table-column>
      </el-table>

    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Money } from '@element-plus/icons-vue'

const loading = ref(false)
const rawReaders = ref([])
const currentCardId = ref(null)
const fineList = ref([])

onMounted(async () => {
  const res = await request.get('/readers/')
  rawReaders.value = res
})

const readerOptions = computed(() => rawReaders.value.map(r => ({ ...r, displayLabel: `${r.name} (ID: ${r.card_id})` })))

// 计算属性：统计未缴 (仅用于单人模式)
const totalUnpaid = computed(() => fineList.value.filter(item => item.is_paid === 0).reduce((sum, item) => sum + item.amount, 0))

// 辅助函数：通过ID反查人名 (用于全局模式)
const getReaderName = (id) => {
  const r = rawReaders.value.find(item => item.card_id === id)
  return r ? r.name : `ID:${id}`
}

const handleReaderChange = async (val) => {
  loading.value = true
  fineList.value = [] // 清空旧数据
  try {
    if (val === -1) {
      // 模式：获取全部
      const res = await request.get('/fines/all')
      // 前端过滤：只保留未缴的 (is_paid === 0)
      fineList.value = res.filter(item => item.is_paid === 0)
    } else {
      // 模式：获取单人
      const res = await request.get(`/fines/${val}`)
      fineList.value = res
    }
  } finally { 
    loading.value = false 
  }
}

const handlePay = (row) => {
  ElMessageBox.confirm(`确认收取罚款 ￥${row.amount} 元吗？`, '缴费确认', { type: 'warning' }).then(async () => {
    await request.post(`/fines/pay/${row.id}`)
    ElMessage.success('缴费成功！')
    // 刷新数据
    handleReaderChange(currentCardId.value)
  })
}
</script>

<style scoped>
.glass-card {
  border: none;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
  min-height: 500px;
}
.card-header { display: flex; align-items: center; }
.left-panel { display: flex; align-items: center; gap: 12px; }
.icon-box {
  width: 36px; height: 36px; border-radius: 8px;
  display: flex; justify-content: center; align-items: center;
}
.title { font-size: 18px; font-weight: bold; }

.search-section {
  text-align: center;
  margin: 20px 0;
}

.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  border-radius: 12px;
  padding: 20px;
  color: white;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.red-card { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%); color: #fff; }

/* ✨ 颜色优化：更鲜艳的宝蓝色渐变 */
.blue-card { 
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
  color: #fff; 
}

.stat-title { opacity: 0.9; font-size: 14px; margin-bottom: 5px; }
.stat-value { font-size: 28px; font-weight: bold; }
.unit { font-size: 14px; font-weight: normal; }
</style>