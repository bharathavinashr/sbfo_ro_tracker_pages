<template>
  <div
    class="main-page-wrapper"
     
  >
    <header class="logo-header">
      <img :src="logoUrl" alt="Suntory Oceania" class="header-logo" />
    </header>
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
          <el-tag v-if="snapshot.ibp_step" size="large">{{ snapshot.ibp_step }}</el-tag>
        </div>
        <p class="snapshot-meta">
          Created: {{ formatDate(snapshot.created_at) }} • {{ snapshotEntries.length }} {{ snapshotEntries.length === 1 ? 'entry' : 'entries' }}
        </p>
      </div>

      <EntriesTable
        :entries="snapshotEntries"
        :is-read-only="true"
        :can-approve="false"
        :default-split-by="[]"
        @add="() => {}"
        @edit="() => {}"
        @duplicate="() => {}"
        @delete="() => {}"
        @history="handleHistory"
        @approve="() => {}"
      />
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Loading } from "@element-plus/icons-vue";
import { snapshotApi } from "@/services/api"; 
import logoUrl from "@/assets/SuntoryOceania-Logo-RGB-Reversed.png";
import backgroundImage from "@/assets/SuntoryOceania-Patterns-RGB-Blue-Water_Ripples.png";
import EntriesTable from "@/components/EntriesTable.vue";
import type { Entry } from "@/types";

interface SnapshotDetail {
  snapshot_id: string;
  name: string;
  period: string;
  year: string;
  ibp_step: string;
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
.main-page-wrapper {
  min-height: 100vh;
  background-size: cover;
  background-attachment: fixed;
  background-repeat: repeat;
  background-position: center;
}

.page-container {
  width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 24px;
  /* background-color: #D9F2F2; */
}

.logo-header {
  width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 16px 24px;
  background: #00325D;
}

.header-logo {
  height: 40px;
  width: auto;
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
  font-family: 'Jost', Arial, sans-serif; /* Already Jost */
  font-size: 28px;
  font-weight: 500;
  margin: 0;
  color: var(--text-title-heading);
  line-height: 1.2;
}

.snapshot-meta {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 0;
}
</style>
