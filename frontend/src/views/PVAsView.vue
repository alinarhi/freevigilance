<script setup lang="ts">
import apiAxios from '@/axios'
import { PVAStatusEnum, PvasApi, type PVA } from '@/api-client'
import { computed, onMounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import AppModal from '@/components/AppModal.vue'
import PVAForm from '@/components/PVAForm.vue'
import { useRouter, useRoute } from 'vue-router'
import ButtonFilter from '@/components/ButtonFilter.vue'
import PVAFiltersForm, { type PvaFilters } from '@/components/PVAFiltersForm.vue'

const router = useRouter()
const route = useRoute()
const pvasApi = new PvasApi(undefined, undefined, apiAxios)
const fetchedPvas = ref<PVA[]>([])

const pvas = computed(() => {
  return fetchedPvas.value.filter((pva) => {
    const matchesSearch = pva.requisites.toLowerCase().includes(search.value.toString().trim().toLowerCase())
      || pva.description?.toLowerCase().includes(search.value.toString().toLowerCase())
    return matchesSearch
  })
})

const search = computed({
  get: () => route.query.search ?? '',
  set: (search) => router.replace({ query: { ...route.query, search: search } })
})
const showModal = ref(false)
const showFiltersForm = ref(false)
const pvaFilters = ref<PvaFilters>({})

const fetchPvas = async () => {
  try {
    const res = await pvasApi.pvasList(
      pvaFilters.value.endDateGte,
      pvaFilters.value.endDateLte,
      pvaFilters.value.medicinalProduct,
      undefined,
      pvaFilters.value.startDateGte,
      pvaFilters.value.startDateLte,
      pvaFilters.value.status
    )
    fetchedPvas.value = res.data
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

const onFiltersFormSubmit = async (filters: PvaFilters) => {
  pvaFilters.value = { ...filters }
  await router.replace({ query: { ...route.query, ...filters } })
  await fetchPvas()
  showFiltersForm.value = false
}

const onFormSubmit = async (pva: PVA) => {
  await postPva(pva)
  showModal.value = false
  await fetchPvas()
}

const toPvaView = (id: number) => {
  router.push({ name: 'pva', params: { id } })
}

onMounted(async () => {
  pvaFilters.value = {
    startDateGte: route.query.startDateGte?.toString(),
    startDateLte: route.query.startDateLte?.toString(),
    endDateGte: route.query.endDateGte?.toString(),
    endDateLte: route.query.endDateLte?.toString(),
    medicinalProduct: route.query.medicinalProduct?.toString(),
    status: route.query.status?.toString() as PVAStatusEnum
  }
  console.log(pvaFilters.value)
  await fetchPvas()
})
</script>

<template>
  <div class="flex flex-col h-full overflow-hidden">
    <!-- Search Header -->
    <div class="flex gap-4 justify-end-safe items-center font-bold mb-6">
      <ButtonFilter @click="showFiltersForm = true" />
      <input v-model="search" placeholder="Поиск по тексту"
        class="flex-1 font-normal input rounded-lg border-gray-500 p-4 bg-white shadow-md" />
      <button @click="showModal = true"
        class="cursor-pointer text-white bg-teal-600 shadow-md rounded-lg py-3 px-10 font-bold hover:bg-teal-700">
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
    <br>
    <ul class="flex-1 overflow-y-auto divide-y divide-gray-300">
      <li v-for="pva in pvas" :key="pva.id" @dblclick="toPvaView(pva.id!)"
        class="cursor-pointer bg-white shadow-md rounded-lg py-4 mb-2">
        <div class="flex text-end gap-6 px-6">
          <div class="flex-none text-start text-gray-600"> {{ pva.id }}</div>
          <div class="flex-2/5 text-start font-semibold">{{ pva.requisites }}</div>
          <div class="flex-1/5"> {{ pva.status_display }}</div>
          <div class="flex-1/5"> {{ pva.start_date ? new Date(pva.start_date).toLocaleDateString('ru-RU') : 'Не указано' }}</div>
          <div class="flex-1/5"> {{ pva.end_date ? new Date(pva.end_date).toLocaleDateString('ru-RU') : 'Не указано' }}
          </div>
        </div>
      </li>
    </ul>

    <AppModal v-if="showModal">
      <PVAForm :mode="'create'" @close="showModal = false" @submit="onFormSubmit" />
    </AppModal>

    <AppModal v-if="showFiltersForm">
      <PVAFiltersForm :filters="pvaFilters" @close="showFiltersForm = false" @submit="onFiltersFormSubmit" />
    </AppModal>
  </div>
</template>