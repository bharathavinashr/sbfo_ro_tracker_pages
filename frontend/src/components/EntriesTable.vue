<template>
  <div class="entries-table-wrapper">

    <!-- Quick Filters -->
    <div v-if="!isReadOnly" class="quick-filters-section">
      <p class="section-label">Quick Filters</p>
      <div class="quick-filter-row">
        <button
          v-for="qf in quickFilterDefs"
          :key="qf.key"
          :class="['quick-btn', { active: quickFilters[qf.key] }]"
          @click="toggleQuick(qf.key)"
        >{{ qf.label }}</button>
      </div>
      <div class="quick-filter-row">
        <button
          v-for="dept in departmentOptions"
          :key="dept"
          :class="['quick-btn', { active: store.filters.department === dept }]"
          @click="toggleDepartment(dept)"
        >{{ dept }}</button>
      </div>
    </div>

    <!-- All Filters (collapsible) -->
    <div v-if="!isReadOnly" class="all-filters-section">
      <div class="all-filters-header" @click="allFiltersOpen = !allFiltersOpen">
        <span class="all-filters-title">All Filters</span>
        <svg
          :class="['chevron-icon', { open: allFiltersOpen }]"
          viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      <div v-show="allFiltersOpen" class="all-filters-body">
        <!-- Row 1 -->
        <el-row :gutter="16" class="filter-row">
          <el-col :span="6">
            <label class="filter-label">Div.</label>
            <el-select v-model="store.filters.division" clearable placeholder="All" @change="store.fetchEntries()">
              <el-option v-for="d in divisionOptions" :key="d" :value="d" :label="d" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Country</label>
            <el-select v-model="store.filters.country" clearable placeholder="All" @change="store.fetchEntries()">
              <el-option v-for="c in countryOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Categorisation</label>
            <el-select v-model="store.filters.categorisation" clearable placeholder="All" @change="store.fetchEntries()">
              <el-option v-for="c in categOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Status</label>
            <el-select v-model="store.filters.status" clearable placeholder="All" @change="store.fetchEntries()">
              <el-option v-for="s in statusOptions" :key="s" :value="s" :label="s" />
            </el-select>
          </el-col>
        </el-row>

        <!-- Row 2 -->
        <el-row :gutter="16" class="filter-row">
          <el-col :span="6">
            <label class="filter-label">Owner</label>
            <el-select v-model="store.filters.owner" clearable placeholder="All" filterable @change="store.fetchEntries()">
              <el-option v-for="u in ownerOptions" :key="u.email" :value="u.email" :label="u.display_name ? `${u.display_name} (${u.email})` : u.email" />
            </el-select>
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Department</label>
            <el-select v-model="store.filters.department" clearable placeholder="All" @change="store.fetchEntries()">
              <el-option v-for="d in departmentOptions" :key="d" :value="d" :label="d" />
            </el-select>
          </el-col>
        </el-row>

        <!-- Customer Filters -->
        <p class="filter-group-label">Customer Filters</p>
        <el-row :gutter="16" class="filter-row">
          <el-col :span="8">
            <label class="filter-label">Channel</label>
            <el-select v-model="store.filters.channel" clearable placeholder="All">
              <el-option v-for="c in channelOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <label class="filter-label">Sub-Channel</label>
            <el-select v-model="store.filters.sub_channel" clearable placeholder="All" :disabled="!store.filters.channel">
              <el-option v-for="c in subChannelOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-col>
          <el-col :span="8">
            <label class="filter-label">Account</label>
            <el-select v-model="store.filters.account" clearable placeholder="All" :disabled="!store.filters.sub_channel" @change="store.fetchEntries()">
              <el-option v-for="a in accountOptions" :key="a" :value="a" :label="a" />
            </el-select>
          </el-col>
        </el-row>

        <!-- Product Filters -->
        <p class="filter-group-label">Product Filters</p>
        <el-row :gutter="16" class="filter-row">
          <el-col :span="12">
            <label class="filter-label">Brand</label>
            <el-select v-model="store.filters.brand" clearable placeholder="All">
              <el-option v-for="b in brandOptions" :key="b" :value="b" :label="b" />
            </el-select>
          </el-col>
          <el-col :span="12">
            <label class="filter-label">Brand Family</label>
            <el-select v-model="store.filters.brand_family" clearable placeholder="All" :disabled="!store.filters.brand" @change="store.fetchEntries()">
              <el-option v-for="b in brandFamilyOptions" :key="b" :value="b" :label="b" />
            </el-select>
          </el-col>
        </el-row>

        <div class="filter-actions">
          <el-button size="small" @click="clearFilters">Clear All Filters</el-button>
        </div>
      </div>
    </div>

    <!-- Table Toolbar -->
    <div class="table-toolbar">
      <span class="entry-count">{{ filteredEntries.length }} entries</span>
      <div class="toolbar-right" v-if="!isReadOnly">
        <div class="split-view-control">
          <span class="split-view-label">Split view by:</span>
          <el-select
            v-model="splitBy"
            multiple
            collapse-tags
            collapse-tags-tooltip
            placeholder="None"
            size="small"
            style="width: 160px"
          >
            <el-option
              v-for="opt in splitByOptions"
              :key="opt.key"
              :value="opt.key"
              :label="opt.label"
            />
          </el-select>
        </div>
        <el-popover placement="bottom-end" :width="260" trigger="click">
          <template #reference>
            <el-button size="small" plain>Columns</el-button>
          </template>
          <div class="column-selector">
            <p class="column-selector-title">Visible Columns</p>
            <el-checkbox v-model="colVisible.department">Department</el-checkbox>
            <el-checkbox v-model="colVisible.subChannel">Sub-Channel</el-checkbox>
            <el-checkbox v-model="colVisible.account">Account</el-checkbox>
            <el-checkbox v-model="colVisible.brandFamily">Brand Family</el-checkbox>
            <el-checkbox v-model="colVisible.nsvAud">NSV (AUD)</el-checkbox>
            <el-checkbox v-model="colVisible.nsvNzd">NSV (NZD)</el-checkbox>
            <el-checkbox v-model="colVisible.volumeLitres">Vol. (L)</el-checkbox>
            <el-checkbox v-model="colVisible.impactPeriod">Impact Period</el-checkbox>
            <el-checkbox v-model="colVisible.creator">Creator</el-checkbox>
          </div>
        </el-popover>
      </div>
    </div>

    <!-- Grouped view -->
    <template v-if="splitBy.length && !isReadOnly">
      <div
        v-for="group in groupedEntries"
        :key="group.key"
        class="split-group"
      >
        <div class="split-group-header">
          <div class="split-group-breadcrumb">
            <template v-for="(item, idx) in group.breadcrumb" :key="idx">
              <span v-if="idx > 0" class="split-sep">›</span>
              <span class="split-chip">
                <span class="split-chip-label">{{ item.label }}</span>
                <span class="split-chip-val">{{ item.val }}</span>
              </span>
            </template>
          </div>
          <span class="split-count">{{ group.entries.length }} {{ group.entries.length === 1 ? 'entry' : 'entries' }}</span>
        </div>
        <el-table
          :data="group.entries"
          border
          stripe
          style="width: 100%"
          :row-class-name="rowClassName"
        >
          <el-table-column type="expand">
            <template #default="{ row }">
              <div v-if="row.childImpacts && row.childImpacts.length" class="child-impacts">
                <p class="child-impacts-title">Impact Details</p>
                <el-table :data="row.childImpacts" size="small" border>
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
              <div v-else style="color: var(--text-muted); padding: 8px">No impact details</div>
            </template>
          </el-table-column>
          <el-table-column label="Division" width="90" align="center">
            <template #default="{ row }">
              <el-tooltip :content="row.division" placement="top">
                <span style="font-size:16px; cursor:default;">{{ divisionEmoji(row.division) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column v-if="colVisible.department" prop="department" label="Department" min-width="130" />
          <el-table-column label="Country" width="90" align="center">
            <template #default="{ row }">
              <el-tooltip :content="row.country" placement="top">
                <span>{{ countryAbbr(row.country) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="channel" label="Channel" width="120" />
          <el-table-column v-if="colVisible.subChannel" prop="subChannel" label="Sub-Channel" width="140" />
          <el-table-column v-if="colVisible.account" prop="account" label="Account" min-width="130" />
          <el-table-column prop="brand" label="Brand" width="120" />
          <el-table-column v-if="colVisible.brandFamily" prop="brandFamily" label="Brand Family" min-width="140">
            <template #default="{ row }">{{ Array.isArray(row.brandFamily) ? row.brandFamily.join(", ") : row.brandFamily }}</template>
          </el-table-column>
          <el-table-column prop="rAndO" label="R&O" width="120">
            <template #default="{ row }">
              <el-tag :type="row.rAndO === 'Risk' ? 'danger' : 'success'" size="small">{{ row.rAndO }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="Probability" width="110" align="center">
            <template #default="{ row }">
              <el-tooltip :content="row.probability" placement="top">
                <span :class="['prob-badge', `prob-${(row.probability || '').toLowerCase()}`]">
                  {{ (row.probability || '').charAt(0).toUpperCase() }}
                </span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column prop="categorisation" label="Category" min-width="120" />
          <el-table-column label="Primary Impact" width="150">
            <template #default="{ row }">{{ formatPrimaryImpact(row) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.nsvAud" label="NSV (AUD)" width="120">
            <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvAud')) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.nsvNzd" label="NSV (NZD)" width="120">
            <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvNzd')) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.volumeLitres" label="Vol. (L)" width="110">
            <template #default="{ row }">{{ formatVol(sumChildField(row, 'volumeLitres')) }}</template>
          </el-table-column>
          <el-table-column v-if="colVisible.impactPeriod" label="Impact Period" width="130">
            <template #default="{ row }">
              {{ row.impactPeriod && row.impactYear ? `${row.impactPeriod} / ${row.impactYear}` : (row.impactPeriod || row.impactYear || '-') }}
            </template>
          </el-table-column>
          <el-table-column prop="owner" label="Owner" min-width="120" />
          <el-table-column v-if="colVisible.creator" prop="creator" label="Creator" min-width="120" />
          <el-table-column prop="status" label="Status" width="190">
            <template #default="{ row }">
              <el-select v-if="canEditStatusRow(row)" :model-value="row.status" size="small" style="width: 100%" @change="(val: string) => handleStatusChange(row, val)">
                <el-option v-for="s in allowedStatusRow(row)" :key="s" :value="s" :label="s" />
              </el-select>
              <el-tag v-else :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="lastModified" label="Last Modified" width="155">
            <template #default="{ row }">{{ formatDate(row.lastModified) }}</template>
          </el-table-column>
          <el-table-column label="Actions" width="140" align="center">
            <template #default="{ row }">
              <div class="action-btns">
                <button class="action-icon" @click="$emit('history', row)" title="History">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
                <button v-if="store.canCreate" class="action-icon" @click="$emit('duplicate', row)" title="Duplicate">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                </button>
                <button v-if="canEditRow(row)" class="action-icon" @click="handleEditClick(row)" title="Edit">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                </button>
                <el-popconfirm v-if="canDeleteRow(row)" title="Delete all versions of this entry?" confirm-button-type="danger" @confirm="$emit('delete', row)">
                  <template #reference>
                    <button class="action-icon action-icon--danger" title="Delete">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                    </button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <!-- Flat table (no split or read-only) -->
    <el-table
      v-else
      :data="filteredEntries"
      v-loading="isReadOnly ? false : store.loading"
      border
      stripe
      style="width: 100%"
      :row-class-name="rowClassName"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div v-if="row.childImpacts && row.childImpacts.length" class="child-impacts">
            <p class="child-impacts-title">Impact Details</p>
            <el-table :data="row.childImpacts" size="small" border>
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
          <div v-else style="color: var(--text-muted); padding: 8px">No impact details</div>
        </template>
      </el-table-column>
      <el-table-column label="Division" width="90" align="center">
        <template #default="{ row }">
          <el-tooltip :content="row.division" placement="top">
            <span style="font-size:16px; cursor:default;">{{ divisionEmoji(row.division) }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column v-if="colVisible.department" prop="department" label="Department" min-width="130" />
      <el-table-column label="Country" width="90" align="center">
        <template #default="{ row }">
          <el-tooltip :content="row.country" placement="top">
            <span>{{ countryAbbr(row.country) }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="channel" label="Channel" width="120" />
      <el-table-column v-if="colVisible.subChannel" prop="subChannel" label="Sub-Channel" width="140" />
      <el-table-column v-if="colVisible.account" prop="account" label="Account" min-width="130" />
      <el-table-column prop="brand" label="Brand" width="120" />
      <el-table-column v-if="colVisible.brandFamily" prop="brandFamily" label="Brand Family" min-width="140">
        <template #default="{ row }">
          {{ Array.isArray(row.brandFamily) ? row.brandFamily.join(", ") : row.brandFamily }}
        </template>
      </el-table-column>
      <el-table-column prop="rAndO" label="R&O" width="120">
        <template #default="{ row }">
          <el-tag :type="row.rAndO === 'Risk' ? 'danger' : 'success'" size="small">{{ row.rAndO }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Probability" width="110" align="center">
        <template #default="{ row }">
          <el-tooltip :content="row.probability" placement="top">
            <span :class="['prob-badge', `prob-${(row.probability || '').toLowerCase()}`]">
              {{ (row.probability || '').charAt(0).toUpperCase() }}
            </span>
          </el-tooltip>
        </template>
      </el-table-column>
      <el-table-column prop="categorisation" label="Category" min-width="120" />
      <el-table-column label="Primary Impact" width="150">
        <template #default="{ row }">{{ formatPrimaryImpact(row) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.nsvAud" label="NSV (AUD)" width="120">
        <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvAud')) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.nsvNzd" label="NSV (NZD)" width="120">
        <template #default="{ row }">{{ formatMoney(sumChildField(row, 'nsvNzd')) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.volumeLitres" label="Vol. (L)" width="110">
        <template #default="{ row }">{{ formatVol(sumChildField(row, 'volumeLitres')) }}</template>
      </el-table-column>
      <el-table-column v-if="colVisible.impactPeriod" label="Impact Period" width="130">
        <template #default="{ row }">
          {{ row.impactPeriod && row.impactYear ? `${row.impactPeriod} / ${row.impactYear}` : (row.impactPeriod || row.impactYear || '-') }}
        </template>
      </el-table-column>
      <el-table-column prop="owner" label="Owner" min-width="120" />
      <el-table-column v-if="colVisible.creator" prop="creator" label="Creator" min-width="120" />
      <el-table-column prop="status" label="Status" width="190">
        <template #default="{ row }">
          <el-select v-if="canEditStatusRow(row)" :model-value="row.status" size="small" style="width: 100%" @change="(val: string) => handleStatusChange(row, val)">
            <el-option v-for="s in allowedStatusRow(row)" :key="s" :value="s" :label="s" />
          </el-select>
          <el-tag v-else :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastModified" label="Last Modified" width="155">
        <template #default="{ row }">{{ formatDate(row.lastModified) }}</template>
      </el-table-column>
      <el-table-column v-if="!isReadOnly" label="Actions" width="140" align="center">
        <template #default="{ row }">
          <div class="action-btns">
            <button class="action-icon" @click="$emit('history', row)" title="History">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
            <button v-if="store.canCreate" class="action-icon" @click="$emit('duplicate', row)" title="Duplicate">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
            <button v-if="canEditRow(row)" class="action-icon" @click="handleEditClick(row)" title="Edit">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <el-popconfirm v-if="canDeleteRow(row)" title="Delete all versions of this entry?" confirm-button-type="danger" @confirm="$emit('delete', row)">
              <template #reference>
                <button class="action-icon action-icon--danger" title="Delete">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                </button>
              </template>
            </el-popconfirm>
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useEntryStore } from "@/stores/entryStore";
import { useLookupStore } from "@/stores/lookupStore";
import { entryApi } from "@/services/api";
import type { Entry } from "@/types";
import { STATUS_OPTIONS } from "@/types";
import { formatDate, formatMoney, formatVol } from "@/utils/formatters";

const props = withDefaults(
  defineProps<{
    entries: Entry[];
    isReadOnly?: boolean;
    canApprove?: boolean;
  }>(),
  {
    isReadOnly: false,
    canApprove: false,
  }
);

const emit = defineEmits<{
  edit: [entry: Entry];
  duplicate: [entry: Entry];
  delete: [entry: Entry];
  history: [entry: Entry];
  approve: [entry: Entry];
  add: [];
}>();

const store = useEntryStore();
const lookupStore = useLookupStore();
const allFiltersOpen = ref(false);

// Preload all top-level options on mount
onMounted(() => {
  lookupStore.preload();
  if (store.users.length === 0) store.fetchUsers();
});

// Quick filter state
const quickFilters = ref({
  openOnly: false,
  highPriority: false,
  recentlyModified: false,
});

const quickFilterDefs = [
  { key: "openOnly" as const, label: "Show Open Only" },
  { key: "highPriority" as const, label: "Show High Priority Only" },
  { key: "recentlyModified" as const, label: "Show Recently Modified Only" },
];

function toggleQuick(key: keyof typeof quickFilters.value) {
  quickFilters.value[key] = !quickFilters.value[key];
}

function toggleDepartment(dept: string) {
  store.filters.department = store.filters.department === dept ? "" : dept;
  store.fetchEntries();
}

// Client-side quick filter application
const filteredEntries = computed(() => {
  let result = props.entries;
  if (quickFilters.value.openOnly) {
    result = result.filter((e) => e.status === "Open");
  }
  if (quickFilters.value.highPriority) {
    result = result.filter((e) => e.probability === "High" || e.probability === "Very High");
  }
  if (quickFilters.value.recentlyModified) {
    const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
    result = result.filter((e) => e.lastModified && new Date(e.lastModified).getTime() > cutoff);
  }
  return result;
});

// ── Lookup options from store (reactive, updates as cache fills) ──────────
const divisionOptions    = computed(() => lookupStore.getCached("division"));
const countryOptions     = computed(() => lookupStore.getCached("country"));
const channelOptions     = computed(() => lookupStore.getCached("channel"));
const categOptions       = computed(() => lookupStore.getCached("categorisation"));
const statusOptions      = computed(() => lookupStore.getCached("status"));
const departmentOptions  = computed(() => lookupStore.getCached("department"));

// Owner dropdown: users with role 0 (System Admin) or 1 (User)
const ownerOptions = computed(() =>
  store.users.filter((u) => u.role === 0 || u.role === 1)
);

// Cascade: Sub-Channel depends on Channel
const subChannelOptions = computed(() =>
  store.filters.channel
    ? lookupStore.getCached("sub_channel", store.filters.channel)
    : lookupStore.getCached("sub_channel")
);
// Cascade: Account depends on Sub-Channel
const accountOptions = computed(() =>
  store.filters.sub_channel
    ? lookupStore.getCached("account", store.filters.sub_channel)
    : lookupStore.getCached("account")
);

// Brand standalone
const brandOptions = computed(() => lookupStore.getCached("brand"));

// Cascade: Brand Family depends on Brand
const brandFamilyOptions = computed(() =>
  store.filters.brand
    ? lookupStore.getCached("brand_family", store.filters.brand)
    : lookupStore.getCached("brand_family")
);

// When Channel changes: clear sub_channel + account, load sub_channel options
watch(() => store.filters.channel, (val) => {
  store.filters.sub_channel = "";
  store.filters.account = "";
  if (val) lookupStore.loadChildren("sub_channel", val);
  store.fetchEntries();
});

// When Sub-Channel changes: clear account, load account options
watch(() => store.filters.sub_channel, (val) => {
  store.filters.account = "";
  if (val) lookupStore.loadChildren("account", val);
  store.fetchEntries();
});

// When Brand changes: clear brand_family, load brand_family options
watch(() => store.filters.brand, (val) => {
  store.filters.brand_family = "";
  if (val) lookupStore.loadChildren("brand_family", val);
  store.fetchEntries();
});

// ── Split view ────────────────────────────────────────────────────────────
const splitByOptions = [
  { key: "country",     label: "Country" },
  { key: "division",    label: "Division" },
  { key: "department",  label: "Department" },
  { key: "rAndO",       label: "Risk vs. Opportunity" },
  { key: "probability", label: "Priority" },
];

const splitBy = ref<string[]>([]);

const groupedEntries = computed(() => {
  const dims = splitBy.value;
  if (!dims.length) return [];

  const groupMap = new Map<string, { entries: Entry[]; vals: string[] }>();
  for (const row of filteredEntries.value) {
    const vals = dims.map(d => (row as unknown as Record<string, unknown>)[d] as string || "—");
    const key = vals.join("\0");
    if (!groupMap.has(key)) groupMap.set(key, { entries: [], vals });
    groupMap.get(key)!.entries.push(row);
  }

  return Array.from(groupMap.values())
    .sort((a, b) => a.vals.join("").localeCompare(b.vals.join("")))
    .map(({ entries, vals }) => ({
      key: vals.join(" | "),
      breadcrumb: dims.map((d, i) => ({
        label: splitByOptions.find(o => o.key === d)?.label ?? d,
        val: vals[i],
      })),
      entries,
    }));
});

const colVisible = ref({
  department: true,
  subChannel: true,
  account: true,
  brandFamily: true,
  nsvAud: true,
  nsvNzd: true,
  volumeLitres: true,
  impactPeriod: true,
  creator: true,
});

function rowClassName({ row }: { row: Entry }) {
  const classes: string[] = [];
  const statusMap: Record<string, string> = {
    "Approved":             "row-approved",
    "Dismissed":            "row-dismissed",
    "Included in Forecast": "row-forecast",
  };
  if (statusMap[row.status ?? ""]) classes.push(statusMap[row.status ?? ""]);
  if (!row.childImpacts?.length) classes.push("no-expand");
  return classes.join(" ");
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

function canEditRow(row: Entry): boolean {
  const role = store.userRole;
  if (role === "System Admin") return true;
  if (role === "User") return row.status === "Open";
  return store.canCreate;
}

async function handleEditClick(row: Entry) {
  try {
    const { status } = await entryApi.getStatus(row.id);
    if (status !== "Open") {
      ElMessage.warning(`This entry is now "${status}" and can no longer be edited.`);
      await store.fetchEntries();
      return;
    }
  } catch {
    ElMessage.error("Unable to verify entry status. Please refresh and try again.");
    await store.fetchEntries();
    return;
  }
  emit("edit", row);
}

function canDeleteRow(row: Entry): boolean {
  const role = store.userRole;
  if (role === "System Admin") return true;
  if (role === "User") return row.status === "Open";
  return false;
}

function canEditStatusRow(row: Entry): boolean {
  const role = store.userRole;
  const status = row.status;
  if (role === "System Admin") return true;
  if (role === "Department Approver") return status === "Open" || status === "Approved";
  if (role === "Finance Approver") return status === "Approved" || status === "Dismissed" || status === "Included in Forecast";
  return false;
}

function allowedStatusRow(row: Entry): string[] {
  const role = store.userRole;
  const status = row.status ?? "Open";
  if (role === "System Admin") return STATUS_OPTIONS;
  if (role === "Department Approver" && (status === "Open" || status === "Approved")) return ["Open", "Approved"];
  if (role === "Finance Approver") return ["Approved", "Dismissed", "Included in Forecast"];
  return [status];
}

async function handleStatusChange(row: Entry, newStatus: string) {
  try {
    const { status: latestStatus } = await entryApi.getStatus(row.id);
    if (latestStatus !== row.status) {
      ElMessage.warning(`This entry's status has changed to "${latestStatus}". Please review the latest state.`);
      await store.fetchEntries();
      return;
    }
    await entryApi.updateStatus(row.id, newStatus, store.currentUser?.email);
    await store.fetchEntries();
    ElMessage.success("Status updated");
  } catch {
    ElMessage.error("Unable to verify entry status. Please refresh and try again.");
    await store.fetchEntries();
  }
}

function sumChildField(row: Entry, field: "nsvAud" | "nsvNzd" | "volumeLitres"): string | undefined {
  if (!row.childImpacts?.length) return row[field];
  const total = row.childImpacts.reduce((acc, ci) => {
    const v = parseFloat(ci[field] ?? "");
    return acc + (isNaN(v) ? 0 : v);
  }, 0);
  return total === 0 ? undefined : String(total);
}

function formatPrimaryImpact(row: Entry) {
  if (row.primaryImpact === "AUD") return formatMoney(sumChildField(row, "nsvAud")) + " AUD";
  if (row.primaryImpact === "NZD") return formatMoney(sumChildField(row, "nsvNzd")) + " NZD";
  if (row.primaryImpact === "Volume") return formatVol(sumChildField(row, "volumeLitres"));
  return "-";
}


function countryAbbr(country?: string): string {
  if (!country) return "—";
  const map: Record<string, string> = {
    "Australia": "AU",
    "New Zealand": "NZ",
  };
  return map[country] ?? country;
}

function divisionEmoji(division?: string): string {
  if (!division) return "";
  const d = division.toLowerCase();
  if (d.includes("alcohol") && !d.includes("non-alcohol")) return "🍷";
  return "💧";
}

function clearFilters() {
  store.resetFilters();
  quickFilters.value = { openOnly: false, highPriority: false, recentlyModified: false };
  store.fetchEntries();
}
</script>

<style scoped>
.entries-table-wrapper {
  background: var(--bg-primary);
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
  overflow: hidden;
  box-shadow: var(--shadow);
}

/* ── Quick Filters ── */
.quick-filters-section {
  padding: 16px 24px 12px;
  border-bottom: 1px solid var(--border-color);
}

.section-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0 0 10px;
}

.quick-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}
.quick-filter-row:last-child {
  margin-bottom: 0;
}

.quick-btn {
  display: inline-flex;
  align-items: center;
  padding: 5px 14px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  line-height: 1.4;
}
.quick-btn:hover {
  border-color: #6b7280;
  background: #f5f7fa;
}
.quick-btn.active {
  border-color: var(--primary, #030213);
  background: var(--primary, #030213);
  color: #fff;
}

/* ── All Filters ── */
.all-filters-section {
  border-bottom: 1px solid var(--border-color);
}

.all-filters-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 24px;
  cursor: pointer;
  user-select: none;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}
.all-filters-header:hover {
  background: #f9fafb;
}

.chevron-icon {
  width: 16px;
  height: 16px;
  color: var(--text-secondary);
  transition: transform 0.2s;
  flex-shrink: 0;
}
.chevron-icon.open {
  transform: rotate(180deg);
}

.all-filters-body {
  padding: 4px 24px 16px;
}

.filter-row {
  margin-bottom: 12px;
}

.filter-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.filter-group-label {
  font-size: 12px;
  font-weight: 600;
  color: #8b5cf6;
  margin: 4px 0 10px;
}

:deep(.all-filters-body .el-select),
:deep(.all-filters-body .el-input) {
  width: 100%;
}

.filter-actions {
  margin-top: 4px;
  display: flex;
  justify-content: flex-end;
}

/* ── Table Toolbar ── */
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(180deg, rgba(245, 247, 251, 0.8) 0%, rgba(241, 245, 252, 0.9) 100%);
}

.entry-count {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.toolbar-right {
  display: flex;
  gap: 8px;
  align-items: center;
}

.column-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.column-selector-title {
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--text-primary);
}

/* ── Expand / Child Impacts ── */
.child-impacts {
  padding: 16px 24px;
}

.child-impacts-title {
  font-weight: 600;
  margin: 0 0 8px;
  color: var(--text-primary);
}

:deep(.row-approved) td {
  background-color: #f0fdf4 !important;
}
:deep(.row-dismissed) td {
  background-color: #f3f4f6 !important;
}
:deep(.row-forecast) td {
  background-color: #eff6ff !important;
}
:deep(.no-expand .el-table__expand-icon) {
  visibility: hidden;
  pointer-events: none;
}


/* ── Action Buttons ── */
.action-btns {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.action-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  color: #6b7280;
  transition: background 0.15s, color 0.15s;
  padding: 0;
}

.action-icon svg {
  width: 15px;
  height: 15px;
}

.action-icon:hover {
  background: #f3f4f6;
  color: #111827;
}

.action-icon--danger {
  color: #d4183d;
}

.action-icon--danger:hover {
  background: #fff1f3;
  color: #d4183d;
}

/* ── Table header: never truncate ── */
:deep(.el-table th .cell) {
  white-space: nowrap;
  overflow: visible;
  text-overflow: clip;
}

/* ── Table horizontal scrollbar ── */
:deep(.el-table__body-wrapper .el-scrollbar__bar.is-horizontal) {
  height: 8px;
  bottom: 0;
  opacity: 1 !important;
}
:deep(.el-table__body-wrapper .el-scrollbar__thumb) {
  background-color: rgba(0, 0, 0, 0.22);
  border-radius: 4px;
  transition: background-color 0.2s;
}
:deep(.el-table__body-wrapper .el-scrollbar__thumb:hover) {
  background-color: rgba(0, 0, 0, 0.42);
}
:deep(.el-table__body-wrapper .el-scrollbar__wrap) {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* ── Probability Badge ── */
.prob-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: default;
}
.prob-high    { background: #0d9488; color: #fff; }
.prob-medium  { background: #cffafe; color: #0e7490; }
.prob-low     { background: #e0f2fe; color: #0369a1; }

/* ── Split Group ── */
.split-group {
  margin-bottom: 24px;
}

.split-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  background: #f8f9fc;
  border-left: 3px solid #030213;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.split-group-breadcrumb {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}

.split-sep {
  color: #9ca3af;
  font-size: 13px;
  padding: 0 2px;
  line-height: 1;
}

.split-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 3px 9px;
  font-size: 12px;
}

.split-chip-label {
  color: #9ca3af;
  font-weight: 500;
}

.split-chip-val {
  color: #111827;
  font-weight: 600;
}

.split-count {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: #030213;
  border-radius: 20px;
  padding: 2px 12px;
  white-space: nowrap;
  flex-shrink: 0;
}
</style>
