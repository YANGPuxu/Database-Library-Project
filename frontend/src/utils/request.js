import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 这里指向你的 Python 后端地址
  timeout: 5000 // 请求超时时间
})

// 响应拦截器：如果有报错，这里会自动弹出红色提示
service.interceptors.response.use(
  response => {
    // 自动剥离外层数据，直接返回后端给的内容
    return response.data
  },
  error => {
    const msg = error.response?.data?.detail || '请求失败，请检查后端是否启动'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default service