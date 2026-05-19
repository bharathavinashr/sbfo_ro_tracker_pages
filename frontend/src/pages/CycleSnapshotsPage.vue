<template>
  <div class="page-container">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="router.push('/')">Back to Main</el-button>
      <div>
        <h1 class="page-title">
          {{ showComparison ? 'Snapshot Comparison' : 'Browse Snapshots' }}
        </h1>
        <p class="page-subtitle">
          {{ showComparison
            ? 'Showing differences between selected snapshots'
            : comparisonMode
              ? 'Select 2 snapshots to compare'
              : 'View and manage frozen snapshots of entry versions' }}
        </p>
      </div>
    </div>

    <!-- Comparison result view -->
    <template v-if="showComparison">
      <div class="comparison-meta">
        <div class="comparison-labels">
          <span><strong>Baseline:</strong> {{ earlierSnapshot?.name }} ({{ formatDate(earlierSnapshot?.created_at ?? '') }})</span>
          <span class="arrow">→</span>
          <span><strong>Comparison:</strong> {{ laterSnapshot?.name }} ({{ formatDate(laterSnapshot?.created_at ?? '') }})</span>
        </div>
        <el-button @click="clearComparison">
          <el-icon><Close /></el-icon>
          Close Comparison
        </el-button>
      </div>

      <!-- Summary badges -->
      <div class="comparison-summary">
        <el-tag type="success">{{ countByStatus('New') }} New</el-tag>
        <el-tag type="primary">{{ countByStatus('Modified') }} Modified</el-tag>
        <el-tag type="danger">{{ countByStatus('Deleted') }} Deleted</el-tag>
        <el-tag type="info">{{ countByStatus('Unchanged') }} Unchanged</el-tag>

        <!-- Column toggle -->
        <el-popover placement="bottom-end" :width="240" trigger="click">
          <template #reference>
            <el-button class="ml-auto" size="small">
              <el-icon><Grid /></el-icon>
              Columns
            </el-button>
          </template>
          <div class="column-toggle">
            <p class="column-toggle-title">Toggle Columns</p>
            <div v-for="col in columnDefs" :key="col.key" class="column-toggle-item">
              <el-checkbox v-model="visibleColumns[col.key]">{{ col.label }}</el-checkbox>
            </div>
          </div>
        </el-popover>
      </div>

      <!-- Comparison table -->
      <div class="table-wrapper">
        <el-table
          :data="comparedEntries"
          border
          stripe
          size="small"
          :row-class-name="getRowClass"
          style="width: 100%"
        >
          <el-table-column v-if="visibleColumns.changeStatus" label="Change" width="110" fixed>
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.changeStatus)" size="small">{{ row.changeStatus }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.modifiedFields" label="Modified Columns" width="200">
            <template #default="{ row }">
              <template v-if="row.changeStatus === 'Modified' && row.modifiedFields?.length">
                <el-tag
                  v-for="field in row.modifiedFields"
                  :key="field"
                  size="small"
                  style="margin: 2px"
                >{{ field }}</el-tag>
              </template>
              <span v-else-if="row.changeStatus === 'New'" class="text-green">New entry</span>
              <span v-else-if="row.changeStatus === 'Deleted'" class="text-red">Deleted</span>
              <span v-else class="text-muted">-</span>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.ibpStep" label="IBP Step" width="140">
            <template #default="{ row }">
              <div>{{ row.ibpStep || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.ibpStep && row.previousValues.ibpStep !== row.ibpStep" class="prev-value">{{ row.previousValues.ibpStep }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.division" label="Division" width="110">
            <template #default="{ row }">
              <div>{{ row.division }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.division && row.previousValues.division !== row.division" class="prev-value">{{ row.previousValues.division }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.country" label="Country" width="110">
            <template #default="{ row }">
              <div>{{ formatValue(row.country) }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.country && formatValue(row.previousValues.country) !== formatValue(row.country)" class="prev-value">{{ formatValue(row.previousValues.country) }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.categorisation" label="Categorisation" width="160">
            <template #default="{ row }">
              <div>{{ row.categorisation || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.categorisation && row.previousValues.categorisation !== row.categorisation" class="prev-value">{{ row.previousValues.categorisation }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.description" label="Short Description" width="200">
            <template #default="{ row }">
              <div>{{ row.description || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.description && row.previousValues.description !== row.description" class="prev-value">{{ row.previousValues.description }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.customer" label="Customer(s)" width="160">
            <template #default="{ row }">
              <div v-if="row.account">{{ formatValue(row.account) }}</div>
              <div v-if="row.subChannel" class="text-small text-muted">{{ formatValue(row.subChannel) }}</div>
              <div v-if="row.channel" class="text-small text-muted text-italic">{{ formatValue(row.channel) }}</div>
              <span v-if="!row.account && !row.subChannel && !row.channel">-</span>
              <div v-if="row.changeStatus === 'Modified' && (row.previousValues?.channel || row.previousValues?.subChannel || row.previousValues?.account)" class="prev-value">
                {{ [formatValue(row.previousValues.channel), formatValue(row.previousValues.subChannel), formatValue(row.previousValues.account)].filter(Boolean).join(', ') }}
              </div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.product" label="Product" width="160">
            <template #default="{ row }">
              <div v-if="row.brand">{{ formatValue(row.brand) }}</div>
              <div v-if="row.brandFamily" class="text-small text-muted">{{ formatValue(row.brandFamily) }}</div>
              <span v-if="!row.brand && !row.brandFamily">-</span>
              <div v-if="row.changeStatus === 'Modified' && (row.previousValues?.brand || row.previousValues?.brandFamily)" class="prev-value">
                {{ [formatValue(row.previousValues.brand), formatValue(row.previousValues.brandFamily)].filter(Boolean).join(', ') }}
              </div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.rAndO" label="Risk vs. Opp." width="130">
            <template #default="{ row }">
              <div>{{ row.rAndO }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.rAndO && row.previousValues.rAndO !== row.rAndO" class="prev-value">{{ row.previousValues.rAndO }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.probability" label="Probability" width="110">
            <template #default="{ row }">
              <div :style="{ opacity: formatProbability(row.probability).opacity + '%' }">{{ formatProbability(row.probability).text }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.probability && row.previousValues.probability !== row.probability" class="prev-value">{{ formatProbability(row.previousValues.probability).text }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.addToForecastBy" label="Add to Forecast By" width="160">
            <template #default="{ row }">
              <div>{{ row.addToForecastByPeriod && row.addToForecastByYear ? `${periodToMonthAbbr(row.addToForecastByPeriod)} ${row.addToForecastByYear}` : '-' }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.creator" label="Creator" width="130">
            <template #default="{ row }">
              <div>{{ row.creator || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.creator && row.previousValues.creator !== row.creator" class="prev-value">{{ row.previousValues.creator }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.owner" label="Owner" width="130">
            <template #default="{ row }">
              <div>{{ row.owner }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.owner && row.previousValues.owner !== row.owner" class="prev-value">{{ row.previousValues.owner }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.status" label="Entry Status" width="120">
            <template #default="{ row }">
              <div>{{ row.status || 'Open' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.status && row.previousValues.status !== row.status" class="prev-value">{{ row.previousValues.status }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.lastModified" label="Last Modified" width="140">
            <template #default="{ row }">
              {{ new Date(row.lastModified).toLocaleDateString() }}
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.financialImpactType" label="Impact Type" width="130">
            <template #default="{ row }">
              <div>{{ row.financialImpactType || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.financialImpactType && row.previousValues.financialImpactType !== row.financialImpactType" class="prev-value">{{ row.previousValues.financialImpactType }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.currency" label="Financial Impact Currency" width="110">
            <template #default="{ row }">
              <div>{{ row.impactCurrency || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.impactCurrency && row.previousValues.impactCurrency !== row.impactCurrency" class="prev-value">{{ row.previousValues.impactCurrency }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.impact" label="Impact" width="120">
            <template #default="{ row }">
              <div>{{ row.impact || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.impact && row.previousValues.impact !== row.impact" class="prev-value">{{ row.previousValues.impact }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.volumeCases" label="Volume (Cases)" width="140">
            <template #default="{ row }">
              <div>{{ row.volumeCases || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.volumeCases && row.previousValues.volumeCases !== row.volumeCases" class="prev-value">{{ row.previousValues.volumeCases }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.volumeImpactType" label="Volume Impact Type" width="160">
            <template #default="{ row }">
              <div>{{ row.volumeImpactType || '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.volumeImpactType && row.previousValues.volumeImpactType !== row.volumeImpactType" class="prev-value">{{ row.previousValues.volumeImpactType }}</div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.volumeImpactValue" label="Volume Impact Value" width="160">
            <template #default="{ row }">
              <div class="tr">{{ row.volumeImpactValue ? Number(row.volumeImpactValue).toLocaleString() : '-' }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.volumeImpactValue && row.previousValues.volumeImpactValue !== row.volumeImpactValue" class="prev-value tr">
                {{ row.previousValues.volumeImpactValue ? Number(row.previousValues.volumeImpactValue).toLocaleString() : '-' }}
              </div>
            </template>
          </el-table-column>

          <el-table-column v-if="visibleColumns.impactPeriods" label="Impact Period(s)" width="180">
            <template #default="{ row }">
              <div>{{ formatImpactPeriods(row.childImpacts, row.impactPeriod, row.impactYear) }}</div>
              <div v-if="row.changeStatus === 'Modified' && row.previousValues?.childImpacts" class="prev-value">
                {{ formatImpactPeriods(row.previousValues.childImpacts, row.previousValues.impactPeriod, row.previousValues.impactYear) }}
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <!-- Default snapshot list view -->
    <template v-else>
      <!-- Compare mode banner -->
      <div v-if="comparisonMode" class="compare-banner">
        <div class="compare-banner-left">
          <el-icon><ScaleToOriginal /></el-icon>
          <span class="compare-banner-text">
            {{ selectedSnapshots.length === 0 ? 'Select 2 snapshots to compare' : `${selectedSnapshots.length} snapshot${selectedSnapshots.length !== 1 ? 's' : ''} selected` }}
          </span>
        </div>
        <div class="compare-banner-right">
          <el-button
            v-if="selectedSnapshots.length === 2"
            type="primary"
            :loading="comparing"
            @click="handleCompare"
          >
            <el-icon><ScaleToOriginal /></el-icon>
            {{ comparing ? 'Comparing...' : 'Compare' }}
          </el-button>
          <el-button @click="cancelComparisonMode">Cancel</el-button>
        </div>
      </div>

      <!-- Compare button (only shown when not in compare mode and 2+ snapshots exist) -->
      <div v-else-if="snapshots.length >= 2" class="compare-btn-row">
        <el-button @click="enterComparisonMode">
          <el-icon><ScaleToOriginal /></el-icon>
          Compare Snapshots
        </el-button>
      </div>

      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>Loading snapshots...</p>
      </div>

      <el-empty v-else-if="snapshots.length === 0" description="No snapshots yet">
        <template #image>
          <el-icon :size="60"><Calendar /></el-icon>
        </template>
        <p>Use the Generate Snapshot button on the main page to create your first snapshot</p>
      </el-empty>

      <div v-else class="snapshots-grid">
        <div v-for="step in ibpSteps" :key="step" class="department-section">
          <template v-if="groupedSnapshots[step]?.length > 0">
            <div class="section-header">
              <h2>{{ step }}</h2>
              <el-tag>{{ groupedSnapshots[step].length }} {{ groupedSnapshots[step].length === 1 ? 'snapshot' : 'snapshots' }}</el-tag>
            </div>
            <div class="cards-grid">
              <el-card
                v-for="snapshot in groupedSnapshots[step]"
                :key="snapshot.snapshot_id"
                class="snapshot-card"
                :class="{ 'is-selected': selectedSnapshots.includes(snapshot.snapshot_id) }"
              >
                <template #header>
                  <div class="card-header">
                    <div class="card-header-left">
                      <el-checkbox
                        v-if="comparisonMode"
                        :model-value="selectedSnapshots.includes(snapshot.snapshot_id)"
                        @change="toggleSnapshotSelection(snapshot.snapshot_id)"
                      />
                      <span class="snapshot-name">{{ snapshot.name }}</span>
                    </div>
                  </div>
                </template>
                <div class="card-content">
                  <p class="snapshot-date">Created: {{ formatDate(snapshot.created_at) }}</p>
                  <p class="snapshot-count">
                    <strong>{{ snapshot.entries_count }}</strong> {{ snapshot.entries_count === 1 ? 'entry' : 'entries' }} frozen
                  </p>
                  <div class="card-actions">
                    <el-button type="primary" @click="handleViewSnapshot(snapshot.snapshot_id)">
                      View Snapshot
                    </el-button>
                    <el-button type="danger" :icon="Delete" @click="handleDeleteSnapshot(snapshot.snapshot_id, snapshot.name)" />
                  </div>
                </div>
              </el-card>
            </div>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowLeft, Calendar, Loading, Delete, Close, Grid, ScaleToOriginal } from "@element-plus/icons-vue";
import { snapshotApi } from "@/services/api";

interface SnapshotGroup {
  snapshot_id: string;
  name: string;
  period: string;
  year: string;
  ibp_step: string;
  entries_count: number;
  created_at: string;
}

interface ChildImpact {
  id: string;
  impactYear: string;
  impactPeriod: string;
  impact: string;
  impactUnit: string;
  secondaryImpact?: string;
  financialImpactType?: string;
  impactCurrency?: string;
  impactValue?: string;
  volumeCases?: string;
}

interface Entry {
  id: string;
  originalEntryId?: string;
  division: string;
  ibpStep?: string;
  country: string;
  channel: string;
  subChannel: string;
  account: string;
  brand: string;
  brandFamily: string | string[] | Record<string, string>;
  rAndO: string;
  probability: string;
  impactPeriod?: string;
  impactYear?: string;
  addToForecastByPeriod?: string;
  addToForecastByYear?: string;
  categorisation: string;
  impact: string;
  impactUnit?: string;
  secondaryImpact?: string;
  noVolumeImpact?: boolean;
  owner: string;
  creator?: string;
  lastModified: string;
  status?: string;
  description?: string;
  detailedDescription?: string;
  financialImpactType?: string;
  impactCurrency?: string;
  impactValue?: string;
  volumeCases?: string;
  volumeImpactType?: string;
  volumeImpactValue?: string;
  childImpacts?: ChildImpact[];
}

type ChangeStatus = 'New' | 'Modified' | 'Deleted' | 'Unchanged';

interface ComparedEntry extends Entry {
  changeStatus: ChangeStatus;
  modifiedFields?: string[];
  previousValues?: Record<string, any>;
}

const router = useRouter();
const loading = ref(true);
const snapshots = ref<SnapshotGroup[]>([]);
const comparing = ref(false);
const comparisonMode = ref(false);
const selectedSnapshots = ref<string[]>([]);
const comparedEntries = ref<ComparedEntry[]>([]);
const showComparison = ref(false);

const ibpSteps = ["Portfolio Review", "Supply Review", "Demand Review", "A&P (Pre-Exec)", "Overheads (Pre-Exec)"];

// Column visibility
const visibleColumns = ref<Record<string, boolean>>({
  changeStatus:        true,
  modifiedFields:      true,
  ibpStep:             true,
  division:            false,
  country:             false,
  categorisation:      true,
  description:         true,
  customer:            false,
  product:             false,
  rAndO:               true,
  probability:         true,
  addToForecastBy: false,
  creator:             false,
  owner:               false,
  status:              true,
  lastModified:        false,
  financialImpactType: false,
  currency:            false,
  impact:              false,
  volumeCases:         false,
  volumeImpactType:    false,
  volumeImpactValue:   false,
  impactPeriods:       true,
});

const columnDefs = [
  { key: 'changeStatus', label: 'Change Status' },
  { key: 'modifiedFields', label: 'Modified Fields' },
  { key: 'ibpStep', label: 'IBP Step' },
  { key: 'division', label: 'Division' },
  { key: 'country', label: 'Country' },
  { key: 'categorisation', label: 'Categorisation' },
  { key: 'description', label: 'Short Description' },
  { key: 'customer', label: 'Customer(s)' },
  { key: 'product', label: 'Product' },
  { key: 'rAndO', label: 'Risk vs. Opp.' },
  { key: 'probability', label: 'Probability' },
  { key: 'addToForecastBy', label: 'Add to Forecast By' },
  { key: 'creator', label: 'Creator' },
  { key: 'owner', label: 'Owner' },
  { key: 'status', label: 'Entry Status' },
  { key: 'lastModified', label: 'Last Modified' },
  { key: 'financialImpactType', label: 'Impact Type' },
  { key: 'currency', label: 'Financial Impact Currency' },
  { key: 'impact', label: 'Impact' },
  { key: 'volumeCases', label: 'Volume (Cases)' },
  { key: 'volumeImpactType', label: 'Volume Impact Type' },
  { key: 'volumeImpactValue', label: 'Volume Impact Value' },
  { key: 'impactPeriods', label: 'Impact Period(s)' },
];

const groupedSnapshots = computed(() => {
  const grouped: Record<string, SnapshotGroup[]> = {};
  ibpSteps.forEach(step => {
    grouped[step] = snapshots.value.filter(s => s.ibp_step === step);
  });
  return grouped;
});

const earlierSnapshot = computed(() => {
  const [a, b] = selectedSnapshots.value.map(id => snapshots.value.find(s => s.snapshot_id === id));
  if (!a || !b) return null;
  return new Date(a.created_at) < new Date(b.created_at) ? a : b;
});

const laterSnapshot = computed(() => {
  const [a, b] = selectedSnapshots.value.map(id => snapshots.value.find(s => s.snapshot_id === id));
  if (!a || !b) return null;
  return new Date(a.created_at) >= new Date(b.created_at) ? a : b;
});

onMounted(async () => {
  await fetchSnapshots();
});

async function fetchSnapshots() {
  loading.value = true;
  try {
    const data = await snapshotApi.getAll();
    snapshots.value = data.snapshots.sort((a: SnapshotGroup, b: SnapshotGroup) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "Failed to load snapshots");
  } finally {
    loading.value = false;
  }
}

function formatDate(dateString: string) {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString("en-US", {
    year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
  });
}

function handleViewSnapshot(snapshotId: string) {
  router.push(`/snapshots/${snapshotId}`);
}

async function handleDeleteSnapshot(snapshotId: string, snapshotName: string) {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete snapshot "${snapshotName}"? This action cannot be undone.`,
      "Confirm Delete",
      { type: "warning", confirmButtonText: "Delete", confirmButtonClass: "el-button--danger" }
    );
    await snapshotApi.delete(snapshotId);
    ElMessage.success(`Snapshot deleted: ${snapshotName}`);
    await fetchSnapshots();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || "Failed to delete snapshot");
    }
  }
}

function toggleSnapshotSelection(snapshotId: string) {
  if (selectedSnapshots.value.includes(snapshotId)) {
    selectedSnapshots.value = selectedSnapshots.value.filter(id => id !== snapshotId);
  } else if (selectedSnapshots.value.length < 2) {
    selectedSnapshots.value = [...selectedSnapshots.value, snapshotId];
  } else {
    ElMessage.warning("You can only compare 2 snapshots at a time");
  }
}

function enterComparisonMode() {
  comparisonMode.value = true;
  selectedSnapshots.value = [];
}

function cancelComparisonMode() {
  comparisonMode.value = false;
  selectedSnapshots.value = [];
}

function clearComparison() {
  showComparison.value = false;
  comparedEntries.value = [];
  selectedSnapshots.value = [];
  comparisonMode.value = false;
}

function countByStatus(status: ChangeStatus) {
  return comparedEntries.value.filter(e => e.changeStatus === status).length;
}

function statusTagType(status: ChangeStatus) {
  switch (status) {
    case 'New': return 'success';
    case 'Modified': return 'primary';
    case 'Deleted': return 'danger';
    default: return 'info';
  }
}

function getRowClass({ row }: { row: ComparedEntry }) {
  if (row.changeStatus === 'New') return 'row-new';
  if (row.changeStatus === 'Modified') return 'row-modified';
  if (row.changeStatus === 'Deleted') return 'row-deleted';
  return '';
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function periodToMonthAbbr(period: string): string {
  if (!period) return '-';
  const abbrs = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const idx = parseInt(period.replace('F', '')) - 1;
  return isNaN(idx) || idx < 0 || idx >= 12 ? period : abbrs[idx];
}

function formatImpactPeriods(childImpacts?: Array<{ impactPeriod: string; impactYear: string }>, impactPeriod?: string, impactYear?: string): string {
  if (!childImpacts || childImpacts.length === 0) {
    return impactPeriod && impactYear ? `${periodToMonthAbbr(impactPeriod)} ${impactYear}` : '-';
  }
  if (childImpacts.length === 1) {
    return `${periodToMonthAbbr(childImpacts[0].impactPeriod)} ${childImpacts[0].impactYear}`;
  }
  const sorted = [...childImpacts].sort((a, b) => {
    const yearDiff = parseInt(a.impactYear) - parseInt(b.impactYear);
    if (yearDiff !== 0) return yearDiff;
    return parseInt(a.impactPeriod.replace('F','')) - parseInt(b.impactPeriod.replace('F',''));
  });
  let continuous = true;
  for (let i = 1; i < sorted.length; i++) {
    const pY = parseInt(sorted[i-1].impactYear), cY = parseInt(sorted[i].impactYear);
    const pP = parseInt(sorted[i-1].impactPeriod.replace('F','')), cP = parseInt(sorted[i].impactPeriod.replace('F',''));
    if (cY === pY && cP !== pP + 1) { continuous = false; break; }
    if (cY === pY + 1 && !(pP === 12 && cP === 1)) { continuous = false; break; }
    if (cY > pY + 1) { continuous = false; break; }
  }
  if (continuous) {
    const f = sorted[0], l = sorted[sorted.length - 1];
    return `${periodToMonthAbbr(f.impactPeriod)} ${f.impactYear} - ${periodToMonthAbbr(l.impactPeriod)} ${l.impactYear}`;
  }
  return sorted.map(c => `${periodToMonthAbbr(c.impactPeriod)} ${c.impactYear}`).join(', ');
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

function formatProbability(probability: string): { text: string; opacity: string } {
  if (!probability) return { text: '-', opacity: '100' };
  const text = probability === 'High' ? 'H' : probability === 'Medium' ? 'M' : probability === 'Low' ? 'L' : probability;
  const opacity = probability === 'Medium' ? '60' : probability === 'Low' ? '20' : '100';
  return { text, opacity };
}

function compareEntries(baseEntry: Entry, compEntry: Entry): { modifiedFields: string[]; previousValues: Record<string, any> } {
  const modifiedFields: string[] = [];
  const previousValues: Record<string, any> = {};

  const fieldDisplayNames: Record<string, string> = {
    division: "Division", ibpStep: "IBP Step", country: "Country",
    channel: "Channel", subChannel: "Sub Channel", account: "Account",
    brand: "Brand", brandFamily: "Brand Family", rAndO: "Risk vs. Opp.",
    probability: "Probability", categorisation: "Categorisation",
    impact: "Impact", impactUnit: "Impact Unit", impactPeriod: "Impact Period",
    impactYear: "Impact Year", secondaryImpact: "Secondary Impact",
    secondaryImpactUnit: "Secondary Impact Unit", status: "Status",
    description: "Description", detailedDescription: "Detailed Description",
    owner: "Owner", addToForecastByPeriod: "Add to Forecast By Period",
    addToForecastByYear: "Add to Forecast By Year", financialImpactType: "Impact Type",
    impactCurrency: "Financial Impact Currency", impactValue: "Impact Value",
    volumeCases: "Volume (Cases)", volumeImpactType: "Volume Impact Type",
    volumeImpactValue: "Volume Impact Value", noVolumeImpact: "No Volume Impact"
  };

  for (const field of Object.keys(fieldDisplayNames)) {
    const bv = baseEntry[field as keyof Entry];
    const cv = compEntry[field as keyof Entry];

    const isComplex = ['country', 'channel', 'subChannel', 'account', 'brand', 'brandFamily'].includes(field);
    const isDiff = isComplex 
      ? formatValue(bv) !== formatValue(cv)
      : (Array.isArray(bv) && Array.isArray(cv))
        ? JSON.stringify([...bv].sort()) !== JSON.stringify([...cv as string[]].sort())
        : bv !== cv;

    if (isDiff) {
      modifiedFields.push(fieldDisplayNames[field]);
      previousValues[field] = bv;
    }
  }

  const bci = baseEntry.childImpacts || [];
  const cci = compEntry.childImpacts || [];
  if (JSON.stringify(bci) !== JSON.stringify(cci)) {
    modifiedFields.push("Impact Periods");
    previousValues.childImpacts = bci;
  }

  return { modifiedFields, previousValues };
}

async function handleCompare() {
  if (selectedSnapshots.value.length !== 2) {
    ElMessage.warning("Please select exactly 2 snapshots to compare");
    return;
  }

  comparing.value = true;
  try {
    const baselineId = earlierSnapshot.value!.snapshot_id;
    const comparisonId = laterSnapshot.value!.snapshot_id;

    const [baselineData, comparisonData] = await Promise.all([
      snapshotApi.getById(baselineId),
      snapshotApi.getById(comparisonId),
    ]);

    const baselineEntries: Entry[] = baselineData.snapshot.entries || [];
    const comparisonEntries: Entry[] = comparisonData.snapshot.entries || [];

    const baselineMap = new Map<string, Entry>();
    baselineEntries.forEach(e => baselineMap.set(e.originalEntryId || e.id, e));

    const comparisonMap = new Map<string, Entry>();
    comparisonEntries.forEach(e => comparisonMap.set(e.originalEntryId || e.id, e));

    const compared: ComparedEntry[] = [];

    comparisonEntries.forEach(compEntry => {
      const key = compEntry.originalEntryId || compEntry.id;
      const baseEntry = baselineMap.get(key);
      if (!baseEntry) {
        compared.push({ ...compEntry, changeStatus: 'New' });
      } else {
        const { modifiedFields, previousValues } = compareEntries(baseEntry, compEntry);
        compared.push({
          ...compEntry,
          changeStatus: modifiedFields.length > 0 ? 'Modified' : 'Unchanged',
          modifiedFields,
          previousValues,
        });
      }
    });

    baselineEntries.forEach(baseEntry => {
      const key = baseEntry.originalEntryId || baseEntry.id;
      if (!comparisonMap.has(key)) {
        compared.push({ ...baseEntry, changeStatus: 'Deleted' });
      }
    });

    comparedEntries.value = compared;
    showComparison.value = true;
    comparisonMode.value = false;
    ElMessage.success("Comparison completed");
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || "Failed to compare snapshots");
  } finally {
    comparing.value = false;
  }
}
</script>

<style scoped>
.page-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary);
  margin: 4px 0 0;
}

/* Compare button row */
.compare-btn-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

/* Compare mode banner */
.compare-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.compare-banner-left {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1d4ed8;
}

.compare-banner-text {
  font-weight: 600;
}

.compare-banner-right {
  display: flex;
  gap: 8px;
}

/* Comparison result header */
.comparison-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.comparison-labels {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: var(--text-secondary);
}

.arrow {
  color: var(--text-secondary);
}

/* Summary badges */
.comparison-summary {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.ml-auto {
  margin-left: auto;
}

/* Column toggle popover */
.column-toggle {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 360px;
  overflow-y: auto;
}

.column-toggle-title {
  font-weight: 600;
  font-size: 13px;
  margin: 0 0 8px;
}

.column-toggle-item {
  padding: 2px 0;
}

/* Table */
.table-wrapper {
  overflow-x: auto;
}

/* Row colours (injected via row-class-name) */
:deep(.row-new) {
  background-color: #f0fdf4 !important;
}

:deep(.row-modified) {
  background-color: #eff6ff !important;
}

:deep(.row-deleted) {
  background-color: #fff1f2 !important;
  opacity: 0.7;
}

/* Previous-value strikethrough */
.prev-value {
  font-size: 11px;
  color: #9ca3af;
  text-decoration: line-through;
  margin-top: 2px;
}

/* Snapshot list */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 12px;
  color: var(--text-secondary);
}

.snapshots-grid {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.department-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.snapshot-card {
  transition: box-shadow 0.2s;
}

.snapshot-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.snapshot-card.is-selected {
  outline: 2px solid var(--el-color-primary);
  outline-offset: 2px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.snapshot-name {
  font-weight: 600;
  font-size: 16px;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.snapshot-date {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.snapshot-count {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.snapshot-count strong {
  color: var(--text-primary);
}

.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.card-actions .el-button:first-child {
  flex: 1;
}

/* Utility */
.text-muted { color: var(--text-secondary); }
.text-green  { color: #16a34a; font-size: 13px; }
.text-red    { color: #dc2626; font-size: 13px; }
.text-small  { font-size: 12px; }
.text-italic { font-style: italic; }
</style>