<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { PVA, MedicinalProduct } from '@/api-client'
import { PVAStatusEnum, MedicinalProductsApi } from '@/api-client'
import { PVAStatusDisplay } from '@/utils/constants'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'

export type FormMode = 'create' | 'edit'
const medsApi = new MedicinalProductsApi(undefined, undefined, apiAxios)

const props = defineProps<{
  mode: FormMode
  pva?: PVA | undefined
}>()

const emit = defineEmits<{
  (e: 'submit', data: PVA): void
  (e: 'close'): void
}>()

const form = ref<PVA>({
  requisites: '',
  description: '',
  status: PVAStatusEnum.Active,
  medicinal_products: [],
  pva_link: '',
  main_contract_link: '',
  start_date: null,
  end_date: null,
})

const medInput = ref<string>('')
const meds = ref<MedicinalProduct[]>([])
const fetchMeds = async () => {
  try {
    const res = await medsApi.medicinalProductsList()
    meds.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}
const medsList = computed(() => {
  return meds.value.map((med => med.title))
})

const handleSubmit = () => {
  if (form.value.start_date === "") {
    form.value.start_date = null
  }
  if (form.value.end_date === "") {
    form.value.end_date = null
  }
  if (form.value.start_date && form.value.end_date && new Date(form.value.start_date) >= new Date(form.value.end_date)) {
    alert('Выбран некорректный интервал дат')

  } else {
    emit('submit', form.value)
  }
}

onMounted(async () => {
  if (props.pva) {
    form.value = {
      ...props.pva,
    }
  }
  await fetchMeds()
})
</script>

<template>
  <form @submit.prevent="handleSubmit" class="h-full p-6 bg-white rounded-2xl shadow-md space-y-6">
    <div>
      <div class="flex-none text-xl mb-4 font-extrabold text-teal-900">{{ mode === 'create' ? 'Добавление' :
        'Редактирование' }} договора
      </div>

      <label class="block mb-1 font-semibold text-gray-700">Реквизиты</label>
      <input v-model="form.requisites" type="text"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        required />
    </div>

    <div>
      <label class="block mb-1 font-semibold text-gray-700">Лекарственные препараты</label>
      <!-- <input v-if="mode !== 'readonly'" v-model="medInput" list="medsList" type="text"
        class=" border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
      <datalist id="medsList">
        <option v-for="med in meds" :key="med.id" :value="med.title" />
      </datalist> -->
      <select v-model="form.medicinal_products" multiple
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
        <option v-for="med in meds" :key="med.id" :value="med.title">
          {{ med.title }}
        </option>
      </select>
    </div>

    <div>
      <label class="block mb-1 font-semibold text-gray-700">Статус</label>
      <select v-model="form.status"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        required>
        <option v-for="status in Object.values(PVAStatusEnum)" :key="status" :value="status">
          {{ PVAStatusDisplay[status] }}
        </option>
      </select>
    </div>

    <div>
      <label class="block mb-1 font-semibold text-gray-700">Ссылка на основной контракт</label>
      <input v-model="form.main_contract_link" type="text"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
    </div>

    <div>
      <label class="block mb-1 font-semibold text-gray-700">Ссылка на контракт по фармакобезопасности</label>
      <input v-model="form.pva_link" type="text"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
    </div>


    <div class="flex items-center gap-2">
      <label class="block mb-1 font-semibold text-gray-700">Сроки: с</label>
      <input v-model="form.start_date" type="date"
        class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
      <label class="block mb-1 font-semibold text-gray-700">по</label>
      <input v-model="form.end_date" type="date"
        class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
    </div>


    <div>
      <label class="block mb-1 font-semibold text-gray-700">Описание</label>
      <textarea v-model="form.description"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        rows="3" />
    </div>


    <div class="flex gap-4 font-semibold">
      <button type="submit"
        class="cursor-pointer px-6 py-2 bg-teal-600 text-white font-bold rounded-lg shadow-md hover:bg-teal-700">
        Сохранить
      </button>
      <button @click="emit('close')" class="cursor-pointer text-gray-700">Отмена</button>
    </div>
  </form>
</template>