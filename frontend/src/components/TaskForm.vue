<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import type { Task, Obligation, PVA, User, TaskSchedule } from '@/api-client'
import { FrequencyTypeEnum, TaskStatusEnum, UsersApi, ObligationsApi, PvasApi } from '@/api-client'
import apiAxios from '@/axios'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'

export type TaskFormMode = 'create' | 'edit' | 'readonly'
const usersApi = new UsersApi(undefined, undefined, apiAxios)
const obligationsApi = new ObligationsApi(undefined, undefined, apiAxios)
const pvasApi = new PvasApi(undefined, undefined, apiAxios)

const frequency_types = new Map();
frequency_types.set(FrequencyTypeEnum.D, 'Ежедневно')
frequency_types.set(FrequencyTypeEnum.W, 'Каждую неделю')
frequency_types.set(FrequencyTypeEnum.M, 'Каждый месяц')
frequency_types.set(FrequencyTypeEnum.Y, 'Каждый год')

const props = defineProps<{
  mode: TaskFormMode
  task?: Task | null
}>()

const emit = defineEmits<{
  (e: 'submit', data: Task): void
  (e: 'close'): void
}>()

const isReadonly = computed(() => props.mode === 'readonly')
const localDeadline = ref<string>('')
const pvaID = ref<number | undefined>()

const form = ref<Task>({
  title: '',
  deadline: '',
  obligation: 0,
  description: '',
  status: TaskStatusEnum.NotStarted,
  is_recurring: false,
  assigned_to: null,
  schedule: {
    frequency_type: undefined,
    // TODO: fix
    start_date: '2000-01-01',
    end_date: ''
  }
})

const users = ref<User[]>([])
const fetchUsers = async () => {
  try {
    const res = await usersApi.usersList()
    users.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const obligations = ref<Obligation[]>([])
const fetchObligations = async (id: number) => {
  try {
    const res = await obligationsApi.pvasObligationsList(id)
    obligations.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

const pvas = ref<PVA[]>([])
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

// Fill form with task's content in edit mode
// watch(
//   () => props.task,
//   (task) => {
//     if (task) {
//       form.value = {
//         ...task,
//       }
//     }
//   },
//   { immediate: true }
// )

watch(localDeadline, (newValue) => {
  if (newValue) {
    console.log(newValue)
    form.value.deadline = new Date(newValue).toISOString()
  }
})

const handleSubmit = () => {
  if (!form.value.is_recurring) {
    form.value.schedule = undefined
  }
  console.log(form.value)
  emit('submit', form.value)
}

onMounted(() => {
  if (props.task) {
    const deadline = new Date(props.task.deadline)

    // TODO: FIX!!!
    localDeadline.value = deadline.toISOString().slice(0, 16)
    
    // localDeadline.value = `${deadline.getFullYear()}-${deadline.getMonth() >= 10 ? deadline.getMonth()}-${deadline.getDay()}T${deadline.getHours()}:${deadline.getMinutes()}`
    form.value = {
      ...props.task,
    }
  }
  if (props.mode !== 'readonly') {
    fetchUsers()
    fetchPvas()
  }
})
</script>

<template>
  <form @submit.prevent="handleSubmit" class="max-h-100% mx-auto p-6 bg-white rounded-2xl shadow-md">

    <div v-if="mode === 'readonly'" class="text-xl mb-4 font-extrabold text-teal-900">Задача #{{ task?.id }}</div>
    <div v-else class="text-xl mb-4 font-extrabold text-teal-900">{{ mode === 'create' ? 'Создание' : 'Редактирование'
    }} задачи</div>

    <div class="space-y-6 overflow-y-auto">
      <div v-if="mode === 'create'">
        <label class="block mb-1 font-semibold text-gray-700">Договор</label>
        <div class="flex gap-4 items-center">
          <div class="flex-1">
            <select v-model="pvaID" :disabled="isReadonly" @change="fetchObligations(pvaID!)"
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
              required>
              <option value="" disabled selected>Выберите договор</option>
              <option v-for="pva in pvas" :key="pva.id" :value="pva.id">
                {{ pva.requisites }} (#{{ pva.id }})
              </option>
            </select>
          </div>
          <div class="flex-none">
            <button class="cursor-pointer font-semibold text-teal-700">
              Добавить
            </button>
          </div>
        </div>
      </div>

      <div v-if="mode === 'create'">
        <label class="block mb-1 font-semibold text-gray-700">Обязательство</label>
        <div class="flex gap-4 items-center">
          <div class="flex-1">
            <select v-model="form.obligation" :disabled="isReadonly || !pvaID"
              class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
              required>
              <option value="" disabled selected>Выберите обязательство</option>
              <option v-for="obligation in obligations" :key="obligation.id" :value="obligation.id">
                {{ obligation.title }} (#{{ obligation.id }})
              </option>
            </select>
          </div>
          <div class="flex-none">
            <button class="cursor-pointer font-semibold text-teal-700">
              Добавить
            </button>
          </div>
        </div>
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Название</label>
        <input v-model="form.title" :disabled="isReadonly" type="text"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
          required />
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Описание</label>
        <textarea v-model="form.description" :disabled="isReadonly"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
          rows="3" />
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Срок выполнения</label>
        <input v-model="localDeadline" :disabled="isReadonly" type="datetime-local"
          class="w-fit border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
          required />
      </div>

      <div v-if="mode !== 'create'">
        <label class="block mb-1 font-semibold text-gray-700">Статус</label>
        <select v-model="form.status" :disabled="isReadonly"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
          <option v-for="status in Object.values(TaskStatusEnum)" :key="status" :value="status">
            {{ status }}
          </option>
        </select>
      </div>

      <div class="flex justify-stretch items-center gap-2">
        <div class="flex items-center gap-2">
          <label for="recurring" class="text-gray-700">Повторять</label>
          <input v-model="form.is_recurring" :disabled="isReadonly" type="checkbox" id="recurring"
            class="rounded border-gray-300 focus:ring-blue-300" />
        </div>

        <div v-if="form.is_recurring">
          <select v-model="form.schedule!.frequency_type"
            class="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
            required>
            <option value="">Выберите тип повторения</option>
            <option v-for="type in Object.values(FrequencyTypeEnum)" :key="type" :value="type">
              {{ frequency_types.get(type) }}
            </option>
          </select>
        </div>

        <label v-if="form.is_recurring" class="text-gray-700">до:</label>

        <div v-if="form.is_recurring">
          <input v-model="form.schedule!.end_date" type="date"
            class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300"
            required />
        </div>
      </div>

      <div v-if="mode === 'readonly'">
        <label class="block mb-1 font-semibold text-gray-700">Создана</label>
        <label class="block mb-1"> {{ form.created_by }}</label>
      </div>

      <div>
        <label class="block mb-1 font-semibold text-gray-700">Назначена</label>
        <select v-model="form.assigned_to" :disabled="isReadonly"
          class="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring focus:ring-blue-300">
          <option value="">Выберите исполнителя</option>
          <option v-for="user in users" :key="user.id" :value="user.id">
            {{ user.last_name }} {{ user.first_name }}
          </option>
        </select>
      </div>

    </div>


    <div class="flex gap-4 font-semibold my-6">
      <button type="submit" :hidden="isReadonly"
        class="cursor-pointer px-6 py-2 bg-teal-600 text-white font-bold rounded-lg shadow-md hover:bg-teal-700">
        Сохранить
      </button>
      <button @click="emit('close')" class="cursor-pointer text-gray-700">Отмена</button>
    </div>
  </form>
</template>

<style scoped>
textarea {
  resize: none;
}
</style>