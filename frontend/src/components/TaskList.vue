<script setup lang="ts">
import TaskListItem from '@/components/TaskListItem.vue'
import { TasksApi, Configuration, type Task } from '@/api-client'
import { ref, computed, onMounted, watch } from 'vue'


const props = defineProps<{
  tasks: Task[],
}>()

defineEmits<{
  (e: 'selectTask', task: Task): void
  (e: 'openTask', task: Task): void
}>()

const groupedTasks = computed(() => {
  const groups: Record<string, Task[]> = {}
  props.tasks.forEach((task) => {
    const date = new Date(task.deadline).toLocaleDateString('ru-RU')
    if (!groups[date]) groups[date] = []
    groups[date].push(task)
  })

  return Object.entries(groups).map(([deadline, tasks]) => ({
    deadline,
    tasks,
  }))
})
</script>



<template>
  <div>
    <div v-for="group in groupedTasks" :key="group.deadline" class="mb-6">
      <h3 class="font-semibold text-lg mb-2 ml-4">До {{ group.deadline }}</h3>
      <TaskListItem v-for="task in group.tasks" :key="task.id" :task="task" @click="$emit('selectTask', task)" @dblclick="$emit('openTask', task)"
        class="cursor-pointer gap-2" />
    </div>
  </div>
</template>
