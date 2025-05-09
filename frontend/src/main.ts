import './assets/main.css'

import { createApp, watch } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const pinia = createPinia()
const app = createApp(App)

// watch(
//     pinia.state,
//     (state) => {
//         localStorage.setItem("user", JSON.stringify(state.user))
//     },
//     { deep: true }
// )

app.use(pinia)
app.use(router)

app.mount('#app')

