<script setup lang="ts">
import { TaskStatusEnum, type Task, type TaskStatus } from '@/api-client';
import { FrequencyTypeDisplay } from '@/utils/constants';
import ButtonEdit from '@/components/ButtonEdit.vue';
import { PlayIcon, XMarkIcon } from '@heroicons/vue/24/solid';
import { computed, ref } from 'vue';

const completionEvidence = ref('')

const props = defineProps<{
  task: Task,
  showEditButton: boolean,
  showDetailsButton: boolean,
  showChangeStatusButton: boolean
}>()

const deadlineDate = computed(() => new Date(props.task.deadline))
defineEmits<{
  (e: 'close'): void
  (e: 'edit'): void
  (e: 'openDetails'): void
  (e: 'changeStatus', status: TaskStatus): void
}>();

</script>

<template>
  <div class="flex flex-col justify-stretch h-full overflow-hidden wrap-anywhere bg-white p-4 text-lg">
    <div class="flex-none">
      <!-- Header -->
      <div class="flex justify-between items-start">
        <div class="text-sm text-gray-600">
          <p> <span class="font-semibold">Договор: </span>{{ task.pva_display }}</p>
          <p><span class="font-semibold">Обязательство: </span>{{ task.obligation_display }} </p>
          <p><span class="font-semibold"> Тип обязательства: </span>{{ task.responsibility_type_display }} </p>
        </div>

        <div class="flex gap-2">
          <ButtonEdit v-if="showEditButton" @click="$emit('edit')"/>
          <button v-if="showDetailsButton" @click="$emit('close')" title="Закрыть"
            class="cursor-pointer py-1 px-2 rounded-lg hover:bg-gray-100">
            <XMarkIcon class="size-7 text-gray-700" />
          </button>
        </div>
      </div>
      <hr class="text-gray-300 mt-2 mb-4">

      <!-- Task Title -->
      <div class="text-2xl font-bold"> {{ task.title }}</div>
      <div :class="deadlineDate >= new Date() ? 'text-teal-700' : 'text-red-700'" class="font-semibold"><span>До
        </span>{{ deadlineDate.toLocaleString('ru-RU') }}</div>

      <!-- Task Info -->
      <div :class="showDetailsButton ? 'text-sm' : 'text-base'" class="mt-4 mb-4">
        <p class="text-gray-600"> ID: {{ task.id }}</p>
        <p><span class="font-semibold">Статус: </span>{{ task.status_display }}</p>
        <p v v-if="task.status === TaskStatusEnum.Completed" class="truncate"><span class="font-semibold">Подтверждение выполнения:
          </span> <a :href="task.completion_evidence_link">{{ task.completion_evidence_link
          }}</a></p>
        <p v-if="task.is_recurring && task.schedule?.frequency_type"><span class="font-semibold">Повтор: </span>{{
          FrequencyTypeDisplay[task.schedule.frequency_type] }} до {{ new Date(task.schedule.end_date).toLocaleDateString('ru-RU') }}</p>
        <p><span class="font-semibold">Исполнитель: </span>{{ task.assigned_to_display ?? 'Не назначен' }} </p>
        <p><span class="font-semibold">Создана: </span> {{ task.created_by_display }} </p>
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

    <hr class="text-gray-300 mt-4 mb-4">

    <!--Status & Details Buttons -->
    <div class="flex-none flex flex-col wrap-normal gap-8">
      <form v-if="showChangeStatusButton && task.status === TaskStatusEnum.InProgress"
        @submit.prevent="$emit('changeStatus', { status: TaskStatusEnum.Completed, completion_evidence_link: completionEvidence })"
        class="flex flex-nowrap gap-2">
        <input v-model.trim="completionEvidence" type="text" placeholder="Подтверждение выполнения (ссылка)"
          class="flex-1 input text-base rounded-lg border border-gray-300 p-2 bg-gray-50" required></input>
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

<style scoped>
@reference "tailwindcss";

a {
    @apply text-teal-600 hover:text-teal-700 underline;
}
</style>