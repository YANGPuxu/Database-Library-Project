<template>
  <div class="page-container">
    <el-card class="glass-card">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="custom-tabs">
        
        <el-tab-pane label="出版社管理" name="publisher">
          <div class="action-bar">
            <el-input v-model="searchPub" placeholder="搜索出版社名称/地址..." prefix-icon="Search" style="width: 250px" clearable />
            <el-button type="primary" class="gradient-btn" @click="openPubDialog()" round>
              <el-icon><Plus /></el-icon> 新增出版社
            </el-button>
          </div>
          <el-table :data="filteredPubList" stripe border style="margin-top: 15px; border-radius: 8px; overflow: hidden">
            <el-table-column prop="id" label="ID" width="80" align="center" />
            <el-table-column prop="name" label="出版社名称" />
            <el-table-column prop="address" label="地址" />
            <el-table-column label="操作" width="180" align="center">
              <template #default="scope">
                <el-button size="small" link type="primary" @click="openPubDialog(scope.row)">编辑</el-button>
                <el-button size="small" link type="danger" @click="delPub(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="图书库" name="book">
          <div class="action-bar">
            <el-input v-model="searchBook" placeholder="搜索书名 / 作者 / ISBN / 出版社..." prefix-icon="Search" style="width: 250px" clearable />
            <el-button type="primary" class="gradient-btn" @click="openBookDialog()" round>
              <el-icon><Plus /></el-icon> 新增图书
            </el-button>
          </div>
          <el-table :data="filteredBookList" stripe border style="margin-top: 15px; border-radius: 8px; overflow: hidden">
            <el-table-column prop="isbn" label="ISBN" width="140" />
            <el-table-column prop="title" label="书名" min-width="150">
               <template #default="scope"><span style="font-weight: 600">{{ scope.row.title }}</span></template>
            </el-table-column>
            <el-table-column prop="author" label="作者" width="200" />
            <el-table-column label="出版社" width="250">
              <template #default="scope"><el-tag effect="plain" type="info">{{ getPubName(scope.row.publisher_id) }}</el-tag></template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100" />
            <el-table-column prop="stock_qty" label="库存" width="90" align="center">
               <template #default="scope">
                 <el-tag :type="scope.row.stock_qty > 0 ? 'success' : 'danger'" effect="dark" round>{{ scope.row.stock_qty }}</el-tag>
               </template>
            </el-table-column>
            <el-table-column label="操作" width="150" align="center">
              <template #default="scope">
                <el-button size="small" link type="primary" @click="openBookDialog(scope.row)">编辑</el-button>
                <el-button size="small" link type="danger" @click="delBook(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="馆藏入库" name="inventory">
          <div class="action-bar">
            <el-input v-model="searchInv" placeholder="搜索书名 / 条码 / 出版社..." prefix-icon="Search" style="width: 250px" clearable />
            <el-button type="success" class="gradient-btn-success" @click="openInvDialog" round>
              <el-icon><Plus /></el-icon> 新书入库
            </el-button>
          </div>
          <el-table :data="filteredInvList" stripe border style="margin-top: 15px; border-radius: 8px; overflow: hidden">
            <el-table-column prop="id" label="条码ID" width="100" align="center">
               <template #default="scope"><span style="font-weight: bold; color: #67c23a">#{{ scope.row.id }}</span></template>
            </el-table-column>
            
            <el-table-column label="图书信息" min-width="250">
              <template #default="scope">
                <div style="display: flex; flex-direction: column;">
                  <span style="font-weight: bold; font-size: 14px">{{ getBookInfo(scope.row.isbn).title }}</span>
                  <div style="font-size: 12px; color: #909399; margin-top: 3px;">
                    ISBN: {{ scope.row.isbn }} | 
                    {{ getBookInfo(scope.row.isbn).publisher }}
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="状态" align="center" width="120">
              <template #default="scope">
                <el-tag v-if="scope.row.status === 1" type="success" effect="dark" round>在馆</el-tag>
                <el-tag v-else-if="scope.row.status === 0" type="warning" effect="dark" round>已借出</el-tag>
                <el-tag v-else type="danger" effect="dark" round>异常</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="scope">
                <el-button size="small" link type="danger" @click="delInv(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>

      <el-dialog v-model="pubVisible" :title="isEdit ? '编辑出版社' : '新增出版社'" width="400px" align-center append-to-body>
        <el-form :model="pubForm" label-width="80px">
          <el-form-item label="名称"><el-input v-model="pubForm.name" /></el-form-item>
          <el-form-item label="地址"><el-input v-model="pubForm.address" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="pubVisible=false" round>取消</el-button>
          <el-button type="primary" @click="submitPub" round>确定</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="bookVisible" :title="isEdit ? '编辑图书' : '新增图书'" width="500px" align-center append-to-body>
        <el-form :model="bookForm" label-width="80px">
          <el-form-item label="ISBN"><el-input v-model="bookForm.isbn" :disabled="isEdit" /></el-form-item>
          <el-form-item label="书名"><el-input v-model="bookForm.title" /></el-form-item>
          <el-form-item label="作者"><el-input v-model="bookForm.author" /></el-form-item>
          <el-form-item label="出版社">
             <el-select v-model="bookForm.publisher_id" style="width: 100%">
               <el-option v-for="item in pubList" :key="item.id" :label="item.name" :value="item.id" />
             </el-select>
          </el-form-item>
          <el-form-item label="价格"><el-input v-model="bookForm.price" type="number" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="bookVisible=false" round>取消</el-button>
          <el-button type="primary" @click="submitBook" round>确定</el-button>
        </template>
      </el-dialog>

      <el-dialog v-model="invVisible" title="新书入库" width="400px" align-center append-to-body>
        <el-form :model="invForm" label-width="80px">
          <el-form-item label="选择图书">
            <el-select v-model="invForm.isbn" filterable style="width: 100%">
              <el-option v-for="item in bookList" :key="item.isbn" :label="item.title" :value="item.isbn" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="invVisible=false" round>取消</el-button>
          <el-button type="primary" @click="submitInv" round>入库</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import request from '../utils/request'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'

const activeTab = ref('publisher')
const isEdit = ref(false)
const pubList = ref([])
const bookList = ref([])
const invList = ref([])

// 搜索关键词
const searchPub = ref('')
const searchBook = ref('')
const searchInv = ref('')

// 辅助函数：根据出版社ID找到名字
const getPubName = (id) => {
  const pub = pubList.value.find(item => item.id === id)
  return pub ? pub.name : `ID:${id}`
}

// ✨ 辅助函数：根据ISBN获取书名和出版社
const getBookInfo = (isbn) => {
  const book = bookList.value.find(b => b.isbn === isbn)
  if (!book) return { title: '未知图书', publisher: '-' }
  const pubName = getPubName(book.publisher_id)
  return { title: book.title, publisher: pubName }
}

const fetchAll = async () => {
  const [res1, res2, res3] = await Promise.all([
    request.get('/publishers/'),
    request.get('/books/'),
    request.get('/inventory/')
  ])
  pubList.value = res1
  bookList.value = res2
  invList.value = res3
}

onMounted(() => fetchAll())
const handleTabChange = () => fetchAll()

// ✨ 3个计算属性：实现前端过滤
// ✨ 1. 出版社过滤：支持搜名字 + 地址
const filteredPubList = computed(() => {
  if (!searchPub.value) return pubList.value
  const q = searchPub.value.toLowerCase()
  return pubList.value.filter(item => 
    item.name.toLowerCase().includes(q) || 
    (item.address && item.address.toLowerCase().includes(q)) // 增加搜地址
  )
})

// ✨ 2. 图书过滤：支持搜书名 + ISBN + 作者 + 出版社名
const filteredBookList = computed(() => {
  if (!searchBook.value) return bookList.value
  const q = searchBook.value.toLowerCase()
  return bookList.value.filter(item => {
    // 获取出版社名字用于搜索
    const pubName = getPubName(item.publisher_id).toLowerCase()
    
    return item.title.toLowerCase().includes(q) || 
           item.isbn.includes(q) || 
           item.author.toLowerCase().includes(q) ||
           pubName.includes(q) // 增加搜出版社
  })
})

// ✨ 3. 馆藏过滤：支持搜条码 + 书名 + 出版社名
const filteredInvList = computed(() => {
  if (!searchInv.value) return invList.value
  const q = searchInv.value.toLowerCase()
  return invList.value.filter(item => {
    const bookInfo = getBookInfo(item.isbn)
    const title = bookInfo.title.toLowerCase()
    const pub = bookInfo.publisher.toLowerCase()
    
    return String(item.id).includes(q) || 
           title.includes(q) || 
           pub.includes(q) // 增加搜出版社
  })
})

// --- 增删改逻辑保持不变 (复制即可) ---
// --- 出版社 ---
const pubVisible = ref(false)
const pubForm = reactive({ id: null, name: '', address: '' })
const openPubDialog = (row = null) => { isEdit.value = !!row; pubVisible.value = true; if (row) Object.assign(pubForm, row); else { pubForm.id = null; pubForm.name = ''; pubForm.address = '' } }
const submitPub = async () => { isEdit.value ? await request.put(`/publishers/${pubForm.id}`, pubForm) : await request.post('/publishers/', pubForm); ElMessage.success('操作成功'); pubVisible.value = false; fetchAll() }
const delPub = (row) => { ElMessageBox.confirm('确认删除？').then(async () => { await request.delete(`/publishers/${row.id}`); ElMessage.success('删除成功'); fetchAll() }) }
// --- 图书 ---
const bookVisible = ref(false)
const bookForm = reactive({ isbn: '', title: '', author: '', publisher_id: null, price: 0 })
const openBookDialog = (row = null) => { isEdit.value = !!row; bookVisible.value = true; if (row) Object.assign(bookForm, row); else { bookForm.isbn = ''; bookForm.title = ''; bookForm.author = ''; bookForm.publisher_id = null; bookForm.price = 0 } }
const submitBook = async () => { isEdit.value ? await request.put(`/books/${bookForm.isbn}`, bookForm) : await request.post('/books/', bookForm); ElMessage.success('操作成功'); bookVisible.value = false; fetchAll() }
const delBook = (row) => { ElMessageBox.confirm('确认删除？').then(async () => { await request.delete(`/books/${row.isbn}`); ElMessage.success('删除成功'); fetchAll() }) }
// --- 馆藏 ---
const invVisible = ref(false)
const invForm = reactive({ isbn: '' })
const openInvDialog = () => { invForm.isbn = ''; invVisible.value = true }
const submitInv = async () => { await request.post('/inventory/', invForm); ElMessage.success('入库成功'); invVisible.value = false; fetchAll() }
const delInv = (row) => { ElMessageBox.confirm('确认报废/删除？').then(async () => { await request.delete(`/inventory/${row.id}`); ElMessage.success('删除成功'); fetchAll() }) }
</script>

<style scoped>
.page-container { padding: 5px; }
.glass-card { border: none; background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border-radius: 16px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05); }
.action-bar { background-color: #f8faff; padding: 15px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border: 1px solid #eef2f8; }
.gradient-btn { background: linear-gradient(90deg, #409eff 0%, #3a8ee6 100%); border: none; }
.gradient-btn-success { background: linear-gradient(90deg, #67c23a 0%, #85ce61 100%); border: none; }
</style>