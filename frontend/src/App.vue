<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useUserStore } from './stores/user';
import { ref, computed, onMounted } from 'vue';

const userStore = useUserStore()
const route = useRoute()
const showSidebar = computed(() => route.name !== 'login') 
// onMounted(() => {
//   // console.log('user from localStorage:', localStorage.getItem('user'))
//   // console.log('user from userStore:', userStore.user)
//   // console.log('token from localStorage:', localStorage.getItem('access_token'))
//   // console.log('token from userStore:', userStore.accessToken)
  
//   // userStore.fetchUser()
// })
</script>

<template>
<header><h1 class="text-white bg-teal-700 text-2xl font-extrabold p-4">Freevigilance</h1></header>
<div class="flex h-screen">
    <aside v-if="showSidebar" class="w-64 text-white p-4 bg-teal-700/70">
      <div v-if="userStore.user">
        <h2 class="font-bold text-lg">{{ userStore.user.first_name + ' ' + userStore.user.last_name }}</h2>
        <p class="text-gray-200 italic">{{ userStore.user.email }}</p>
        <p class="font-semibold">{{ userStore.user.username }}</p>
      </div>
      <br>
      <hr class="text-teal-700">
      <br>
      <nav>
        <ul class="space-y-2">
          <li><RouterLink to="/tasks" class="link font-semibold">Задачи</RouterLink></li>
          <li><RouterLink to="/pvas" class="link font-semibold">Договоры</RouterLink></li>
          <li><RouterLink to="/auditlog" class="link font-semibold">Журнал действий</RouterLink></li>
        </ul>
      </nav>
    </aside>
    <main class="flex-1 overflow-y-auto p-10 bg-gray-100">
      <RouterView />
    </main>
</div>
</template>

