<script setup lang="ts">
import type { LogEntry } from '@/api-client';
import { ActionDisplay } from '@/utils/constants';

const props = defineProps<{
    log: LogEntry,
    showType: boolean
}>()

const toIsoString = (str: string) => str.replace(' ', 'T') + 'Z'

</script>
<template>
    <div class="py-2">
        <div class="flex flex-wrap gap-x-2 items-center">
            <span class="font-semibold">{{ new Date(log.timestamp ?? "").toLocaleString('ru-RU')
            }}:</span>
            <span>Пользователь #{{ log.actor }}</span>
            <span class="italic">{{ log.actor_display }}</span>
            <span>{{ ActionDisplay[log.action] }}</span>
            <span v-if="showType">объект типа</span>
            <span v-if="showType" class="italic">"{{ log.content_type_display }}": </span>
            <span class="font-bold text-end">{{ log.object_repr }}</span>
        </div>
        <p v-if="log.changes_text">Описание изменений:
        <p></p>{{ log.changes_text }}</p>
        <br>
        <p v-if="log.changes">ИЗМЕНЕНИЯ:</p>
        <ul>
            <li v-for="(values, field) in log.changes">
                <div class="flex flex-wrap gap-x-2 items-center">
                    <span class="font-semibold">{{ field }}:</span>
                    <span v-if="field.toString() == 'deadline' || field.toString() == 'created_at'"
                        class="italic whitespace-pre-wrap">{{ values[0] == 'None' ? 'None' : new
                            Date(toIsoString(values[0])).toLocaleString('ru-RU') }} -> {{ new Date(toIsoString(values[1])).toLocaleString('ru-RU') }}</span>
                    <span v-else class="italic whitespace-pre-wrap">{{ values[0] }} -> {{ values[1] }}</span>
                </div>
            </li>
        </ul>
    </div>
</template>