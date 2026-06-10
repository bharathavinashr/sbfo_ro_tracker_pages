<template>
  <div
    class="main-page-wrapper"
     
  >
    <header class="logo-header">
      <img :src="logoUrl" alt="Suntory Oceania" class="header-logo" />
    </header>
    <div class="page-container">
    <div class="page-header">
      <el-button :icon="ArrowLeft" @click="router.push('/')">Back to Main</el-button>
      <div>
        <h1 class="page-title">
          {{ showComparison ? 'Snapshot Comparison' : 'Browse Snapshots' }}
        </h1>
        <p class="page-subtitle">
          {{ showComparison
            ? ''
            : comparisonMode
              ? 'Select 2 snapshots to compare'
              : 'View and manage frozen snapshots of entry versions' }}
        </p>
      </div>
    </div>

    <template v-if="showComparison">
      <div class="comparison-meta">
        <div class="comparison-labels">
          <span><strong>Baseline:</strong> {{ earlierSnapshot?.name }} ({{ formatDate(earlierSnapshot?.created_at ?? '') }})</span>
          <span class="arrow">→</span>
          <span><strong>Comparison:</strong> {{ laterSnapshot?.name }} ({{ formatDate(laterSnapshot?.created_at ?? '') }})</span>
        </div>
        <!-- <el-button @click="clearComparison">
          <el-icon><Close /></el-icon>
          Close Comparison
        </el-button> -->
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
              <template v-for="(row, index) in comparedEntries" :key="row.id || index">
                <tr :class="getRowClass(row)">
                <td class="col-expand">
                  <button v-if="row.comparedChildren?.length" class="expand-btn" @click="toggleExpand(row.originalEntryId || row.id)">
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
                      <span v-for="field in row.modifiedFields" :key="field" class="field-badge">{{ field }}</span>
                    </div>
                  </template>
                  <span v-else-if="row.changeStatus === 'New' && row.changeStatus" class="text-green">New entry</span>
                  <span v-else-if="row.changeStatus === 'Deleted'" class="text-red">Deleted</span>
                  <span v-else class="cell-muted">-</span>
                </td>

                <td v-if="visibleColumns.ibpStep">
                  <div>{{ row.ibpStep || '-' }}</div>
                  <div v-if="row.changeStatus === 'Modified' && row.previousValues?.ibpStep && row.previousValues.ibpStep !== row.ibpStep" class="prev-value">{{ row.previousValues.ibpStep }}</div>
                </td>

                <td v-if="visibleColumns.division">
                  <div>{{ row.division }}</div>
                  <div v-if="row.changeStatus === 'Modified' && row.previousValues?.division && row.previousValues.division !== row.division" class="prev-value">{{ row.previousValues.division }}</div>
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
                  <div>{{ row.rAndO }}</div>
                  <div v-if="row.changeStatus === 'Modified' && row.previousValues?.rAndO && row.previousValues.rAndO !== row.rAndO" class="prev-value">{{ row.previousValues.rAndO }}</div>
                </td>

                <td v-if="visibleColumns.probability" class="tc">
                  <span v-if="row.probability" :class="['prob-badge', `prob-${(row.probability||'').toLowerCase()}`]">
                    {{ (row.probability||'').charAt(0).toUpperCase() }}
                  </span>
                  <span v-else class="cell-muted">-</span>
                  
                  <div v-if="row.changeStatus === 'Modified' && row.previousValues?.probability && row.previousValues.probability !== row.probability" class="prev-value tc" style="margin-top: 4px;">
                    <span :class="['prob-badge', `prob-${(row.previousValues.probability||'').toLowerCase()}`, 'dim']" style="transform: scale(0.8)">
                      {{ (row.previousValues.probability||'').charAt(0).toUpperCase() }}
                    </span>
                  </div>
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

                <td v-if="visibleColumns.status">
                  <div>{{ row.status || 'Open' }}</div>
                  <div v-if="row.changeStatus === 'Modified' && row.previousValues?.status && row.previousValues.status !== row.status" class="prev-value">{{ row.previousValues.status }}</div>
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

              <!-- Child Impact Rows for Comparison -->
              <template v-if="expandedRows.has(row.originalEntryId || row.id) && row.comparedChildren?.length">
                <tr v-for="(ci, cIdx) in row.comparedChildren" :key="`${row.id}-c${cIdx}`" :class="['child-row', getRowClass(ci)]">
                  <td class="col-expand"></td>
                  <td v-if="visibleColumns.changeStatus">
                    <span :class="['status-badge', changeStatusClass(ci.changeStatus), 'dim']">{{ ci.changeStatus }}</span>
                  </td>
                  <td v-if="visibleColumns.modifiedFields">
                    <div v-if="ci.changeStatus === 'Modified'" class="field-badges-wrap">
                      <span v-for="f in ci.modifiedFields" :key="f" class="field-badge">{{ f }}</span>
                    </div>
                    <span v-else-if="ci.changeStatus === 'New'" class="text-green dim">New period</span>
                    <span v-else-if="ci.changeStatus === 'Deleted'" class="text-red dim">Removed</span>
                    <span v-else class="cell-muted">-</span>
                  </td>
                  <td v-if="visibleColumns.ibpStep" class="cell-muted">{{ row.ibpStep || '-' }}</td>
                  <td v-if="visibleColumns.division" class="cell-muted">{{ row.division }}</td>
                  <td v-if="visibleColumns.country" class="cell-muted">{{ formatValue(row.country) }}</td>
                  <td v-if="visibleColumns.categorisation" class="cell-muted">{{ row.categorisation || '-' }}</td>
                  <td v-if="visibleColumns.description" class="cell-muted">{{ row.shortDescription || '-' }}</td>
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
    </template>

    <template v-else>
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

      <div v-else-if="snapshots.length >= 2" class="compare-btn-row">
        <el-button
          :icon="ScaleToOriginal"
          class="black-icon-btn"
          @click="enterComparisonMode"
        >
          Compare Snapshots
        </el-button>
        <el-button
          :icon="Search"
          class="black-icon-btn"
          @click="router.push('/snapshot-history')"
        >
          Browse Snapshot History
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
                      <div class="snapshot-title-group">
                        <span class="snapshot-name">{{ snapshot.name }}</span>
                        <div class="snapshot-meta-tags">
                          <el-tag v-if="snapshot.is_final" type="success" size="small" effect="dark" class="final-tag">Final</el-tag>
                          <el-tag v-if="snapshot.version !== undefined" size="small" class="version-tag">v{{ snapshot.version }}</el-tag>
                        </div>
                      </div>
                    </div>
                    <el-dropdown trigger="click" @command="handleToggleFinal(snapshot)">
                      <el-button link :icon="MoreFilled" />
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="toggle">
                            {{ snapshot.is_final ? 'Unmark as Final Version' : 'Mark as Final Version' }}
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </template>
                <div class="card-content">
                  <p class="snapshot-date">Created By: {{ snapshot.creator }}</p>
                  <p class="snapshot-date">Created: {{ formatDate(snapshot.created_at) }}</p>
                  <p class="snapshot-count">
                    <strong>{{ snapshot.entries_count }}</strong> {{ snapshot.entries_count === 1 ? 'entry' : 'entries' }} frozen
                  </p>
                  <div class="card-actions">
                    <el-button class="view-snapshot-btn" @click="handleViewSnapshot(snapshot.snapshot_id)">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { ArrowLeft, Calendar, Loading, Delete, Close, ScaleToOriginal, MoreFilled, Search } from "@element-plus/icons-vue";
import logoUrl from "@/assets/SuntoryOceania-Logo-RGB-Reversed.png";
import { snapshotApi } from "@/services/api";
import backgroundImage from "@/assets/SuntoryOceania-Patterns-RGB-Blue-Water_Ripples.png";

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
  creator?: string;
}


interface ChildImpact {
  id: number;
  impactYear: string; // 2023, 2024, etc.
  impactPeriod: string; // F01, F02, etc.
  nsvAud?: string;
  nsvNzd?: string;
  volumeLitres?: string;
  volumeCases?: string;
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

interface ComparedEntry extends Entry {
  changeStatus: ChangeStatus;
  modifiedFields?: string[];
  previousValues?: Record<string, any>;
  comparedChildren?: ComparedChildImpact[];
}

const router = useRouter();
const loading = ref(true);
const snapshots = ref<SnapshotGroup[]>([]);
const comparing = ref(false);
const comparisonMode = ref(false);
const selectedSnapshots = ref<string[]>([]);
const comparedEntries = ref<ComparedEntry[]>([]);
const showComparison = ref(false);

const expandedRows = ref<Set<string | number>>(new Set());
function toggleExpand(id: string | number) {
  const s = new Set(expandedRows.value);
  s.has(id) ? s.delete(id) : s.add(id);
  expandedRows.value = s;
}

const ibpSteps = ["All", "Portfolio Review", "Supply Review", "Demand Review", "A&P (Pre-Exec)", "Overheads (Pre-Exec)"];

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
  { key: 'status', label: 'Status' },
  { key: 'lastModified', label: 'Last Modified' },
  { key: 'financialImpactType', label: 'Financial Impact Type' },
  { key: 'currency', label: 'Financial Impact Currency' },
  { key: 'impact', label: 'Financial Impact Value' },
  // { key: 'volumeCases', label: 'Volume (Cases)' },
  { key: 'volumeImpactType', label: 'Volume Impact Type' },
  { key: 'volumeImpactValue', label: 'Volume Impact Value' },
  { key: 'impactPeriods', label: 'Impact Period(s)' },
];

const groupedSnapshots = computed(() => {
  const grouped: Record<string, SnapshotGroup[]> = {};
  ibpSteps.forEach(step => {
    grouped[step] = snapshots.value.filter(s => s.ibp_step === step).slice(0, 6);
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

async function handleToggleFinal(snapshot: SnapshotGroup) {
  try {
    const newVal = !snapshot.is_final;
    await snapshotApi.updateFinal(snapshot.snapshot_id, newVal);
    ElMessage.success(`Snapshot ${newVal ? 'marked as final' : 'unmarked as final'}`);
    await fetchSnapshots();
  } catch (error: any) {
    const detail = error?.response?.data?.detail;
    const message = Array.isArray(detail) 
      ? detail.map(d => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join(', ')
      : detail;
    
    ElMessage.error(message || error.message || "Failed to update snapshot status");
    console.error("Snapshot toggle error:", error);
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

function changeStatusClass(status: ChangeStatus) {
  switch (status) {
    case 'New': return 'status-success';
    case 'Modified': return 'status-primary';
    case 'Deleted': return 'status-danger';
    default: return 'status-info';
  }
}

function getRowClass(row: ComparedEntry | ComparedChildImpact) {
  if (row.changeStatus === 'New') return 'row-new';
  if (row.changeStatus === 'Modified') return 'row-modified';
  if (row.changeStatus === 'Deleted') return 'row-deleted';
  return '';
}

// ── Helpers ──────────────────────────────────────────────────────────────────

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

function compareEntries(baseEntry: Entry, compEntry: Entry): { modifiedFields: string[]; previousValues: Record<string, any>; comparedChildren: ComparedChildImpact[] } {
  const modifiedFields: string[] = [];
  const previousValues: Record<string, any> = {};
  const comparedChildren: ComparedChildImpact[] = [];

  const bci = baseEntry.childImpacts || [];
  const cci = compEntry.childImpacts || [];

  const fieldDisplayNames: Partial<Record<keyof Entry, string>> = {
    division: "Division", ibpStep: "IBP Step", country: "Country",
    channel: "Channel", subChannel: "Sub Channel", account: "Account",
    brand: "Brand", brandFamily: "Brand Family", rAndO: "Risk vs. Opp.",
    probability: "Probability", categorisation: "Categorisation",
    impact: "Financial Impact Value", impactPeriod: "Impact Period",
    impactYear: "Impact Year", status: "Status",
    shortDescription: "Short Description", description: "Description",
    owner: "Owner", addToForecastByPeriod: "Add to Forecast By",
    addToForecastByYear: "Add to Forecast By", financialImpactType: "Financial Impact Type",
    impactCurrency: "Financial Impact Currency",
    volumeCases: "Volume (Cases)",
    volumeImpactType: "Volume Impact Type",
    volumeImpactValue: "Volume Impact Value",
  };

  for (const fieldKey of Object.keys(fieldDisplayNames)) {
    const field = fieldKey as keyof Entry;
    const bv = baseEntry[field];
    const cv = compEntry[field];

    const isComplex = ['country', 'channel', 'subChannel', 'account', 'brand', 'brandFamily'].includes(field);
    const isDiff = isComplex 
      ? formatValue(bv) !== formatValue(cv)
      : (Array.isArray(bv) && Array.isArray(cv))
        ? JSON.stringify([...(bv as any[])].sort()) !== JSON.stringify([...((cv as any[]) || [])].sort())
        : bv !== cv;

    if (isDiff) {
      // Skip parent timing fields if children exist, as they are redundant with "Impact Periods" badge
      if ((field === 'impactPeriod' || field === 'impactYear') && (bci.length > 0 || cci.length > 0)) {
        continue;
      }

      const label = fieldDisplayNames[field] as string;
      if (!modifiedFields.includes(label)) {
        modifiedFields.push(label);
      }
      previousValues[field] = bv;
    }
  }

  const baseChildMap = new Map<string, ChildImpact>();
  bci.forEach(c => baseChildMap.set(`${c.impactPeriod}-${c.impactYear}`, c));
  const compChildMap = new Map<string, ChildImpact>();
  cci.forEach(c => compChildMap.set(`${c.impactPeriod}-${c.impactYear}`, c));

  const childModifiedLabels = new Set<string>();

  // Check for New or Modified children
  cci.forEach(compChild => {
    const key = `${compChild.impactPeriod}-${compChild.impactYear}`;
    const baseChild = baseChildMap.get(key);

    if (!baseChild) {
      // New child impact
      comparedChildren.push({ ...compChild, changeStatus: 'New' });
      childModifiedLabels.add("Impact Periods");
    } else {
      const childModified: string[] = [];
      const childPrev: Record<string, any> = {};

      // Compare financial impact
      if (baseChild.impact !== compChild.impact) {
        const label = 'Financial Impact Value';
        childModified.push(label);
        childPrev.impact = baseChild.impact;
        childModifiedLabels.add(label);
      }
      // Compare volume impact
      if (baseChild.volumeImpactValue !== compChild.volumeImpactValue) {
        const label = 'Volume Impact Value';
        childModified.push(label);
        childPrev.volumeImpactValue = baseChild.volumeImpactValue;
        childModifiedLabels.add(label);
      }

      comparedChildren.push({
        ...compChild,
        changeStatus: childModified.length > 0 ? 'Modified' : 'Unchanged', // Mark as modified if any field changed
        modifiedFields: childModified,
        previousValues: childPrev
      });
    }
  });

  // Check for Deleted children (present in base but not in comp)
  bci.forEach(baseChild => {
    const key = `${baseChild.impactPeriod}-${baseChild.impactYear}`;
    if (!compChildMap.has(key)) {
      comparedChildren.push({ ...baseChild, changeStatus: 'Deleted' });
      childModifiedLabels.add("Impact Periods");
    }
  });

  // Merge child-level modified fields into parent's modifiedFields
  childModifiedLabels.forEach(label => {
    if (!modifiedFields.includes(label)) {
      modifiedFields.push(label);
    }
  });

  return { modifiedFields, previousValues, comparedChildren };
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
    baselineEntries.forEach(e => baselineMap.set(String(e.originalEntryId || e.id), e));

    const comparisonMap = new Map<string, Entry>();
    comparisonEntries.forEach(e => comparisonMap.set(String(e.originalEntryId || e.id), e));

    const compared: ComparedEntry[] = [];

    comparisonEntries.forEach(compEntry => {
      const key = String(compEntry.originalEntryId || compEntry.id);
      const baseEntry = baselineMap.get(key);
      if (!baseEntry) {
        compared.push({ 
          ...compEntry, 
          changeStatus: 'New', // Parent is new
          comparedChildren: (compEntry.childImpacts || []).map(c => ({ ...c, changeStatus: 'New' }))
        });
      } else {
        const { modifiedFields, previousValues, comparedChildren } = compareEntries(baseEntry, compEntry);
        
        let changeStatus: ChangeStatus = modifiedFields.length > 0 ? 'Modified' : 'Unchanged';
        
        compared.push({
          ...compEntry,
          changeStatus,
          modifiedFields,
          previousValues,
          comparedChildren
        });
      }
    });

    baselineEntries.forEach(baseEntry => {
      const key = String(baseEntry.originalEntryId || baseEntry.id);
      if (!comparisonMap.has(key)) {
        compared.push({ 
          ...baseEntry, 
          changeStatus: 'Deleted', // Parent is deleted
          comparedChildren: (baseEntry.childImpacts || []).map(c => ({ ...c, changeStatus: 'Deleted' }))
        });
      }
    });

    expandedRows.value = new Set();
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
.main-page-wrapper {
  min-height: 100vh;
  background-size: cover;
  background-attachment: fixed;
  background-repeat: repeat;
  background-position: center;
}

.page-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 24px;
  /* background-color: #D9F2F2; */
}

.logo-header {
  max-width: 1800px;
  margin: 0 auto;
  padding: 16px 24px;
  background: #00325D;
}

.page-header {
  /* display: flex; */
  /* flex-direction: column; */
  gap: 16px;
  margin-bottom: 24px;
}

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
}

.header-logo {
  height: 40px;
  width: auto;
}

/* Compare button row */
.compare-btn-row {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
  gap: 12px;
  color: #000 !important;
}

.compare-btn-row :deep(.el-button) {
  width: 200px;
  color: #000;
  border-color: var(--border-color);
}

/* Ensures the icon specifically is rendered as black */
.black-icon-btn :deep(.el-icon) {
  color: #000 !important;
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

/* ── Comparison Table Wrapper Treatment ───────────────────────────────── */
.comparison-table-wrapper {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #ddd;
  overflow: visible;
  box-shadow: none;
}

.comparison-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  background: linear-gradient(180deg, rgba(245,247,251,.8) 0%, rgba(241,245,252,.9) 100%);
  border-radius: 10px 10px 0 0;
}

.comparison-summary-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* ── Table scroll wrapper ─────────────────────────────── */
.table-scroll-wrap {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  border-radius: 0 0 10px 10px;
}
.table-scroll-wrap::-webkit-scrollbar { height: 8px; }
.table-scroll-wrap::-webkit-scrollbar-track { background: transparent; }
.table-scroll-wrap::-webkit-scrollbar-thumb { background: rgba(0,0,0,.22); border-radius: 4px; }
.table-scroll-wrap::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,.42); }

/* ── Custom HTML Data Table ───────────────────────────────────────── */
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
.data-table td {
  padding: 8px 12px; 
  border-bottom: 1px solid #f0f2f5;
  vertical-align: middle; 
  white-space: nowrap;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover td { background: #f9fafb; }

/* Dynamic change grid colors */
.row-new td { background-color: #f0fdf4 !important; }
.row-modified td { background-color: #eff6ff !important; }
.row-deleted td { background-color: #fff1f2 !important; opacity: 0.7; }

/* Child rows expansion */
.col-expand { width: 36px; }
.expand-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border: none; background: transparent;
  border-radius: 4px; cursor: pointer; color: #6b7280; padding: 0;
}
.expand-btn:hover { background: #f3f4f6; }
.expand-icon { width: 14px; height: 14px; transition: transform 0.2s; }
.expand-icon.rotated { transform: rotate(90deg); }
.child-row td { background: #fafafa; padding-left: 12px; }
.child-row:hover td { background: #f3f4f6 !important; }
.child-row.row-new td { background-color: #f0fdf4 !important; opacity: 0.8; }
.child-row.row-deleted td { background-color: #fff1f2 !important; opacity: 0.6; }

/* Column width dimensions */
.col-sm { min-width: 80px; }
.col-md { min-width: 120px; }
.col-lg { min-width: 150px; }
.col-xl { min-width: 200px; max-width: 240px; }

.truncate-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Core alignment styles */
.tc { text-align: center; }
.tr { text-align: left; }
.fw { font-weight: 600; }

/* Utility layout blocks */
.cell-muted { color: #9ca3af; }
.cell-sub { font-size: 11px; color: #9ca3af; }
.italic { font-style: italic; }

/* Modified values notation */
.prev-value {
  font-size: 11px;
  color: #9ca3af;
  text-decoration: line-through;
  margin-top: 2px;
}

/* Priority status markers */
.prob-badge {
  display: inline-flex; 
  align-items: center; 
  justify-content: center;
  width: 28px; 
  height: 28px; 
  border-radius: 6px;
  font-size: 12px; 
  font-weight: 700; 
  cursor: default;
}
.prob-high   { background: #0d9488; color: #fff; }
.prob-medium { background: #cffafe; color: #0e7490; }
.prob-low    { background: #e0f2fe; color: #0369a1; }
.dim { opacity: .5; }

/* Column modifier tag fields */
.field-badges-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.field-badge {
  background: #f1f5f9;
  color: #475569;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
}

/* Status evaluation badges */
.status-badge {
  display: inline-block; 
  padding: 2px 8px; 
  border-radius: 4px;
  font-size: 12px; 
  font-weight: 500;
}
.status-success { background: #dcfce7; color: #166534; }
.status-primary { background: #dbeafe; color: #1e40af; }
.status-danger  { background: #fee2e2; color: #991b1b; }
.status-info    { background: #f3f4f6; color: #374151; }

/* ── Custom Popover Override Container ───────────────────────────────── */
:deep(.column-popover) {
  padding: 12px 0 12px 12px !important;
}

.column-selector-container { 
  display: flex; 
  flex-direction: column; 
}
.column-selector-title {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  margin: 0 0 12px 0;
  padding-right: 12px;
}
.column-selector-list {
  display: flex;
  flex-direction: column;
  max-height: 250px;
  overflow-y: auto;
  padding-right: 8px;
}
.column-selector-list :deep(.el-checkbox) {
  margin-right: 0;
  margin-bottom: 8px;
  font-weight: normal;
}
.column-selector-list :deep(.el-checkbox:last-child) {
  margin-bottom: 0;
}
.column-selector-list::-webkit-scrollbar {
  width: 6px;
}
.column-selector-list::-webkit-scrollbar-track {
  background: transparent;
}
.column-selector-list::-webkit-scrollbar-thumb {
  background-color: #909399;
  border-radius: 10px;
}

/* ── Snapshot Grid View ───────────────────────────────────────────────── */
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
  font-family: 'Jost', Arial, sans-serif;
  font-size: 24px;
  font-weight: 500;
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

.snapshot-title-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.snapshot-meta-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.version-tag {
  background-color: #e0e0e0;
  color: #333;
}

.el-dropdown-link {
  cursor: pointer;
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

.snapshot-creator {
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

.view-snapshot-btn {
  flex: 1;
  background-color: #000 !important;
  border-color: #000 !important;
  color: #fff !important;
}

.view-snapshot-btn:hover,
.view-snapshot-btn:focus {
  background-color: #333 !important;
  border-color: #333 !important;
  color: #fff !important;
}

/* Utility layout extensions */
.text-green  { color: #16a34a; font-size: 13px; }
.text-red    { color: #dc2626; font-size: 13px; }
</style>