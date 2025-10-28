<script setup lang="ts">
import apiAxios from '@/axios'
import { AuditlogApi, type LogEntry } from '@/api-client'
import { onMounted, ref } from 'vue'
import { isAxiosError } from 'axios'
import { handleAxiosError } from '@/utils/utils'
import { ActionDisplay } from '@/utils/constants'

const logsApi = new AuditlogApi(undefined, undefined, apiAxios)
const logs = ref<LogEntry[]>([])

const fetchLogs = async () => {
  try {
    const res = await logsApi.auditlogList()
    logs.value = res.data
  } catch (error) {
    console.error(error)
    if (isAxiosError(error)) {
      handleAxiosError(error)
    }
  }
}

onMounted(fetchLogs)
</script>

<template>
  <div>
    <ul class="divide-y divide-gray-300">
      <li v-for="log in logs" :key="log.id" class="p-2">
        <div class="flex flex-wrap gap-x-2 items-center">
          <span class="font-semibold">{{ new Date(log.timestamp ?? "").toLocaleString('ru-RU') }}:</span>
          <span>Пользователь #{{ log.actor }}</span>
          <span class="font-bold italic">{{ log.actor_display }}</span>
          <span>{{ ActionDisplay[log.action] }}</span>
          <span>объект типа</span>
          <span class="italic">"{{ log.content_type_display }}": </span>
          <span class="font-bold text-end">{{ log.object_repr }}</span>
        </div>
        <p v-if="log.changes_text">Описание изменений: {{ log.changes_text }}</p>
        <br>
        <p v-if="log.changes">ИЗМЕНЕНИЯ:</p>
        <ul>
          <li v-for="(values, field) in log.changes">
            <div class="flex flex-wrap gap-x-2 items-center">
              <span class="font-semibold">{{ field }}:</span>
              <span class="italic">{{ values[0] }} -> {{ values[1] }}</span>
            </div>
          </li>
        </ul>
        <br>
      </li>
    </ul>
  </div>

</template>