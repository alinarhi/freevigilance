<script setup lang="ts">
import { TaskStatusEnum, type Task } from '@/api-client';

const props = defineProps<{
  task: Task,
  showButtons: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'edit'): void
  (e: 'details'): void
}>();
</script>

<template>
  <div class="relative bg-white p-4 text-lg">
    <div class="text-sm text-gray-600">
      <p> Договор: {{ task.pva_display }}</p>
      <p> Обязательство: {{ task.obligation_display }} </p>
      <p> Тип обязательства: {{ task.responsibility_type_display }} </p>
      <hr class="text-gray-300 mt-2 mb-4">
      <!-- <p class="text-lg"> Задача #{{ task.id }} </p> -->
    </div>

    <div class="text-2xl font-bold"> {{ task.title }}</div>
    <div class="font-semibold text-teal-700">До: {{ new Date(task.deadline).toLocaleString('ru-RU') }}</div>

    <br>
    <div class="text-sm">
      <p class="text-gray-600"> ID: {{ task.id }}</p>
      <p> Статус: {{ task.status_display }}</p>
      <p v v-if="task.status === TaskStatusEnum.Completed"> Подтверждение выполнения: {{ task.completion_evidence_link }}</p>
      <p v-if="task.is_recurring"> Повтор: {{ task.schedule?.frequency_type }}</p>
      <p> Исполнитель: {{ task.assigned_to_display ?? 'Не назначен' }} </p>
      <p> Создана: {{ task.created_by_display }} </p>
      <br>

      <!-- <p> Описание: </p> -->
    </div>

    <!-- <textarea disabled class="text-gray-600 w-full border border-gray-300 rounded-lg px-1 py-1"> {{ task.description }} </textarea> -->
    <div class="text-gray-600 italic"> {{ task.description }}</div>

    <hr class="text-gray-300 mt-20 mb-4">
    <div v-if="showButtons" class="flex gap-4">
      <button v-if="task.status === TaskStatusEnum.NotStarted || task.status === TaskStatusEnum.InProgress " @click="$emit('edit')"
        class="cursor-pointer px-4 py-2 text-white font-bold bg-teal-600 hover:bg-teal-700 rounded-lg shadow-md">
        Редактировать
      </button>
      <button @click="$emit('details')" class="cursor-pointer px-4 py-2 font-semibold">
        Подробнее
      </button>
    </div>

    <button v-if="showButtons" @click="$emit('close')"
      class="cursor-pointer absolute top-4 right-4 px-4 py-1 font-bold bg-gray-300 rounded-lg shadow-md hover:bg-gray-400">x</button>
  </div>
</template>