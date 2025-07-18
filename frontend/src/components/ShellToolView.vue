<template>
  <div
    class="h-[36px] flex items-center px-3 w-full bg-[var(--background-gray-main)] border-b border-[var(--border-main)] rounded-t-[12px] shadow-[inset_0px_1px_0px_0px_#FFFFFF] dark:shadow-[inset_0px_1px_0px_0px_#FFFFFF30]">
    <div class="flex-1 flex items-center justify-center">
      <div class="max-w-[250px] truncate text-[var(--text-tertiary)] text-sm font-medium text-center">{{
        shellSessionId }}
      </div>
    </div>
  </div>
  <div class="flex-1 min-h-0 w-full overflow-y-auto">
    <div dir="ltr" data-orientation="horizontal" class="flex flex-col flex-1 min-h-0">
      <div data-state="active" data-orientation="horizontal" role="tabpanel"
        id="radix-:r5m:-content-setup" tabindex="0"
        class="py-2 focus-visible:outline-none data-[state=inactive]:hidden flex-1 font-mono text-sm leading-relaxed px-3 outline-none overflow-auto whitespace-pre-wrap break-all"
        style="animation-duration: 0s;">
        <code v-html="shell"></code>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch, onUnmounted } from 'vue';
import { viewShellSession } from '../api/agent';
import { ToolContent } from '../types/message';
//import { showErrorToast } from '../utils/toast';

const props = defineProps<{
  sessionId: string;
  toolContent: ToolContent;
  live: boolean;
}>();

defineExpose({
  loadContent: () => {
    loadShellContent();
  }
});

const shell = ref('');
const cancelViewShell = ref<(() => void) | null>(null);

// Get shellSessionId from toolContent
const shellSessionId = computed(() => {
  if (props.toolContent && props.toolContent.args.id) {
    return props.toolContent.args.id;
  }
  return '';
});

const updateShellContent = (console: any) => {
  if (!console) return;
  let newShell = '';
  for (const e of console) {
    newShell += `<span style="color: rgb(0, 187, 0);">${e.ps1}</span><span> ${e.command}</span>\n`;
    newShell += `<span>${e.output}</span>\n`;
  }
  if (newShell !== shell.value) {
    shell.value = newShell;
  }
}

// Function to load Shell session content
const loadShellContent = async () => {
  if (cancelViewShell.value) {
    cancelViewShell.value();
  }

  if (!props.live) {
    updateShellContent(props.toolContent.content?.console);
    return;
  }
  if (!shellSessionId.value) return;

  cancelViewShell.value = await viewShellSession(props.sessionId, shellSessionId.value, {
    onMessage: (event) => {
      if (event.event === "shell") {
        updateShellContent(event.data.console);
      }
    }
  })
};

watch(shellSessionId, () => {
  loadShellContent();
});

watch(() => props.toolContent.timestamp, () => {
  loadShellContent();
});

// Load content and set up refresh timer when component is mounted
onMounted(() => {
  loadShellContent();
});

// Clear timer when component is unmounted
onUnmounted(() => {
  if (cancelViewShell.value) {
    cancelViewShell.value();
    cancelViewShell.value = null;
  }
});
</script>
