<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ResponsibilityTypesApi, type Obligation, type ResponsibilityType } from '@/api-client'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'

export type FormMode = 'create' | 'edit' | 'readonly'
const typesApi = new ResponsibilityTypesApi(undefined, undefined, apiAxios)

const props = defineProps<{
  mode: FormMode
  pva_id: number
  obligation?: Obligation | null
}>()

const emit = defineEmits<{
  (e: 'submit', data: Obligation): void
  (e: 'close'): void
}>()

const isReadonly = computed(() => props.mode === 'readonly')
const typeInput = ref<string>('')
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
  if (!types.value.map(type => type.title).includes(form.value.responsibility_type)) {
    await postType(form.value.responsibility_type)
  }
  console.log(form.value)
  emit('submit', form.value)
}

onMounted(() => {
  if (props.obligation) {
    form.value = {
      ...props.obligation,
    }
  }
  if (props.mode !== 'readonly') {
    fetchTypes()
  }
})
</script>

<template>
  <form @submit.prevent="handleSubmit"
    class="max-h-100% min-h-100% mx-auto p-6 bg-white rounded-2xl shadow-md space-y-6">

    <div>
      <label v-if="mode !== 'create'" class="block mb-1 font-semibold text-gray-700">Обязательство #{{obligation?.id }}</label>
      <label class="block mb-1 font-semibold text-gray-700">Заголовок</label>
      <input v-model="form.title" :disabled="isReadonly" type="text"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        required />
    </div>

    <div>
      <label class="block mb-1 font-semibold text-gray-700">Тип Обязательства</label>
      <input v-if="mode !== 'readonly'" v-model="form.responsibility_type" list="typesList" type="text"
        class=" border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" />
      <datalist id="typesList">
        <option v-for="type in types" :key="type.id" :value="type.title" />
      </datalist>
    </div>


    <div class="flex items-center gap-2">
      <label class="block mb-1 font-semibold text-gray-700">Сроки: с</label>
      <input v-model="form.start_date" type="date" :disabled="isReadonly"
        class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" required/>
      <label class="block mb-1 font-semibold text-gray-700">по</label>
      <input v-model="form.end_date" type="date" :disabled="isReadonly"
        class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300" required/>
    </div>


    <div>
      <label class="block mb-1 font-semibold text-gray-700">Описание</label>
      <textarea v-model="form.description" :disabled="isReadonly"
        class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
        rows="3" />
    </div>


    <div class="flex gap-4 font-semibold">
      <button type="submit" :hidden="isReadonly" 
        class="cursor-pointer px-6 py-2 bg-teal-600 text-white font-bold rounded-lg shadow-md hover:bg-teal-700">
        Сохранить
      </button>
      <button @click="emit('close')" class="cursor-pointer text-gray-700">Отмена</button>
    </div>
  </form>
</template>