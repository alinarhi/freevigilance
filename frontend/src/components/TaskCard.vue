<script setup lang="ts">
import { TaskStatusEnum, type Task, type TaskStatus } from '@/api-client';
import { FrequencyTypeDisplay } from '@/utils/constants';
import { PencilIcon, PlayIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/solid';
import { ref } from 'vue';

const completion_evidence = ref('')

const props = defineProps<{
  task: Task,
  showEditButton: boolean,
  showDetailsButton: boolean,
  showChangeStatusButton: boolean
}>()

defineEmits<{
  (e: 'close'): void
  (e: 'edit'): void
  (e: 'openDetails'): void
  (e: 'changeStatus', status: TaskStatus): void
}>();

</script>

<template>
  <div class="flex flex-col h-full overflow-hidden wrap-anywhere bg-white p-4 text-lg">
    <div class="relative">
      <div class="absolute top-0 right-0 flex gap-2">
        <button v-if="showEditButton" @click="$emit('edit')" title="Редактировать"
          class="cursor-pointer p-3 font-bold bg-teal-600 rounded-lg shadow-md hover:bg-teal-700">
          <PencilIcon class="size-5 text-white" />
        </button>
        <button v-if="showDetailsButton" @click="$emit('close')" title="Закрыть"
          class="cursor-pointer py-1 px-2 rounded-lg hover:bg-gray-100">
          <XMarkIcon class="size-7 text-gray-700" />
        </button>
      </div>

      <!-- Header -->
      <div class="text-sm text-gray-600">
        <p> Договор: {{ task.pva_display }}</p>
        <p> Обязательство: {{ task.obligation_display }} </p>
        <p> Тип обязательства: {{ task.responsibility_type_display }} </p>
        <hr class="text-gray-300 mt-2 mb-4">
      </div>

      <!-- Task Info -->
      <div class="text-2xl font-bold"> {{ task.title }}</div>
      <div class="font-semibold text-teal-700">До: {{ new Date(task.deadline).toLocaleString('ru-RU') }}</div>

      <br>
      <div class="text-sm">
        <p class="text-gray-600"> ID: {{ task.id }}</p>
        <p> Статус: {{ task.status_display }}</p>
        <p v v-if="task.status === TaskStatusEnum.Completed"> Подтверждение выполнения: {{ task.completion_evidence_link
          }}</p>
        <p v-if="task.is_recurring && task.schedule?.frequency_type"> Повтор: {{
          FrequencyTypeDisplay[task.schedule.frequency_type] }}</p>
        <p> Исполнитель: {{ task.assigned_to_display ?? 'Не назначен' }} </p>
        <p> Создана: {{ task.created_by_display }} </p>
        <br>

      </div>
    </div>

    <!-- Description -->
    <div class="flex-1 relative overflow-hidden">
      <div class="h-full overflow-y-auto text-gray-600 italic whitespace-pre-line">
        {{ task.description }}
        <br>
        <br>
      </div>
      <!-- Fading effect to make overflow obvious -->
      <div class="absolute bottom-0 left-0 w-full h-6 bg-gradient-to-t from-white to-transparent pointer-events-none">
      </div>
    </div>

    <hr class="text-gray-300 mt-20 mb-4">

    <!-- Buttons -->
    <div class="flex flex-col gap-8">
      <form v-if="showChangeStatusButton && task.status === TaskStatusEnum.InProgress"
        @submit.prevent="$emit('changeStatus', { status: TaskStatusEnum.Completed, completion_evidence_link: completion_evidence })"
        class="flex flex-nowrap gap-2">
        <input v-model.trim="completion_evidence" type="text" placeholder="Подтверждение выполнения (ссылка)"
          class="flex-1 input rounded-lg border border-gray-300 p-2 bg-gray-50" required></input>
        <button type="submit"
          class="inline-flex items-center gap-2 cursor-pointer px-4 py-2 text-white font-semibold bg-teal-600 hover:bg-teal-700 rounded-lg shadow-md">
          Завершить
        </button>
      </form>

      <div class="flex flex-row-reverse justify-between">
        <button v-if="showDetailsButton" @click="$emit('openDetails')"
          class="cursor-pointer px-4 py-2 rounded-lg font-normal hover:bg-gray-100">
          Подробнее
        </button>
        <button v-if="showChangeStatusButton && task.status === TaskStatusEnum.NotStarted"
          @click="$emit('changeStatus', { status: TaskStatusEnum.InProgress })"
          class="inline-flex items-center gap-2 cursor-pointer px-4 py-2 text-white font-semibold bg-teal-600 hover:bg-teal-700 rounded-lg shadow-md">
          Взять в работу
          <PlayIcon class="size-5" />
        </button>
      </div>
    </div>
  </div>
</template>