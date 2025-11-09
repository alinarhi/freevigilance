<script setup lang="ts">
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user';
import { ref, computed, onMounted } from 'vue';
import { UserIcon, ArrowRightStartOnRectangleIcon } from '@heroicons/vue/24/solid';

const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const showSidebar = computed(() => route.name !== 'login')

const onLogout = () => {
  userStore.logout()
  router.push('logout')
}
</script>

<template>
  <div class="flex flex-col h-screen overflow-hidden">
    <!-- Topbar -->
    <header class="flex justify-end bg-teal-700 text-white p-4">
      <h1 class="flex-1 text-2xl font-extrabold">Freevigilance</h1>
      <button v-if="userStore.user" @click="onLogout" class="flex-none inline-flex items-center gap-2 cursor-pointer font-semibold">
        Выйти
        <ArrowRightStartOnRectangleIcon class="size-5"/>
      </button>
    </header>

    <div class="flex-1 flex overflow-hidden">
    <!-- Sidebar  -->
    <aside v-if="showSidebar" class="w-64 overflow-y-auto flex-none text-white p-4 bg-teal-700/70">
      <!-- User Info -->
      <div v-if="userStore.user" class="flex flex-col items-center mt-6 mb-6">
        <UserIcon class="size-14 mb-2"/>
        <h2 class="font-bold text-lg">{{ userStore.user.first_name + ' ' + userStore.user.last_name }}</h2>
        <p class="text-gray-200 italic">{{ userStore.user.email }}</p>
        <p class="font-semibold">{{ userStore.user.username }}</p>
      </div>
      <br>
      <hr class="text-teal-700">
      <br>
      <!-- Navigation -->
      <nav>
        <ul class="space-y-2 text-lg text-gray-200 font-semibold">
          <li><RouterLink to="/tasks" activeClass="text-white font-bold">Задачи</RouterLink></li>
          <li><RouterLink to="/pvas" activeClass="text-white font-bold">Договоры</RouterLink></li>
          <li><RouterLink to="/auditlog" activeClass="text-white font-bold">Журнал действий</RouterLink></li>
        </ul>
      </nav>
    </aside>
    <!-- Content -->
    <main class="flex-1 p-10 bg-gray-100">
      <RouterView />
    </main>
    </div>
  </div>

</template>

