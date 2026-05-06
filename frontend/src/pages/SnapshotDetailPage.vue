<template>
  <div class="page-container">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="router.push('/snapshots')">
        Back to Snapshots
      </el-button>
    </div>

    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <p>Loading snapshot...</p>
    </div>

    <div v-else-if="!snapshot" class="empty-state">
      <p>Snapshot not found</p>
    </div>

    <div v-else class="content">
      <div class="snapshot-header">
        <div class="header-title">
          <h1 class="page-title">Snapshot: {{ snapshot.name }}</h1>
          <el-tag v-if="snapshot.department" size="large">{{ snapshot.department }}</el-tag>
        </div>
        <p class="snapshot-meta">
          Created: {{ formatDate(snapshot.created_at) }} • {{ snapshotEntries.length }} {{ snapshotEntries.length === 1 ? 'entry' : 'entries' }}
        </p>
      </div>

      <EntriesTable
        :entries="snapshotEntries"
        :is-read-only="true"
        :can-approve="false"
        :default-split-by="['country', 'division']"
        @add="() => {}"
        @edit="() => {}"
        @duplicate="() => {}"
        @delete="() => {}"
        @history="handleHistory"
        @approve="() => {}"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Loading } from "@element-plus/icons-vue";
import { snapshotApi } from "@/services/api";
import EntriesTable from "@/components/EntriesTable.vue";
import type { Entry } from "@/types";

interface SnapshotDetail {
  snapshot_id: string;
  name: string;
  period: string;
  year: string;
  department: string;
  created_at: string;
  entries: Entry[];
}

const router = useRouter();
const route = useRoute();
const loading = ref(true);
const snapshot = ref<SnapshotDetail | null>(null);

const snapshotId = computed(() => route.params.snapshotId as string);

const snapshotEntries = computed(() => {
  if (!snapshot.value) return [];
  
  return snapshot.value.entries.map((entry) => ({
    ...entry,
    customer: [entry.channel, entry.subChannel, entry.account].filter(Boolean).join(" / "),
    product: [
      entry.brand,
      Array.isArray(entry.brandFamily)
        ? entry.brandFamily.join(", ")
        : entry.brandFamily,
    ]
      .filter(Boolean)
      .join(" - "),
  }));
});

onMounted(async () => {
  await fetchSnapshot();
});

async function fetchSnapshot() {
  loading.value = true;
  try {
    const data = await snapshotApi.getById(snapshotId.value);
    snapshot.value = data.snapshot;
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "Failed to load snapshot");
  } finally {
    loading.value = false;
  }
}

function formatDate(dateString: string) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  });
}

function handleHistory(entry: Entry) {
  router.push(`/entry/${entry.originalEntryId}/history`);
}
</script>

<style scoped>
.page-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: var(--text-secondary);
}

.content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.snapshot-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.snapshot-meta {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
}
</style>
