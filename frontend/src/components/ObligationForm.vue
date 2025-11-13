<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ResponsibilityTypesApi, type Obligation, type ResponsibilityType } from '@/api-client'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'

export type FormMode = 'create' | 'edit'
const typesApi = new ResponsibilityTypesApi(undefined, undefined, apiAxios)

const props = defineProps<{
  mode: FormMode
  pva_id: number
  obligation?: Obligation
}>()

const emit = defineEmits<{
  (e: 'submit', data: Obligation): void
  (e: 'close'): void
}>()

const form = ref<Obligation>({
  title: '',
  description: '',
  start_date: '',
  responsibility_type: '',
  end_date: '',
  pva: props.pva_id,
})

const types = ref<ResponsibilityType[]>([])
const fetchTypes = async () => {
  try {
    const res = await typesApi.responsibilityTypesList()
    types.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const postType = async (type: string) => {
  try {
    const res = await typesApi.responsibilityTypesCreate({ title: type })
    if (res.status === 201) {
      types.value.push(res.data)
    }
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const handleSubmit = async () => {
  if (new Date(form.value.start_date) >= new Date(form.value.end_date)) {
    alert('Выбран некорректный интервал дат')
  } else {
    if (form.value.responsibility_type && !types.value.map(type => type.title).includes(form.value.responsibility_type)) {
      await postType(form.value.responsibility_type)
    }
    emit('submit', form.value)
  }
}

onMounted(async () => {
  if (props.obligation) {
    form.value = {
      ...props.obligation,
    }
  }
  await fetchTypes()
})
</script>

<template>
  <form @submit.prevent="handleSubmit" class="h-full p-6 bg-white rounded-2xl shadow-md space-y-6">

    <div class="flex-none text-xl mb-4 font-extrabold text-teal-900">{{ mode === 'create' ? 'Добавление' :
      'Редактирование' }} обязательства </div>

    <div>
      <label class="block mb-1 font-semibold text-gray-700">Заголовок</label>
      <input v-model="form.title" type="text"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        required />
    </div>

    <div>
      <label class="block mb-1 font-semibold text-gray-700">Тип обязательства</label>
      <input v-model.trim="form.responsibility_type" list="typesList" type="text"
        class=" border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" required/>
      <datalist id="typesList">
        <option v-for="type in types" :key="type.id" :value="type.title" />
      </datalist>
    </div>


    <div class="flex items-center gap-2">
      <label class="block mb-1 font-semibold text-gray-700">Сроки: с</label>
      <input v-model="form.start_date" type="date"
        class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        required />
      <label class="block mb-1 font-semibold text-gray-700">по</label>
      <input v-model="form.end_date" type="date"
        class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        required />
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