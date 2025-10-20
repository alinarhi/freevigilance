import axios from 'axios'
import { useUserStore } from '@/stores/user'

const isDev = import.meta.env.DEV

const apiAxios = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

// REQUEST: Attach token if available
apiAxios.interceptors.request.use(req => {
  if (isDev) {
    console.log('Axios Request', req)
  }
  const store = useUserStore()
  if (store.accessToken && !store.isAccessTokenExpired) {
    req.headers.Authorization = `Bearer ${store.accessToken}`
  }
  return req
})


apiAxios.interceptors.response.use(
  res => {
    if (isDev) {
      console.log('Axios Response', res)
    }
    return res
  },
  async error => {
    console.error('Axios Error', error)
    const store = useUserStore()

    const originalRequest = error.config

    // try to refresh token if 401 
    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      store.refreshToken &&
      !store.isRefreshTokenExpired
    ) {
      originalRequest._retry = true
      try {
        await store.refresh()
        originalRequest.headers.Authorization = `Bearer ${store.accessToken}`
        return apiAxios(originalRequest)
      } catch (e) {
        store.logout()
      }
    }

    return Promise.reject(error)
  }
)

export default apiAxios
