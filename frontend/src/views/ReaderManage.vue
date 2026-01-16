<template>
  <div class="page-container">
    <el-card class="glass-card">
      <template #header>
        <div class="card-header">
          <div class="left-panel">
            <div class="icon-box"><el-icon><User /></el-icon></div>
            <span class="title">读者信息管理</span>
          </div>
          <div class="right-panel">
            <el-input
              v-model="searchQuery"
              placeholder="搜索姓名或学号..."
              prefix-icon="Search"
              clearable
              style="width: 200px; margin-right: 15px"
            />
            <el-button type="primary" class="gradient-btn" @click="handleAdd" round>
              <el-icon style="margin-right: 5px"><Plus /></el-icon> 新增读者
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="filteredTableData" style="width: 100%" stripe :header-cell-style="{background:'#f5f7fa', color:'#606266'}" v-loading="loading">
        <el-table-column prop="card_id" label="学号/借书证" width="150">
          <template #default="scope">
            <el-tag type="info" effect="plain" round>{{ scope.row.card_id }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" label="姓名" width="150">
          <template #default="scope"><span style="font-weight: 600">{{ scope.row.name }}</span></template>
        </el-table-column>
        
        <el-table-column prop="category" label="类别">
          <template #default="scope">
            <el-tag :type="getCategoryType(scope.row.category)" effect="light" round>{{ scope.row.category }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="borrowed_count" label="当前已借">
          <template #default="scope">
             <span :style="{color: scope.row.borrowed_count > 0 ? '#409eff' : '#909399', fontWeight: 'bold'}">
               {{ scope.row.borrowed_count }} 本
             </span>
          </template>
        </el-table-column>

        <el-table-column label="账户状态" width="120" align="center">
          <template #default="scope">
            <el-tag 
              v-if="scope.row.unpaid_fine_count > 0" 
              type="danger" 
              effect="dark" 
              round
            >
              欠款 {{ scope.row.unpaid_fine_count }} 笔
            </el-tag>
            
            <el-tag 
              v-else 
              type="success" 
              effect="dark" 
              round
            >
              正常
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" align="center">
          <template #default="scope">
            <el-button size="small" link type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-dialog v-model="dialogVisible" :title="dialogTitle" width="400px" class="custom-dialog" align-center append-to-body>
        <el-form :model="form" label-width="70px" style="padding: 10px 20px 0 0">
          <el-form-item label="姓名"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="类别">
            <el-select v-model="form.category" style="width: 100%">
              <el-option label="学生" value="学生" /><el-option label="教师" value="教师" /><el-option label="校外人员" value="校外人员" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false" round>取消</el-button>
            <el-button type="primary" class="gradient-btn" @click="handleSubmit" round>确定</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, Search, Warning, CircleCheck } from '@element-plus/icons-vue'

const tableData = ref([])
const loading = ref(false)
const searchQuery = ref('') // 🔍 搜索关键词

const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEdit = ref(false)
const form = reactive({ card_id: null, name: '', category: '' })

// ✨ 计算属性：前端实时过滤
const filteredTableData = computed(() => {
  if (!searchQuery.value) return tableData.value
  const q = searchQuery.value.toLowerCase()
  return tableData.value.filter(item => 
    item.name.includes(q) || String(item.card_id).includes(q)
  )
})

const getCategoryType = (cat) => {
  if (cat === '教师') return 'warning'
  if (cat === '校外人员') return 'danger'
  return 'success'
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await request.get('/readers/')
    tableData.value = res
  } finally { loading.value = false }
}

onMounted(() => fetchData())

// 下面的增删改逻辑保持不变...
const handleAdd = () => { isEdit.value = false; dialogTitle.value = '新增读者'; form.card_id = null; form.name = ''; form.category = '学生'; dialogVisible.value = true }
const handleEdit = (row) => { isEdit.value = true; dialogTitle.value = '编辑读者'; Object.assign(form, row); dialogVisible.value = true }
const handleSubmit = async () => {
  if (!form.name) return ElMessage.warning('请输入姓名')
  try {
    isEdit.value ? await request.put(`/readers/${form.card_id}`, form) : await request.post('/readers/', form)
    ElMessage.success('操作成功'); dialogVisible.value = false; fetchData()
  } catch (err) {}
}
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除读者 "${row.name}" 吗？`, '警告', { type: 'warning' }).then(async () => {
    await request.delete(`/readers/${row.card_id}`); ElMessage.success('删除成功'); fetchData()
  })
}
</script>

<style scoped>
/* 保持之前的样式 */
.page-container { padding: 5px; }
.glass-card { border: none; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border-radius: 16px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.left-panel, .right-panel { display: flex; align-items: center; gap: 12px; }
.icon-box { width: 36px; height: 36px; background: #ecf5ff; border-radius: 8px; display: flex; justify-content: center; align-items: center; color: #409eff; }
.title { font-size: 18px; font-weight: bold; color: #303133; }
.gradient-btn { background: linear-gradient(90deg, #409eff 0%, #3a8ee6 100%); border: none; }
.gradient-btn:hover { opacity: 0.9; transform: translateY(-1px); }
</style>