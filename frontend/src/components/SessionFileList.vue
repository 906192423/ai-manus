<template>
    <div v-if="visible" class="absolute z-[1000] pointer-events-auto">
        <div class="w-full h-full bg-black/60 backdrop-blur-[4px] fixed inset-0 data-[state=open]:animate-dialog-bg-fade-in data-[state=closed]:animate-dialog-bg-fade-out"
            style="position: fixed; overflow: auto; inset: 0px;" @click="close"></div>
        <div role="dialog"
            class="bg-[var(--background-menu-white)] rounded-[20px] border border-white/5 fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 max-w-[95%] max-h-[95%] overflow-auto data-[state=open]:animate-dialog-slide-in-from-bottom data-[state=closed]:animate-dialog-slide-out-to-bottom h-[680px] flex flex-col"
            style="width: 600px;">
            <div class="p-0">
                <h3 class="text-[var(--text-primary)] text-[18px] leading-[24px] font-semibold flex items-center"></h3>
            </div>
            <header class="flex items-center pt-6 pr-6 pl-6 pb-2.5">
                <h1 class="flex-1 text-[var(--text-primary)] text-lg font-semibold">{{ $t('All Files in This Task') }}</h1>
                <div class="flex items-center gap-4">
                    <div @click="close"
                        class="flex h-7 w-7 items-center justify-center cursor-pointer hover:bg-[var(--fill-tsp-gray-main)] rounded-md">
                        <X class="size-5 text-[var(--icon-tertiary)]" />
                    </div>
                </div>
            </header>
            <div class="flex-1 min-h-0 flex flex-col">
                <div v-if="files.length > 0" class="flex-1 min-h-0 overflow-auto px-3 mt-4 pb-4">
                    <div class="flex flex-col gap-1 first:pt-0 pt-2">
                        <div class="">
                            <div v-for="file in files" 
                                class="flex items-center gap-3 px-3 py-2.5 hover:bg-[var(--fill-tsp-gray-main)] transition-colors rounded-lg clickable">
                                <div class="relative flex items-center justify-center">
                                    <component :is="getFileType(file.filename).icon" />
                                </div>
                                <div @click="showFile(file)" class="flex flex-col gap-1 flex-grow flex-1 min-w-0">
                                    <div class="flex justify-between items-center flex-1 min-w-0">
                                        <div class="flex flex-col flex-1 min-w-0 max-w-[100%]">
                                            <div class="flex-1 min-w-0 flex gap-2 items-center">
                                                <span
                                                    class="inline-block whitespace-nowrap text-sm text-[var(--text-primary)]"
                                                    style="overflow: hidden; text-overflow: ellipsis;">{{ file.filename
                                                    }}</span>
                                                <div class="flex gap-2 flex-shrink-0 items-center"></div>
                                            </div>
                                            <span class="text-xs text-[var(--text-tertiary)]">{{
                                                formatRelativeTime(parseISODateTime(file.upload_date)) }}</span>
                                        </div>
                                        <div @click="downloadFile(file.file_id)"
                                            class="flex items-center justify-center cursor-pointer hover:bg-[var(--fill-tsp-gray-main)] rounded-md w-8 h-8 text-[var(--icon-tertiary)]"
                                            aria-expanded="false" aria-haspopup="dialog">
                                            <Download class="size-5 text-[var(--icon-tertiary)]" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-else class="flex-1 min-h-0 flex flex-col items-center justify-center gap-3">
                    <File />
                    <p class="text-[var(--icon-tertiary)] text-[14px]">{{ $t('No Content') }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { X, Download, File } from 'lucide-vue-next';
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { eventBus } from '../utils/eventBus';
import { EVENT_SESSION_FILE_LIST_SHOW, EVENT_FILE_SHOW } from '../constants/event';
import type { FileInfo } from '../api/file';
import { getFileDownloadUrl } from '../api/file';
import { getSessionFiles } from '../api/agent';
import { formatRelativeTime, parseISODateTime } from '../utils/time';
import { getFileType } from '../utils/fileType';

const route = useRoute();
const visible = ref(false);
const files = ref<FileInfo[]>([]);

const fetchFiles = async (sessionId: string) => {
    if (!sessionId) {
        return;
    }
    const response = await getSessionFiles(sessionId);
    files.value = response;
}

const downloadFile = async (fileId: string) => {
    const url = getFileDownloadUrl(fileId);
    window.open(url, '_blank');
}

const open = () => {
    const sessionId = route.params.sessionId as string;
    if (sessionId) {
        visible.value = true;
        fetchFiles(sessionId);
    }
}

const showFile = (file: FileInfo) => {
    eventBus.emit(EVENT_FILE_SHOW, { file });
    close();
}

const close = () => {
    visible.value = false;
}

const handleShow = () => {
    open();
}

onMounted(() => {
    eventBus.on(EVENT_SESSION_FILE_LIST_SHOW, handleShow);
})

onUnmounted(() => {
    eventBus.off(EVENT_SESSION_FILE_LIST_SHOW, handleShow);
})

defineExpose({
    open,
    close
});
</script>