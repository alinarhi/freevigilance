<script setup lang="ts">
import { TaskStatusEnum, type Task } from '@/api-client'

const props = defineProps<{
  task: Task,
}>()

</script>


<template>
  <div class="relative bg-gray-50 shadow-md rounded-lg p-4 mb-2">
    <div class="flex flex-row font-bold text-end">
      <div class="w-3/5 flex-initial text-start">{{ task.title }}</div>
      <div class="w-1/5 flex-initial">{{ task.assigned_to_display ?? "Не назначен" }} </div>
      <div class="w-1/5 flex-initial">{{ task.status_display }}</div>
    </div>

    <div v-if="task.description?.length" class="max-w-lg truncate text-gray-700">{{ task.description }}</div>
    <div v-else><br></div>
  </div>
</template>