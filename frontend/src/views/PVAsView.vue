<script setup lang="ts">
import apiAxios from '@/axios'
import { PvasApi, type PVA } from '@/api-client'
import { computed, onMounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import PVAForm from '@/components/PVAForm.vue'
import router from '@/router'

const pvasApi = new PvasApi(undefined, undefined, apiAxios)
const pvas = ref<PVA[]>([])
const search = ref('')
const selectedPva = ref<PVA | null>(null)
const showModal = ref(false)

const fetchPvas = async () => {
  try {
    const res = await pvasApi.pvasList()
    pvas.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const postPva = async (pva: PVA) => {
  try {
    const res = await pvasApi.pvasCreate(pva)
    if (res.status === 201) {
      alert('Договор успешно создан')
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const filteredPvas = computed(() => {
  return pvas.value.filter((pva) => {
    const matchesSearch = pva.requisites.toLowerCase().includes(search.value.trim().toLowerCase())
      || pva.description?.toLowerCase().includes(search.value.toLowerCase())
    return matchesSearch
  })
})

const onCreate = () => {
  selectedPva.value = null
  showModal.value = true
}

const onSubmit = async (pva: PVA) => {
  await postPva(pva)
  showModal.value = false
  await fetchPvas()
}

const toPvaView = (id: number) => {
  router.push({ name: 'pva', params: { id } })
}

onMounted(fetchPvas)
</script>

<template>
  <div class="gap-4">
    <div class="flex gap-4 justify-end-safe items-center font-bold mb-6">
      <input v-model="search" placeholder="Поиск по тексту"
        class="flex-1 font-normal input rounded-lg border-gray-500 p-4 bg-white shadow-md" />
      <button @click="onCreate"
        class="cursor-pointer text-white bg-teal-600 shadow-md rounded-lg py-2 px-10 font-bold hover:bg-teal-700">
        Добавить
      </button>
    </div>
    <div class="flex text-end text-gray-700 font-bold gap-6 px-6">
      <div class="flex-none text-start">ID</div>
      <div class="flex-2/5 text-start">Реквизиты</div>
      <div class="flex-1/5">Статус</div>
      <div class="flex-1/5">Начало действия</div>
      <div class="flex-1/5">Окончание действия</div>
    </div>
    <ul class="divide-y divide-gray-300">
      <li v-for="pva in filteredPvas" :key="pva.id" @click="selectedPva = pva" @dblclick="toPvaView(pva.id!)"
        class="cursor-pointer bg-gray-50 shadow-md rounded-lg py-4 mb-2">
        <div class="flex text-end gap-6 px-6">
          <div class="flex-none text-start"> {{ pva.id }}</div>
          <div class="flex-2/5 text-start">{{ pva.requisites }}</div>
          <div class="flex-1/5"> {{ pva.status_display }}</div>
          <div class="flex-1/5"> {{ pva.start_date ? new Date(pva.start_date).toLocaleDateString('ru-RU') : 'Не указано' }}</div>
          <div class="flex-1/5"> {{ pva.end_date ? new Date(pva.end_date).toLocaleDateString('ru-RU') : 'Не указано' }}</div>
        </div>
      </li>
    </ul>
    <!-- <p>{{ selectedPva }}</p> -->

    <Teleport to="body" v-if="showModal">
    <div class="overlay">
      <div class="modal">
        <PVAForm :pva="selectedPva" :mode="'create'" @close="showModal = false" @submit="onSubmit" />
      </div>
    </div>
  </Teleport>
  </div>

</template>

<style scoped>
.overlay {
  position: fixed;
  z-index: 998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
}

.modal {
  position: fixed;
  z-index: 999;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  height: 80%;
  min-width: min-content;
  width: 40%;
}
</style>