<script setup lang="ts">
import { TaskStatusEnum, type Task } from '@/api-client'

const props = defineProps<{
  task: Task,
}>()

</script>


<template>

  <div class="relative bg-gray-50 shadow-md rounded-lg p-4 mb-2">
    <!-- <div class="absolute bottom-1 right-1 text-xs text-gray-600">#{{ task.id }}</div> -->
    <div class="flex flex-row font-bold text-end">
      <div class="flex-3/5 text-start">{{ task.title }}</div>
      <div v-if="task.assigned_to" class="flex-1/5">{{ task.assigned_to_display }} </div>
      <div v-else class="flex-1/5">Не назначен</div>
      <div class="flex-1/5">{{ task.status_display }}</div>
    </div>
    <p class="max-w-xl truncate text-gray-700">{{ task.description }}</p>
  </div>
</template>