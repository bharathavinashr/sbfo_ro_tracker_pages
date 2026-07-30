<template>
  <div
    class="main-page-wrapper"
     
  >
    <header class="logo-header">
      <img :src="logoUrl" alt="Suntory Oceania" class="header-logo" />
    </header>
    <div class="page-container">
      <div class="page-header">
        <el-button :icon="ArrowLeft" @click="router.push('/snapshots')">Back to Browse</el-button>
        <h1 class="page-title">Snapshot History</h1>
        <p class="page-subtitle">Search and compare all snapshot versions of entries</p>
      </div>

      <!-- Search and Compare Bar -->
      <div class="toolbar-card">
        <div class="search-wrap">
          <el-input
            v-model="searchQuery"
            placeholder="Search snapshots by name, step, or period..."
            :prefix-icon="Search"
            clearable
            class="history-search"
          />
        </div>
        <div class="selection-actions">
          <el-tag v-if="selectedSnapshots.length > 0" type="info" effect="plain">
            {{ selectedSnapshots.length }} selected (Max 2)
          </el-tag>
          <el-button
            :disabled="selectedSnapshots.length !== 2"
            :loading="comparing"
            :icon="ScaleToOriginal"
            @click="handleCompare"
            class="black-icon-btn"
          >
            Compare Selected
          </el-button>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <p>Fetching history...</p>
      </div>

      <template v-else>
        <!-- Snapshot List Table -->
        <div v-if="!showComparison" class="history-list-wrapper">
          <el-table
            :data="filteredSnapshots"
            style="width: 100%"
            @selection-change="handleSelectionChange"
            ref="historyTableRef"
          >
            <el-table-column type="selection" width="55" :selectable="canSelectRow" />
            <el-table-column prop="name" label="Snapshot Name" min-width="200" />
            <el-table-column prop="ibp_step" label="IBP Step" width="180" />
            <el-table-column label="Period" width="120">
              <template #default="{ row }">{{ row.period }} {{ row.year }}</template>
            </el-table-column>
            <el-table-column label="Version" width="80" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.version !== undefined" size="small" class="version-tag">v{{ row.version }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Status" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.is_final" type="success" size="small">Final</el-tag>
                <el-tag v-else type="info" size="small">Draft</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="Created At" width="180">
              <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="Actions" width="120" align="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="router.push(`/snapshots/${row.snapshot_id}`)">View</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- Comparison View (Reused logic from CycleSnapshotsPage) -->
        <div v-else class="comparison-result-area">
          <div class="comparison-meta">
            <div class="comparison-labels">
              <span><strong>Baseline:</strong> {{ earlierSnapshot?.name }}</span>
              <span class="arrow">→</span>
              <span><strong>Comparison:</strong> {{ laterSnapshot?.name }}</span>
            </div>
        <el-button @click="showComparison = false" :icon="Close" class="black-icon-btn">Close Comparison</el-button>
          </div>

          <div class="comparison-table-wrapper">
             <div class="comparison-summary">
               <div class="comparison-summary-left">
                 <el-tag type="success" style="margin-right: 4px;">{{ countByStatus('New') }} New</el-tag>
                 <el-tag type="primary" style="margin-right: 4px;">{{ countByStatus('Modified') }} Modified</el-tag>
                 <el-tag type="danger" style="margin-right: 4px;">{{ countByStatus('Deleted') }} Deleted</el-tag>
                 <el-tag type="info">{{ countByStatus('Unchanged') }} Unchanged</el-tag>
               </div>

               <el-popover placement="bottom-end" :width="240" trigger="click" popper-class="column-popover">
                 <template #reference>
                   <el-button size="small" plain style="color: black;">
                     <svg style="width:14px;height:14px;margin-right:4px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                       <rect x="3" y="3" width="7" height="18"/>
                       <rect x="14" y="3" width="7" height="18"/>
                     </svg>
                     Columns
                   </el-button>
                 </template>
                 <div class="column-selector-container">
                   <p class="column-selector-title">Toggle Columns</p>
                   <div class="column-selector-list">
                     <div v-for="col in columnDefs" :key="col.key" class="column-selector-item">
                       <el-checkbox v-model="visibleColumns[col.key]">{{ col.label }}</el-checkbox>
                     </div>
                   </div>
                 </div>
               </el-popover>
             </div>

             <div class="table-scroll-wrap">
               <table class="data-table">
                 <thead>
                   <tr>
                     <th class="col-expand"></th>
                     <th v-if="visibleColumns.changeStatus" class="col-sm">Change</th>
                     <th v-if="visibleColumns.modifiedFields" class="col-xl">Modified Columns</th>
                     <th v-if="visibleColumns.ibpStep" class="col-md">IBP Step</th>
                     <th v-if="visibleColumns.division" class="col-sm">Division</th>
                     <th v-if="visibleColumns.country" class="col-sm">Country</th>
                     <th v-if="visibleColumns.categorisation" class="col-lg">Categorisation</th>
                     <th v-if="visibleColumns.description" class="col-xl">Short Description</th>
                     <th v-if="visibleColumns.customer" class="col-lg">Customer(s)</th>
                     <th v-if="visibleColumns.product" class="col-lg">Product</th>
                     <th v-if="visibleColumns.rAndO" class="col-md">Risk vs. Opp.</th>
                     <th v-if="visibleColumns.probability" class="col-sm tc">Probability</th>
                     <th v-if="visibleColumns.addToForecastBy" class="col-md">Add to Forecast By</th>
                     <th v-if="visibleColumns.creator" class="col-md">Creator</th>
                     <th v-if="visibleColumns.owner" class="col-md">Owner</th>
                     <th v-if="visibleColumns.status" class="col-md">Status</th>
                     <th v-if="visibleColumns.lastModified" class="col-lg">Last Modified</th>
                     <th v-if="visibleColumns.financialImpactType" class="col-md">Financial Impact Type</th>
                     <th v-if="visibleColumns.currency" class="col-sm">Financial Impact Currency</th>
                     <th v-if="visibleColumns.impact" class="col-md tr">Financial Impact Value</th>
                     <th v-if="visibleColumns.volumeCases" class="col-md tr">Volume (Cases)</th>
                     <th v-if="visibleColumns.volumeImpactType" class="col-lg">Volume Impact Type</th>
                     <th v-if="visibleColumns.volumeImpactValue" class="col-md tr">Volume Impact Value</th>
                     <th v-if="visibleColumns.impactPeriods" class="col-lg">Impact Period(s)</th>
                   </tr>
                 </thead>
                 <tbody>
                   <template v-for="row in comparedEntries" :key="row.id">
                     <tr :class="getRowClass(row)">
                       <td class="col-expand">
                         <button v-if="row.comparedChildren?.length || row.childImpacts?.length" class="expand-btn" @click="toggleExpand(row.originalEntryId || row.id)">
                           <svg :class="['expand-icon', { rotated: expandedRows.has(row.originalEntryId || row.id) }]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                             <polyline points="9 18 15 12 9 6"/>
                           </svg>
                         </button>
                       </td>
                       <td v-if="visibleColumns.changeStatus">
                         <span :class="['status-badge', changeStatusClass(row.changeStatus)]">{{ row.changeStatus }}</span>
                       </td>
                       <td v-if="visibleColumns.modifiedFields">
                         <template v-if="row.changeStatus === 'Modified' && row.modifiedFields?.length">
                           <div class="field-badges-wrap">
                             <span v-for="f in row.modifiedFields" :key="f" class="field-badge">{{ f }}</span>
                           </div>
                         </template>
                         <span v-else-if="row.changeStatus === 'New'" class="text-green">New entry</span>
                         <span v-else-if="row.changeStatus === 'Deleted'" class="text-red">Deleted</span>
                         <span v-else class="cell-muted">-</span>
                       </td>
                       <td v-if="visibleColumns.ibpStep">
                         <div>{{ row.ibpStep || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.ibpStep && row.previousValues.ibpStep !== row.ibpStep" class="prev-value">{{ row.previousValues.ibpStep }}</div>
                       </td>
                       <td v-if="visibleColumns.division">
                         <div>{{ formatValue(row.division) || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.division && formatValue(row.previousValues.division) !== formatValue(row.division)" class="prev-value">{{ formatValue(row.previousValues.division) }}</div>
                       </td>
                       <td v-if="visibleColumns.country">
                         <div>{{ formatValue(row.country) }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.country && formatValue(row.previousValues.country) !== formatValue(row.country)" class="prev-value">{{ formatValue(row.previousValues.country) }}</div>
                       </td>
                       <td v-if="visibleColumns.categorisation">
                         <div>{{ row.categorisation || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.categorisation && row.previousValues.categorisation !== row.categorisation" class="prev-value">{{ row.previousValues.categorisation }}</div>
                       </td>
                       <td v-if="visibleColumns.description">
                         <div class="truncate-text">{{ row.shortDescription || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.shortDescription && row.previousValues.shortDescription !== row.shortDescription" class="prev-value truncate-text">{{ row.previousValues.shortDescription }}</div>
                       </td>
                       <td v-if="visibleColumns.customer">
                         <div v-if="row.account">{{ formatValue(row.account) }}</div>
                         <div v-if="row.subChannel" class="cell-sub">{{ formatValue(row.subChannel) }}</div>
                         <div v-if="row.channel" class="cell-sub italic">{{ formatValue(row.channel) }}</div>
                         <span v-if="!row.account && !row.subChannel && !row.channel">-</span>
                         <div v-if="row.changeStatus === 'Modified' && (row.previousValues?.channel || row.previousValues?.subChannel || row.previousValues?.account)" class="prev-value">
                           {{ [formatValue(row.previousValues.channel), formatValue(row.previousValues.subChannel), formatValue(row.previousValues.account)].filter(Boolean).join(', ') }}
                         </div>
                       </td>
                       <td v-if="visibleColumns.product">
                         <div v-if="row.brand">{{ formatValue(row.brand) }}</div>
                         <div v-if="row.brandFamily" class="cell-sub italic">{{ formatValue(row.brandFamily) }}</div>
                         <span v-if="!row.brand && !row.brandFamily">-</span>
                         <div v-if="row.changeStatus === 'Modified' && (row.previousValues?.brand || row.previousValues?.brandFamily)" class="prev-value">
                           {{ [formatValue(row.previousValues.brand), formatValue(row.previousValues.brandFamily)].filter(Boolean).join(', ') }}
                         </div>
                       </td>
                       <td v-if="visibleColumns.rAndO">
                         <div>{{ row.rAndO || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.rAndO && row.previousValues.rAndO !== row.rAndO" class="prev-value">{{ row.previousValues.rAndO }}</div>
                       </td>
                       <td v-if="visibleColumns.probability" class="tc">
                         <span v-if="row.probability" :class="['prob-badge', `prob-${(row.probability||'').toLowerCase()}`]">
                           {{ (row.probability||'').charAt(0).toUpperCase() }}
                         </span>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.probability && row.previousValues.probability !== row.probability" class="prev-value tc">
                           {{ (row.previousValues.probability||'').charAt(0).toUpperCase() }}
                         </div>
                       </td>
                       <td v-if="visibleColumns.status">
                         <div>{{ row.status || 'Open' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.status && row.previousValues.status !== row.status" class="prev-value">{{ row.previousValues.status }}</div>
                       </td>
                       <td v-if="visibleColumns.addToForecastBy">
                         <div>{{ row.addToForecastByPeriod && row.addToForecastByYear ? `${periodToMonthAbbr(row.addToForecastByPeriod)} ${row.addToForecastByYear}` : '-' }}</div>
                       </td>
                       <td v-if="visibleColumns.creator">
                         <div>{{ row.creator || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.creator && row.previousValues.creator !== row.creator" class="prev-value">{{ row.previousValues.creator }}</div>
                       </td>
                       <td v-if="visibleColumns.owner">
                         <div>{{ row.owner }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.owner && row.previousValues.owner !== row.owner" class="prev-value">{{ row.previousValues.owner }}</div>
                       </td>
                       <td v-if="visibleColumns.lastModified" class="cell-muted">
                         {{ new Date(row.lastModified).toLocaleDateString() }}
                       </td>
                       <td v-if="visibleColumns.financialImpactType">
                         <div>{{ row.financialImpactType || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.financialImpactType && row.previousValues.financialImpactType !== row.financialImpactType" class="prev-value">{{ row.previousValues.financialImpactType }}</div>
                       </td>
                       <td v-if="visibleColumns.currency">
                         <div>{{ row.impactCurrency || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.impactCurrency && row.previousValues.impactCurrency !== row.impactCurrency" class="prev-value">{{ row.previousValues.impactCurrency }}</div>
                       </td>
                       <td v-if="visibleColumns.impact" class="tr fw">
                         <div>{{ row.impact || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.impact && row.previousValues.impact !== row.impact" class="prev-value tr">{{ row.previousValues.impact }}</div>
                       </td>
                       <td v-if="visibleColumns.volumeCases" class="tr">
                         <div>{{ row.volumeCases || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.volumeCases && row.previousValues.volumeCases !== row.volumeCases" class="prev-value tr">{{ row.previousValues.volumeCases }}</div>
                       </td>
                       <td v-if="visibleColumns.volumeImpactType">
                         <div>{{ row.volumeImpactType || '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.volumeImpactType && row.previousValues.volumeImpactType !== row.volumeImpactType" class="prev-value">{{ row.volumeImpactType }}</div>
                       </td>
                       <td v-if="visibleColumns.volumeImpactValue" class="tr">
                         <div>{{ row.volumeImpactValue ? Number(row.volumeImpactValue).toLocaleString() : '-' }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.volumeImpactValue && row.previousValues.volumeImpactValue !== row.volumeImpactValue" class="prev-value tr">
                           {{ row.previousValues.volumeImpactValue ? Number(row.previousValues.volumeImpactValue).toLocaleString() : '-' }}
                         </div>
                       </td>
                       <td v-if="visibleColumns.impactPeriods">
                         <div>{{ formatImpactPeriods(row.childImpacts, row.impactPeriod, row.impactYear) }}</div>
                         <div v-if="row.changeStatus === 'Modified' && row.previousValues?.childImpacts" class="prev-value">
                           {{ formatImpactPeriods(row.previousValues.childImpacts, row.previousValues.impactPeriod, row.previousValues.impactYear) }}
                         </div>
                       </td>
                     </tr>
                     <!-- Child Row Expansion logic -->
                     <template v-if="expandedRows.has(row.originalEntryId || row.id)">
                        <tr v-for="ci in (row.comparedChildren || row.childImpacts || [])" :key="ci.id" :class="['child-row', getRowClass(ci)]">
                           <td class="col-expand"></td> 
                           <td v-if="visibleColumns.changeStatus">
                             <span :class="['status-badge', changeStatusClass(ci.changeStatus || 'Unchanged'), 'dim']">
                               {{ ci.changeStatus || 'Unchanged' }}
                             </span>
                           </td>
                           <td v-if="visibleColumns.modifiedFields">
                             <div v-if="ci.changeStatus === 'Modified'" class="field-badges-wrap">
                               <span v-for="f in ci.modifiedFields" :key="f" class="field-badge">{{ f }}</span>
                             </div>
                             <span v-else class="cell-muted">-</span>
                           </td>
                           <td v-if="visibleColumns.ibpStep" class="cell-muted">{{ row.ibpStep }}</td>
                           <td v-if="visibleColumns.division" class="cell-muted">{{ row.division }}</td> 
                           <td v-if="visibleColumns.country" class="cell-muted">{{ formatValue(row.country) }}</td>
                           <td v-if="visibleColumns.categorisation" class="cell-muted">{{ row.categorisation }}</td>
                           <td v-if="visibleColumns.description" class="cell-muted">{{ row.shortDescription }}</td>
                           <td v-if="visibleColumns.customer" class="cell-muted">
                             {{ [formatValue(row.channel), formatValue(row.subChannel), formatValue(row.account)].filter(Boolean).join(' / ') }}
                           </td>
                           <td v-if="visibleColumns.product" class="cell-muted">
                             {{ [formatValue(row.brand), formatValue(row.brandFamily)].filter(Boolean).join(' / ') }}
                           </td>
                           <td v-if="visibleColumns.rAndO" class="cell-muted">{{ row.rAndO }}</td>
                           <td v-if="visibleColumns.probability" class="tc cell-muted">
                             <span v-if="row.probability" :class="['prob-badge', `prob-${(row.probability||'').toLowerCase()}`, 'dim']">
                               {{ (row.probability||'').charAt(0).toUpperCase() }}
                             </span>
                           </td>
                           <td v-if="visibleColumns.addToForecastBy" class="cell-muted">-</td>
                           <td v-if="visibleColumns.creator" class="cell-muted">-</td>
                           <td v-if="visibleColumns.owner" class="cell-muted">-</td>
                           <td v-if="visibleColumns.status" class="cell-muted">{{ row.status || 'Open' }}</td>
                           <td v-if="visibleColumns.lastModified" class="cell-muted">-</td>
                           <td v-if="visibleColumns.financialImpactType" class="cell-muted">{{ row.financialImpactType || '-' }}</td>
                           <td v-if="visibleColumns.currency" class="cell-muted">{{ row.impactCurrency || '-' }}</td>
                           <td v-if="visibleColumns.impact" class="tr fw">
                             <div>{{ ci.impact || '-' }}</div>
                             <div v-if="ci.changeStatus === 'Modified' && ci.previousValues?.impact && ci.previousValues.impact !== ci.impact" class="prev-value tr">
                               {{ ci.previousValues.impact }}
                             </div>
                           </td>
                           <td v-if="visibleColumns.volumeCases" class="tr cell-muted">
                             <div>{{ ci.volumeCases || '-' }}</div>
                             <div v-if="ci.changeStatus === 'Modified' && ci.previousValues?.volumeCases && ci.previousValues.volumeCases !== ci.volumeCases" class="prev-value tr">
                               {{ ci.previousValues.volumeCases }}
                             </div>
                           </td>
                           <td v-if="visibleColumns.volumeImpactType" class="cell-muted">{{ row.volumeImpactType || '-' }}</td>
                           <td v-if="visibleColumns.volumeImpactValue" class="tr">
                             <div>{{ ci.volumeImpactValue ? Number(ci.volumeImpactValue).toLocaleString() : '-' }}</div>
                             <div v-if="ci.changeStatus === 'Modified' && ci.previousValues?.volumeImpactValue && ci.previousValues.volumeImpactValue !== ci.volumeImpactValue" class="prev-value tr">
                               {{ ci.previousValues.volumeImpactValue ? Number(ci.previousValues.volumeImpactValue).toLocaleString() : '-' }}
                             </div>
                           </td>
                           <td v-if="visibleColumns.impactPeriods">
                             {{ ci.impactPeriod && ci.impactYear ? `${periodToMonthAbbr(ci.impactPeriod)} ${ci.impactYear}` : '-' }}
                           </td>
                        </tr>
                     </template>
                   </template>
                 </tbody>
               </table>
             </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { ArrowLeft, Search, Loading, ScaleToOriginal, Close } from "@element-plus/icons-vue"; 
import logoUrl from "@/assets/SuntoryOceania-Logo-RGB-Reversed.png";
import { snapshotApi } from "@/services/api";
import backgroundImage from "@/assets/SuntoryOceania-Patterns-RGB-Blue-Water_Ripples.png";

interface ChildImpact {
  id: number;
  impactYear: string; // 2023, 2024, etc.
  impactPeriod: string; // F01, F02, etc.
  nsvAud?: string;
  nsvNzd?: string;
  volumeLitres?: string;
  volumeCases?: string; // Calculated volume impact
  volumeImpactValue?: string; // Calculated volume impact
  impact?: string; // Calculated financial impact
  financialImpactType?: string;
  impactCurrency?: string;
}

interface Entry {
  id: number;
  originalEntryId?: number;
  division: string;
  ibpStep?: string;
  rAndO: string;
  probability: string;
  impactPeriod?: string;
  impactYear?: string;
  addToForecastByPeriod?: string;
  addToForecastByYear?: string;
  categorisation: string;
  nsvAud?: string;
  nsvNzd?: string;
  volumeLitres?: string;
  primaryImpact?: string;
  financialImpactType?: string;
  volumeCases?: string; // Raw volume cases
  volumeImpactType?: string;
  volumeImpactValue?: string; // Calculated volume impact
  impact?: string; // Calculated financial impact
  impactCurrency?: string;
  owner: string;
  creator?: string;
  lastModified: string;
  status?: string;
  shortDescription?: string;
  description?: string;
  country: Record<string, string>; // {company_code: country_name}
  channel: Record<string, string>; // {channel_code: channel_name}
  subChannel: Record<string, string>; // {subchannel_code: subchannel_name}
  account: Record<string, string>; // {account_code: account_name}
  brand: Record<string, string>;
  brandFamily?: Record<string, string>;
  childImpacts?: ChildImpact[];
}

type ChangeStatus = 'New' | 'Modified' | 'Deleted' | 'Unchanged';

interface ComparedChildImpact extends ChildImpact {
  changeStatus: ChangeStatus;
  modifiedFields?: string[];
  previousValues?: Record<string, any>;
}

interface SnapshotGroup {
  snapshot_id: string;
  name: string;
  period: string;
  year: string;
  ibp_step: string;
  entries_count: number;
  created_at: string;
  is_final: boolean;
  version?: number;
}

interface ComparedEntry extends Entry {
  changeStatus: ChangeStatus;
  modifiedFields?: string[];
  previousValues?: Record<string, any>;
  comparedChildren?: ComparedChildImpact[];
}

const router = useRouter();
const loading = ref(true);
const comparing = ref(false);
const snapshots = ref<SnapshotGroup[]>([]);
const searchQuery = ref("");
const selectedSnapshots = ref<string[]>([]);
const historyTableRef = ref<any>(null);
const showComparison = ref(false);
const comparedEntries = ref<any[]>([]);
const expandedRows = ref<Set<string | number>>(new Set());

// Column visibility logic
const visibleColumns = ref<Record<string, boolean>>({ // Default visibility
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
  addToForecastBy:     false,
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
  { key: 'changeStatus',   label: 'Change Status' },
  { key: 'modifiedFields', label: 'Modified Fields' },
  { key: 'ibpStep',        label: 'IBP Step' },
  { key: 'division',       label: 'Division' },
  { key: 'categorisation', label: 'Categorisation' },
  { key: 'country', label: 'Country' },
  { key: 'description',    label: 'Short Description' },
  { key: 'customer', label: 'Customer(s)' },
  { key: 'product', label: 'Product' },
  { key: 'rAndO',          label: 'Risk vs. Opp.' },
  { key: 'probability',    label: 'Probability' },
  { key: 'addToForecastBy', label: 'Add to Forecast By' },
  { key: 'creator', label: 'Creator' },
  { key: 'owner', label: 'Owner' },
  { key: 'status', label: 'Status' },
  { key: 'lastModified', label: 'Last Modified' },
  { key: 'financialImpactType', label: 'Financial Impact Type' },
  { key: 'currency', label: 'Financial Impact Currency' },
  { key: 'impact', label: 'Financial Impact Value' },
  { key: 'volumeCases', label: 'Volume (Cases)' },
  { key: 'volumeImpactType', label: 'Volume Impact Type' },
  { key: 'volumeImpactValue', label: 'Volume Impact Value' },
  { key: 'impactPeriods',  label: 'Impact Period(s)' },
];
const filteredSnapshots = computed(() => {
  if (!searchQuery.value) return snapshots.value;
  const q = searchQuery.value.toLowerCase();
  return snapshots.value.filter(s =>
    s.name.toLowerCase().includes(q) ||
    s.ibp_step.toLowerCase().includes(q) ||
    s.period.toLowerCase().includes(q) ||
    s.year.toString().includes(q)
  );
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

onMounted(fetchSnapshots);

async function fetchSnapshots() {
  loading.value = true;
  try {
    const data = await snapshotApi.getAll();
    console.log("API Response received:", data);
    // Sort snapshots by creation date descending
    snapshots.value = data.snapshots.sort((a: SnapshotGroup, b: SnapshotGroup) => 
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
    console.log("Snapshots loaded:", snapshots.value.length);
  } catch (error) {
    ElMessage.error("Failed to load snapshot history");
  } finally {
    loading.value = false;
  }
}

function handleSelectionChange(val: SnapshotGroup[]) {
  selectedSnapshots.value = val.map(s => s.snapshot_id);
  if (selectedSnapshots.value.length > 2) {
    ElMessage.warning("Please select exactly 2 snapshots to compare");
  }
}

function canSelectRow(row: SnapshotGroup) {
  // Allow selection if it's already selected, or if we have less than 2 selected
  return selectedSnapshots.value.includes(row.snapshot_id) || selectedSnapshots.value.length < 2;
}

function formatDate(dateString: string) {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString("en-US", {
    year: "numeric", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit"
  });
}

// ── Comparison Logic (Synced with CycleSnapshotsPage.vue) ─────────────────────

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

function periodToMonthAbbr(period?: string): string {
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

function compareEntries(baseEntry: any, compEntry: any) {
  const modifiedFields: string[] = [];
  const previousValues: any = {};
  const fieldDisplayNames: any = {
    ibpStep: "IBP Step", rAndO: "Risk vs. Opp.", probability: "Probability",
    categorisation: "Categorisation", impact: "Value", status: "Status",
    division: "Division", shortDescription: "Short Description"
  };

  for (const field in fieldDisplayNames) {
    if (baseEntry[field] !== compEntry[field]) {
      modifiedFields.push(fieldDisplayNames[field]);
      previousValues[field] = baseEntry[field];
    }
  }

  const comparedChildren: any[] = [];
  const bci = baseEntry.childImpacts || [];
  const cci = compEntry.childImpacts || [];

  cci.forEach((compChild: any) => {
    const baseChild = bci.find((b: any) => b.impactPeriod === compChild.impactPeriod && b.impactYear === compChild.impactYear);
    if (!baseChild) comparedChildren.push({ ...compChild, changeStatus: 'New' });
    else if (baseChild.impact !== compChild.impact) {
      comparedChildren.push({ 
        ...compChild, 
        changeStatus: 'Modified', 
        modifiedFields: ['Value'],
        previousValues: { impact: baseChild.impact }
      });
      if (!modifiedFields.includes("Impact Periods")) modifiedFields.push("Impact Periods");
      if (!previousValues.childImpacts) previousValues.childImpacts = bci;
    } else comparedChildren.push({ ...compChild, changeStatus: 'Unchanged' });
  });

  return { modifiedFields, previousValues, comparedChildren };
}

async function handleCompare() {
  if (selectedSnapshots.value.length !== 2) return;
  
  comparing.value = true;
  expandedRows.value.clear();
  try {
    const [baseData, compData] = await Promise.all([
      snapshotApi.getById(earlierSnapshot.value!.snapshot_id),
      snapshotApi.getById(laterSnapshot.value!.snapshot_id),
    ]);

    const baselineEntries = baseData.snapshot.entries || [];
    const comparisonEntries = compData.snapshot.entries || [];
    const baselineMap = new Map<string, Entry>();
    baselineEntries.forEach((e: Entry) => baselineMap.set(String(e.originalEntryId || e.id), e));

    const comparisonMap = new Map<string, Entry>();
    comparisonEntries.forEach((e: Entry) => comparisonMap.set(String(e.originalEntryId || e.id), e));

    const compared: any[] = [];
    comparisonEntries.forEach((compEntry: any) => {
      const baseEntry = baselineMap.get(String(compEntry.originalEntryId || compEntry.id));
      if (!baseEntry) {
        compared.push({ 
          ...compEntry, 
          changeStatus: 'New',
          comparedChildren: (compEntry.childImpacts || []).map((c: any) => ({ ...c, changeStatus: 'New' }))
        });
      } else {
        const { modifiedFields, previousValues, comparedChildren } = compareEntries(baseEntry, compEntry);
        compared.push({
          ...compEntry,
          changeStatus: modifiedFields.length > 0 ? 'Modified' : 'Unchanged',
          modifiedFields,
          previousValues,
          comparedChildren
        });
      }
    });

    baselineEntries.forEach((baseEntry: any) => {
      const key = String(baseEntry.originalEntryId || baseEntry.id);
      if (!comparisonMap.has(key)) {
        compared.push({ 
          ...baseEntry, 
          changeStatus: 'Deleted',
          comparedChildren: (baseEntry.childImpacts || []).map((c: any) => ({ ...c, changeStatus: 'Deleted' }))
        });
      }
    });

    comparedEntries.value = compared;
    showComparison.value = true;
    ElMessage.success("Comparison generated successfully");
  } catch (error) {
    ElMessage.error("Comparison failed");
  } finally {
    comparing.value = false;
  }
  selectedSnapshots.value = []; // Clear selection after comparison
}

function toggleExpand(id: any) {
  const s = new Set(expandedRows.value);
  if (s.has(id)) s.delete(id);
  else s.add(id);
  expandedRows.value = s;
}

function countByStatus(status: string) {
  return comparedEntries.value.filter(e => e.changeStatus === status).length;
}

function changeStatusClass(status: string) {
  if (status === 'New') return 'status-success';
  if (status === 'Modified') return 'status-primary';
  if (status === 'Deleted') return 'status-danger';
  return 'status-info';
}

function getRowClass(row: any) {
  if (row.changeStatus === 'New') return 'row-new';
  if (row.changeStatus === 'Modified') return 'row-modified';
  return '';
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
}

.logo-header {
  width: 100%;
  box-sizing: border-box;
  margin: 0 auto;
  padding: 16px 24px;
  background: #00325D;
}

.header-logo { height: 40px; }

.page-title {
  font-family: 'Jost', Arial, sans-serif; /* Already Jost */
  font-size: 28px;
  font-weight: 500;
  margin: 0;
  color: var(--text-title-heading);
  line-height: 1.2;
}

.page-subtitle {
  font-family: 'Work Sans', Arial, sans-serif;
  font-weight: 400;
  font-size: 15px;
  color: var(--text-secondary);
  margin: 4px 0 0;
  padding-bottom: 20px;
  padding-top: 10px;
}

/* Toolbar */
.toolbar-card {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.history-search { width: 400px; }

.selection-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.selection-actions :deep(.el-button) {
  width: 200px;
  color: #000;
  border-color: var(--border-color);
}

.version-tag {
  background-color: #e0e0e0;
  color: #333;
  border: none;
}

.black-icon-btn {
  color: #000 !important; /* Ensure text color is black for the button itself */
}

/* Ensures the icon specifically is rendered as black */
.black-icon-btn :deep(.el-icon) {
  color: #000 !important;
}

.history-list-wrapper {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

/* Comparison Result Area */
.comparison-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  background: #f8fafc;
  padding: 12px 20px;
  border-radius: 8px;
}

.comparison-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(180deg, rgba(245,247,251,.8) 0%, rgba(241,245,252,.9) 100%);
  border-radius: 10px 10px 0 0;
}

.comparison-summary-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.comparison-labels {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.arrow { color: #94a3b8; }

.comparison-table-wrapper {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
}

/* Reused Table Styles from CycleSnapshotsPage */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px; 
  color: var(--text-primary);
}

.data-table th {
  background: #f8f9fc;
  font-weight: 600;
  font-size: 12px;
  padding: 9px 12px;
  white-space: nowrap;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-secondary);
  text-align: left;
}

:deep(.el-table th) {
  background-color: #f8f9fc !important;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 12px;
  font-family: 'Work Sans', Arial, sans-serif;
}

.data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f2f5;
  vertical-align: middle;
  white-space: nowrap;
  font-size: 12px;
}

:deep(.el-table td) {
  color: var(--text-secondary);
  font-size: 12px;
  font-family: 'Work Sans', Arial, sans-serif;
}


.row-new td { background-color: #f0fdf4 !important; }
.row-modified td { background-color: #eff6ff !important; }
.row-deleted td { background-color: #fff1f2 !important; opacity: 0.7; }

/* Prev values & Badges */
.prev-value {
  font-size: 11px;
  color: #9ca3af;
  text-decoration: line-through;
  margin-top: 2px;
}

.prob-badge {
  display: inline-flex; 
  align-items: center; 
  justify-content: center;
  width: 28px; 
  height: 28px; 
  border-radius: 6px;
  font-size: 12px; 
  font-weight: 700;
}
.prob-high   { background: #0d9488; color: #fff; }
.prob-medium { background: #cffafe; color: #0e7490; }
.prob-low    { background: #e0f2fe; color: #0369a1; }

/* Column Selector Styles */
:deep(.column-popover) {
  padding: 12px 0 12px 12px !important;
}
.column-selector-title {
  font-weight: 600; font-size: 14px; margin: 0 0 12px 0;
}
.column-selector-list {
  display: flex; flex-direction: column; max-height: 250px; overflow-y: auto;
}
.column-selector-item { margin-bottom: 8px; }
.text-green { color: #16a34a; font-size: 13px; }
.text-red { color: #dc2626; font-size: 13px; }

.status-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.status-success { background: #dcfce7; color: #166534; }
.status-primary { background: #dbeafe; color: #1e40af; }
.status-danger  { background: #fee2e2; color: #991b1b; }
.status-info { background: #f1f5f9; color: #475569; }

.field-badges-wrap { display: flex; flex-wrap: wrap; gap: 4px; }
.field-badge {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #64748b;
}

.expand-icon {
  width: 16px;
  transition: transform 0.2s;
}

.expand-icon.rotated { transform: rotate(90deg); }

.child-row td {
  background: #fafafa;
  padding-left: 12px;
}

.child-row:hover td {
  background: #f3f4f6 !important;
}

.tr { text-align: left; }
.fw { font-weight: 600; }

.truncate-text {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.dim { opacity: 0.6; }
.cell-muted { color: #94a3b8; }

.loading-state {
  text-align: center;
  padding: 60px;
  color: #64748b;
}
</style>