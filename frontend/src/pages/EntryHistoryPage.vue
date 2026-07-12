<template>
  <div
    class="main-page-wrapper"
     
  >
    <header class="logo-header">
      <img :src="logoUrl" alt="Suntory Oceania" class="header-logo" />
    </header>
    <div class="page-container">
    <div class="page-nav">
      <el-button :icon="ArrowLeft" plain @click="router.push('/')">Back to Entries</el-button>
    </div>

    <div class="page-header">
      <div v-if="versions.length" class="history-header-content">
        <h1 class="page-title">Entry History</h1>

        <!-- Current Entry Info -->
        <div class="entry-info card">
          <el-row :gutter="16">
            <el-col :span="3">
              <label class="info-label">Division</label>
              <div class="info-value">{{ formatValue(latestVersion?.division) }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Country</label>
              <div class="info-value">{{ formatValue(latestVersion?.country) }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Brand</label>
              <div class="info-value">{{ formatValue(latestVersion?.brand) }}</div>
            </el-col>
            <el-col :span="6">
              <label class="info-label">Owner</label>
              <div class="info-value">{{ latestVersion?.owner }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Status</label>
              <el-tag :type="statusType(latestVersion?.status)" size="small">
                {{ latestVersion?.status }}
              </el-tag>
            </el-col>
            <el-col :span="3">
              <label class="info-label">ID</label>
              <div class="info-value">{{ latestVersion?.originalEntryId }}</div>
            </el-col>
            <el-col :span="3">
              <label class="info-label">Total Versions</label>
              <div class="info-value">{{ versions.length }}</div>
            </el-col>
          </el-row>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state-block">
      <el-icon :size="32" class="spin"><Loading /></el-icon>
    </div>

    <div v-else-if="!versions.length" class="state-block state-block-muted">
      No history found for this entry.
    </div>

    <el-table
      v-else
      :data="versions"
      border
      style="width: 100%; margin-top: 24px"
      :row-class-name="rowClassName"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div v-if="row.childImpacts?.length" class="child-details">
            <strong>Impact Details:</strong>
            <el-table :data="row.childImpacts" size="small" border style="margin-top:8px">
              <el-table-column prop="impactYear" label="Year" width="80" />
              <el-table-column prop="impactPeriod" label="Period" width="80" />
              <el-table-column label="NSV (AUD)" width="130">
                <template #default="{ row: ci }">{{ formatMoney(ci.nsvAud) }}</template>
              </el-table-column>
              <el-table-column label="NSV (NZD)" width="130">
                <template #default="{ row: ci }">{{ formatMoney(ci.nsvNzd) }}</template>
              </el-table-column>
              <el-table-column label="Vol. (L)" width="110">
                <template #default="{ row: ci }">{{ formatVol(ci.volumeLitres) }}</template>
              </el-table-column>
            </el-table>
          </div>
          <div v-else style="padding: 8px; color: var(--text-muted)">No impact details</div>
        </template>
      </el-table-column>


      <el-table-column label="Country" width="120">
        <template #default="{ row, $index }">
          {{ formatValue(row.country) }}
          <el-tag v-if="hasChanged($index, 'country')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Division" width="100">
        <template #default="{ row, $index }">
          {{ formatValue(row.division) }}
          <el-tag v-if="hasChanged($index, 'division')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Categorisation" min-width="120">
        <template #default="{ row, $index }">
          {{ row.categorisation }}
          <el-tag v-if="hasChanged($index, 'categorisation')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Brand" min-width="120">
        <template #default="{ row, $index }">
          {{ formatValue(row.brand) }}
          <el-tag v-if="hasChanged($index, 'brand')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Primary Impact" width="160">
        <template #default="{ row, $index }">
          {{ formatPrimaryImpact(row) }}
          <el-tag v-if="hasChanged($index, 'nsvAud') || hasChanged($index, 'nsvNzd') || hasChanged($index, 'volumeLitres')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Owner" min-width="100">
        <template #default="{ row, $index }">
          {{ row.owner }}
          <el-tag v-if="hasChanged($index, 'owner')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column label="Status" width="100">
        <template #default="{ row, $index }">
          <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          <el-tag v-if="hasChanged($index, 'status')" type="warning" size="small" style="margin-left:4px">Updated</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="modifiedUser" label="Modified By" min-width="140">
        <template #default="{ row }">
          {{ row.modifiedUser || row.creator || "-" }}
        </template>
      </el-table-column>

      <el-table-column prop="lastModified" label="Modified At" width="155">
        <template #default="{ row }">
          {{ formatDate(row.lastModified) }}
        </template>
      </el-table-column>
    </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ArrowLeft, Loading } from "@element-plus/icons-vue";
import { entryApi } from "@/services/api"; 
import logoUrl from "@/assets/SuntoryOceania-Logo-RGB-Reversed.png";
import backgroundImage from "@/assets/SuntoryOceania-Patterns-RGB-Blue-Water_Ripples.png";
import type { Entry } from "@/types";
import { formatDate, formatMoney, formatVol } from "@/utils/formatters";

const router = useRouter();
const route = useRoute();
const loading = ref(true);
const versions = ref<Entry[]>([]);

const latestVersion = computed(() => versions.value[0]);

onMounted(async () => {
  const id = Number(route.params.originalEntryId);
  try {
    const data = await entryApi.getHistory(id);
    versions.value = data.versions;
  } finally {
    loading.value = false;
  }
});

function rowClassName({ row }: { row: Entry }) {
  return row.version === latestVersion.value?.version ? "row-latest" : "";
}

function hasChanged(index: number, field: keyof Entry): boolean {
  if (index >= versions.value.length - 1) return false;
  const current = versions.value[index];
  const prev = versions.value[index + 1];

  const v1 = current[field];
  const v2 = prev[field];

  const complexFields = ['country', 'brand', 'brandFamily', 'channel', 'subChannel', 'account'];
  if (complexFields.includes(field as string)) {
    return formatValue(v1) !== formatValue(v2);
  }

  return JSON.stringify(v1) !== JSON.stringify(v2);
}

function formatValue(v: any): string {
  if (!v) return '';
  if (Array.isArray(v)) return v.join(', ');
  if (typeof v === 'object') return Object.values(v).join(', ');
  try {
    const parsed = JSON.parse(v);
    if (Array.isArray(parsed)) return parsed.join(', ');
    if (parsed && typeof parsed === 'object') return Object.values(parsed).join(', ');
  } catch {}
  return String(v);
}

function statusType(status?: string) {
  const map: Record<string, "" | "success" | "warning" | "danger" | "info"> = {
    Open: "",
    Approved: "success",
    Dismissed: "info",
    "Included in Forecast": "warning",
  };
  return map[status || "Open"] ?? "";
}

function formatPrimaryImpact(row: Entry) {
  if (row.primaryImpact === "AUD") return formatMoney(row.nsvAud) + " AUD";
  if (row.primaryImpact === "NZD") return formatMoney(row.nsvNzd) + " NZD";
  if (row.primaryImpact === "Volume") return formatVol(row.volumeLitres);
  return "-";
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  /* background-color: #D9F2F2; */
}

.logo-header {
  max-width: 1400px;
  margin: 0 auto;
  padding: 16px 24px;
  background: #00325D;
}

.page-title {
  font-family: 'Jost', Arial, sans-serif; /* Already Jost */
  font-size: 28px;
  font-weight: 500;
  margin: 0;
  color: var(--text-title-heading);
  line-height: 1.2;
}

.page-nav {
  margin-bottom: 16px;
}

.history-header-content {
  margin-top: 4px;
}

.entry-info {
  padding: 16px;
  margin-top: 16px;
}

.info-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
  display: block;
  margin-bottom: 4px;
}

.info-value {
  font-weight: 500;
  color: var(--text-primary);
}

.child-details {
  padding: 12px 24px;
}

.state-block {
  text-align: center;
  padding: 48px;
}

.state-block-muted {
  color: var(--text-muted);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

:deep(.row-latest) td {
  background-color: #f0fdf4 !important;
}

.header-logo {
  height: 40px;
  width: auto;
}
</style>
