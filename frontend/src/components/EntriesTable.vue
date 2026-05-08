<template>
  <div class="entries-table-wrapper">

    <div class="quick-filters-section">
      <p class="section-label" style="font-size:16px; font-weight:700; margin-bottom:6px">Database Entries</p>
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

    <div class="all-filters-section">
      <div class="all-filters-header" @click="allFiltersOpen = !allFiltersOpen">
        <span class="all-filters-title">All Filters</span>
        <svg :class="['chevron-icon', { open: allFiltersOpen }]"
          viewBox="0 0 24 24" fill="none" stroke="currentColor"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </div>

      <div v-show="allFiltersOpen" class="all-filters-body">
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

        <el-row :gutter="16" class="filter-row">
          <el-col :span="6">
            <label class="filter-label">Owner</label>
            <el-input v-model="store.filters.owner" placeholder="Filter owner..." clearable @change="store.fetchEntries()" />
          </el-col>
          <el-col :span="6">
            <label class="filter-label">Department</label>
            <el-select v-model="store.filters.department" clearable placeholder="All" @change="store.fetchEntries()">
              <el-option v-for="d in departmentOptions" :key="d" :value="d" :label="d" />
            </el-select>
          </el-col>
        </el-row>

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

    <div class="table-toolbar">
      <span class="entry-count">All Entries ({{ filteredEntries.length }})</span>

      <div class="toolbar-right">

        <div class="split-view-control">
          <span class="split-view-label">Split view by:</span>
          <div class="group-by-wrap" v-click-outside="closeGroupBy">
            <button class="group-by-trigger" @click.stop="groupByOpen = !groupByOpen">
              <span :class="splitBy.length ? 'has-value' : 'placeholder'">
                {{ splitBy.length ? `${splitBy.length} selected` : 'No grouping' }}
              </span>
              <svg class="chevron-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </button>
            <div v-if="groupByOpen" class="group-by-dropdown" @click.stop>
              <label class="gbd-item gbd-all">
                <el-checkbox
                  :model-value="splitBy.length === splitByOptions.length"
                  :indeterminate="splitBy.length > 0 && splitBy.length < splitByOptions.length"
                  @change="toggleAllSplitBy"
                />
                <span class="gbd-label-bold">Select All</span>
              </label>
              <div class="gbd-divider" />
              <label v-for="opt in splitByOptions" :key="opt.key" class="gbd-item">
                <el-checkbox
                  :model-value="splitBy.includes(opt.key)"
                  @change="toggleSplitBy(opt.key)"
                />
                <span>{{ opt.label }}</span>
              </label>
            </div>
          </div>
        </div>

        <el-popover placement="bottom-end" :width="240" trigger="click" popper-class="column-popover">
          <template #reference>
            <el-button size="small" plain style="color: black;">
              <svg style="width:14px;height:14px;margin-right:4px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="18"/><rect x="14" y="3" width="7" height="18"/></svg>
              Columns
            </el-button>
          </template>
          <div class="column-selector-container">
            <p class="column-selector-title">Toggle Columns</p>
            <div class="column-selector-list">
              <el-checkbox v-model="colVisible.department">Department</el-checkbox>
              <el-checkbox v-model="colVisible.division">Division</el-checkbox>
              <el-checkbox v-model="colVisible.country">Country</el-checkbox>
              <el-checkbox v-model="colVisible.customer">Customer(s)</el-checkbox>
              <el-checkbox v-model="colVisible.product">Product</el-checkbox>
              <el-checkbox v-model="colVisible.rAndO">Risk vs. Opp.</el-checkbox>
              <el-checkbox v-model="colVisible.probability">Probability</el-checkbox>
              <el-checkbox v-model="colVisible.addToForecastBy">Add to Forecast By</el-checkbox>
              <el-checkbox v-model="colVisible.categorisation">Categorisation</el-checkbox>
              <el-checkbox v-model="colVisible.description">Short Description</el-checkbox>
              <el-checkbox v-model="colVisible.impactType">Impact Type</el-checkbox>
              <el-checkbox v-model="colVisible.currency">Currency</el-checkbox>
              <el-checkbox v-model="colVisible.impact">Impact</el-checkbox>
              <el-checkbox v-model="colVisible.volumeCases">Volume (Cases)</el-checkbox>
              <el-checkbox v-model="colVisible.impactPeriods">Impact Period(s)</el-checkbox>
              <el-checkbox v-model="colVisible.subChannel">Sub-Channel</el-checkbox>
              <el-checkbox v-model="colVisible.account">Account</el-checkbox>
              <el-checkbox v-model="colVisible.brandFamily">Brand Family</el-checkbox>
              <el-checkbox v-model="colVisible.creator">Creator</el-checkbox>
              <el-checkbox v-model="colVisible.owner">Owner</el-checkbox>
              <el-checkbox v-model="colVisible.status">Status</el-checkbox>
              <el-checkbox v-model="colVisible.lastModified">Last Modified</el-checkbox>
            </div>
          </div>
        </el-popover>

        <div class="phased-view-control" v-click-outside="closePhasedMenu">
          <button
            class="phased-view-trigger"
            :class="{ 'phased-view-active': phasedImpactViews.length > 0 }"
            @click.stop="phasedMenuOpen = !phasedMenuOpen">
            <svg style="width:14px;height:14px;margin-right:4px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            <span class="phased-view-text">
              {{ phasedImpactViews.length === 0 ? 'View Phased Impact' : `${phasedImpactViews.length} selected` }}
            </span>
            <svg class="chevron-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>
          <div v-if="phasedMenuOpen" class="phased-view-dropdown" @click.stop>
            <label class="gbd-item gbd-all">
              <el-checkbox
                :model-value="phasedImpactViews.length === phasedViewOptions.length"
                :indeterminate="phasedImpactViews.length > 0 && phasedImpactViews.length < phasedViewOptions.length"
                @change="toggleAllPhasedViews"
              />
              <span class="gbd-label-bold">Select All</span>
            </label>
            <div class="gbd-divider" />
            <label v-for="opt in phasedViewOptions" :key="opt.key" class="gbd-item">
              <el-checkbox
                :model-value="phasedImpactViews.includes(opt.key)"
                @change="togglePhasedView(opt.key)"
              />
              <span>{{ opt.label }}</span>
            </label>
          </div>
        </div>

        <el-button v-if="!isReadOnly" size="small" plain @click="$emit('add')" style="color: black;">
          <svg style="width:14px;height:14px;margin-right:4px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          Add New Entry
        </el-button>

        <el-button v-if="!isReadOnly" size="small" plain @click="exportToCSV(filteredEntries)" style="color: black;">
          <svg style="width:14px;height:14px;margin-right:4px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Export CSV
        </el-button>
      </div>
    </div>

    <template v-if="splitBy.length">
      <div v-for="group in groupedEntries" :key="group.key" class="split-group">
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
          <div class="split-group-actions">
            <span class="split-count">{{ group.entries.length }} {{ group.entries.length === 1 ? 'entry' : 'entries' }}</span>
            <el-button size="small" plain @click="exportToCSV(group.entries, `${group.key}.csv`)">
              <svg style="width:12px;height:12px;margin-right:3px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Export CSV
            </el-button>
          </div>
        </div>
        <div class="table-scroll-wrap">
          <table class="data-table">
            <thead><tr>
              <th class="col-expand"></th>
              <th v-if="colVisible.department"     class="col-md">Department</th>
              <th v-if="colVisible.division"       class="col-sm">Division</th>
              <th v-if="colVisible.country"        class="col-sm">Country</th>
              <th v-if="colVisible.categorisation" class="col-lg">Categorisation</th>
              <th v-if="colVisible.description"    class="col-xl">Short Description</th>
              <th v-if="colVisible.customer"       class="col-lg">Customer(s)</th>
              <th v-if="colVisible.product"        class="col-lg">Product</th>
              <th v-if="colVisible.rAndO"          class="col-md">Risk vs. Opp.</th>
              <th v-if="colVisible.probability"    class="col-sm tc">Probability</th>
              <th v-if="colVisible.addToForecastBy" class="col-md">Add to Forecast By</th>
              <th v-if="colVisible.creator"        class="col-md">Creator</th>
              <th v-if="colVisible.owner"          class="col-md">Owner</th>
              <th v-if="colVisible.status"         class="col-md">Status</th>
              <th v-if="colVisible.lastModified"   class="col-lg">Last Modified</th>
              <th v-if="colVisible.impactType"     class="col-md">Impact Type</th>
              <th v-if="colVisible.currency"       class="col-sm">Currency</th>
              <th v-if="colVisible.impact"         class="col-md tr">Impact</th>
              <th v-if="colVisible.volumeCases"    class="col-md tr">Volume (Cases)</th>
              <template v-if="phasedImpactViews.length > 0">
                <th v-for="col in phasedColumns" :key="col.label" class="col-phased tc">{{ col.label }}</th>
              </template>
              <th v-else-if="colVisible.impactPeriods" class="col-lg">Impact Period(s)</th>
              <th class="col-actions tc">Actions</th>
            </tr></thead>
            <tbody>
              <template v-for="row in group.entries" :key="row.id">
                <tr :class="rowClass(row)">
                  <td class="col-expand">
                    <button v-if="row.childImpacts?.length" class="expand-btn" @click="toggleExpand(row.id)">
                      <svg :class="['expand-icon', { rotated: expandedRows.has(row.id) }]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                    </button>
                  </td>
                  <td v-if="colVisible.department">{{ row.department || '-' }}</td>
                  <td v-if="colVisible.division">{{ row.division }}</td>
                  <td v-if="colVisible.country">{{ formatCountry(row.country) }}</td>
                  <td v-if="colVisible.categorisation">{{ row.categorisation }}</td>
                  <td v-if="colVisible.description">{{ row.shortDescription || row.description || '-' }}</td>
                  <td v-if="colVisible.customer">
                    <div v-if="row.account">{{ row.account }}</div>
                    <div v-if="row.subChannel" class="cell-sub">{{ row.subChannel }}</div>
                    <div v-if="row.channel"    class="cell-sub italic">{{ row.channel }}</div>
                    <span v-if="!row.account && !row.subChannel && !row.channel">-</span>
                  </td>
                  <td v-if="colVisible.product">
                    <div v-if="row.brand">{{ row.brand }}</div>
                    <div v-if="row.brandFamily" class="cell-sub italic">{{ formatBrandFamily(row.brandFamily) }}</div>
                    <span v-if="!row.brand && !row.brandFamily">-</span>
                  </td>
                  <td v-if="colVisible.rAndO">{{ row.rAndO }}</td>
                  <td v-if="colVisible.probability" class="tc">
                    <span :class="['prob-badge', `prob-${(row.probability||'').toLowerCase()}`]">
                      {{ (row.probability||'').charAt(0).toUpperCase() }}
                    </span>
                  </td>
                  <td v-if="colVisible.addToForecastBy">
                    {{ row.addToForecastByPeriod && row.addToForecastByYear
                        ? `${row.addToForecastByPeriod} ${row.addToForecastByYear}`
                        : (row.impactPeriod && row.impactYear ? `${row.impactPeriod} ${row.impactYear}` : '-') }}
                  </td>
                  <td v-if="colVisible.creator">{{ row.creator || '-' }}</td>
                  <td v-if="colVisible.owner">{{ row.owner }}</td>
                  <td v-if="colVisible.status">
                    <el-select v-if="canEditStatusRow(row)" :model-value="row.status" size="small" style="width:100%" @change="(v:string) => handleStatusChange(row, v)">
                      <el-option v-for="s in allowedStatusRow(row)" :key="s" :value="s" :label="s" />
                    </el-select>
                    <span v-else :class="['status-badge', statusClass(row.status)]">{{ row.status }}</span>
                  </td>
                  <td v-if="colVisible.lastModified" class="cell-muted">{{ formatDate(row.lastModified) }}</td>
                  <td v-if="colVisible.impactType">{{ row.impactType || '-' }}</td>
                  <td v-if="colVisible.currency">{{ row.impactCurrency || '-' }}</td>
                  <td v-if="colVisible.impact" class="tr fw">{{ row.impact ? Number(row.impact).toLocaleString() : '-' }}</td>
                  <td v-if="colVisible.volumeCases" class="tr">{{ row.volumeImpact ? Number(row.volumeImpact).toLocaleString() : '-' }}</td>
                  <template v-if="phasedImpactViews.length > 0">
                    <td v-for="col in phasedColumns" :key="col.label" class="tc phased-cell">
                      {{ formatPhasedCell(getAggregatedImpact(row, col)) }}
                    </td>
                  </template>
                  <td v-else-if="colVisible.impactPeriods">{{ formatImpactPeriods(row.childImpacts, row.impactPeriod, row.impactYear) }}</td>
                  <td class="tc">
                    <div class="action-btns">
                      <button class="action-icon" @click="$emit('history', row)" title="History">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                      </button>
                      <button v-if="!isReadOnly && store.canCreate" class="action-icon" @click="$emit('duplicate', row)" title="Duplicate">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                      </button>
                      <button v-if="!isReadOnly && canEditRow(row)" class="action-icon" @click="handleEditClick(row)" title="Edit">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                      </button>
                      <el-popconfirm v-if="!isReadOnly && canDeleteRow(row)" title="Delete all versions of this entry?" confirm-button-type="danger" @confirm="$emit('delete', row)">
                        <template #reference>
                          <button class="action-icon action-icon--danger" title="Delete">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                          </button>
                        </template>
                      </el-popconfirm>
                    </div>
                  </td>
                </tr>
                <template v-if="expandedRows.has(row.id) && row.childImpacts?.length">
                  <tr v-for="(ci, cIdx) in row.childImpacts" :key="`${row.id}-c${cIdx}`" class="child-row">
                    <td class="col-expand"></td>
                    <td v-if="colVisible.department"     class="cell-muted">{{ row.department || '-' }}</td>
                    <td v-if="colVisible.division"       class="cell-muted">{{ row.division }}</td>
                    <td v-if="colVisible.country"        class="cell-muted">{{ formatCountry(row.country) }}</td>
                    <td v-if="colVisible.categorisation" class="cell-muted">{{ row.categorisation }}</td>
                    <td v-if="colVisible.description"    class="cell-muted">{{ row.shortDescription || '-' }}</td>
                    <td v-if="colVisible.customer"       class="cell-muted">
                      <div v-if="row.account">{{ row.account }}</div>
                      <div v-if="row.subChannel" class="cell-sub">{{ row.subChannel }}</div>
                    </td>
                    <td v-if="colVisible.product"        class="cell-muted">
                      <div v-if="row.brand">{{ row.brand }}</div>
                    </td>
                    <td v-if="colVisible.rAndO"          class="cell-muted">{{ row.rAndO }}</td>
                    <td v-if="colVisible.probability"    class="tc cell-muted">
                      <span :class="['prob-badge', `prob-${(row.probability||'').toLowerCase()}`, 'dim']">{{ (row.probability||'').charAt(0).toUpperCase() }}</span>
                    </td>
                    <td v-if="colVisible.addToForecastBy" class="cell-muted">-</td>
                    <td v-if="colVisible.creator"        class="cell-muted">{{ row.creator || '-' }}</td>
                    <td v-if="colVisible.owner"          class="cell-muted">{{ row.owner }}</td>
                    <td v-if="colVisible.status"         class="cell-muted">
                      <span :class="['status-badge', statusClass(row.status), 'dim']">{{ row.status }}</span>
                    </td>
                    <td v-if="colVisible.lastModified"   class="cell-muted">{{ formatDate(row.lastModified) }}</td>
                    <td v-if="colVisible.impactType"     class="cell-muted">{{ row.impactType || '-' }}</td>
                    <td v-if="colVisible.currency"       class="cell-muted">{{ row.impactCurrency || '-' }}</td>
                    <td v-if="colVisible.impact"         class="tr fw cell-muted">{{ ci.impact ? Number(ci.impact).toLocaleString() : '-' }}</td>
                    <td v-if="colVisible.volumeCases"    class="tr cell-muted">{{ ci.volumeImpact ? Number(ci.volumeImpact).toLocaleString() : '-' }}</td>
                    <template v-if="phasedImpactViews.length > 0">
                      <td v-for="col in phasedColumns" :key="col.label" class="tc cell-muted phased-cell">
                        {{ formatPhasedCellChild(ci, col) }}
                      </td>
                    </template>
                    <td v-else-if="colVisible.impactPeriods" class="cell-muted">
                      {{ ci.impactPeriod && ci.impactYear ? `${periodToMonthAbbr(ci.impactPeriod)} ${ci.impactYear}` : '-' }}
                    </td>
                    <td class="cell-muted tc">-</td>
                  </tr>
                </template>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </template>

    <div v-else class="table-scroll-wrap" v-loading="isReadOnly ? false : store.loading">
      <table class="data-table">
        <thead><tr>
          <th class="col-expand"></th>
          <th v-if="colVisible.department"     class="col-md">Department</th>
          <th v-if="colVisible.division"       class="col-sm">Division</th>
          <th v-if="colVisible.country"        class="col-sm">Country</th>
          <th v-if="colVisible.categorisation" class="col-lg">Categorisation</th>
          <th v-if="colVisible.description"    class="col-xl">Short Description</th>
          <th v-if="colVisible.customer"       class="col-lg">Customer(s)</th>
          <th v-if="colVisible.product"        class="col-lg">Product</th>
          <th v-if="colVisible.rAndO"          class="col-md">Risk vs. Opp.</th>
          <th v-if="colVisible.probability"    class="col-sm tc">Probability</th>
          <th v-if="colVisible.addToForecastBy" class="col-md">Add to Forecast By</th>
          <th v-if="colVisible.creator"        class="col-md">Creator</th>
          <th v-if="colVisible.owner"          class="col-md">Owner</th>
          <th v-if="colVisible.status"         class="col-md">Status</th>
          <th v-if="colVisible.lastModified"   class="col-lg">Last Modified</th>
          <th v-if="colVisible.impactType"     class="col-md">Impact Type</th>
          <th v-if="colVisible.currency"       class="col-sm">Currency</th>
          <th v-if="colVisible.impact"         class="col-md tr">Impact</th>
          <th v-if="colVisible.volumeCases"    class="col-md tr">Volume (Cases)</th>
          <template v-if="phasedImpactViews.length > 0">
            <th v-for="col in phasedColumns" :key="col.label" class="col-phased tc">{{ col.label }}</th>
          </template>
          <th v-else-if="colVisible.impactPeriods" class="col-lg">Impact Period(s)</th>
          <th class="col-actions tc">Actions</th>
        </tr></thead>
        <tbody>
          <template v-if="filteredEntries.length === 0">
            <tr><td :colspan="100" class="tc cell-muted" style="padding:24px">No entries found</td></tr>
          </template>
          <template v-for="row in filteredEntries" :key="row.id">
            <tr :class="rowClass(row)">
              <td class="col-expand">
                <button v-if="row.childImpacts?.length" class="expand-btn" @click="toggleExpand(row.id)">
                  <svg :class="['expand-icon', { rotated: expandedRows.has(row.id) }]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
                </button>
              </td>
              <td v-if="colVisible.department">{{ row.department || '-' }}</td>
              <td v-if="colVisible.division">{{ row.division }}</td>
              <td v-if="colVisible.country">{{ formatCountry(row.country) }}</td>
              <td v-if="colVisible.categorisation">{{ row.categorisation }}</td>
              <td v-if="colVisible.description">{{ row.shortDescription || row.description || '-' }}</td>
              <td v-if="colVisible.customer">
                <div v-if="row.account">{{ row.account }}</div>
                <div v-if="row.subChannel" class="cell-sub">{{ row.subChannel }}</div>
                <div v-if="row.channel"    class="cell-sub italic">{{ row.channel }}</div>
                <span v-if="!row.account && !row.subChannel && !row.channel">-</span>
              </td>
              <td v-if="colVisible.product">
                <div v-if="row.brand">{{ row.brand }}</div>
                <div v-if="row.brandFamily" class="cell-sub italic">{{ formatBrandFamily(row.brandFamily) }}</div>
                <span v-if="!row.brand && !row.brandFamily">-</span>
              </td>
              <td v-if="colVisible.rAndO">{{ row.rAndO }}</td>
              <td v-if="colVisible.probability" class="tc">
                <span :class="['prob-badge', `prob-${(row.probability||'').toLowerCase()}`]">
                  {{ (row.probability||'').charAt(0).toUpperCase() }}
                </span>
              </td>
              <td v-if="colVisible.addToForecastBy">
                {{ row.addToForecastByPeriod && row.addToForecastByYear
                    ? `${row.addToForecastByPeriod} ${row.addToForecastByYear}`
                    : (row.impactPeriod && row.impactYear ? `${row.impactPeriod} ${row.impactYear}` : '-') }}
              </td>
              <td v-if="colVisible.creator">{{ row.creator || '-' }}</td>
              <td v-if="colVisible.owner">{{ row.owner }}</td>
              <td v-if="colVisible.status">
                <el-select v-if="canEditStatusRow(row)" :model-value="row.status" size="small" style="width:100%" @change="(v:string) => handleStatusChange(row, v)">
                  <el-option v-for="s in allowedStatusRow(row)" :key="s" :value="s" :label="s" />
                </el-select>
                <span v-else :class="['status-badge', statusClass(row.status)]">{{ row.status }}</span>
              </td>
              <td v-if="colVisible.lastModified" class="cell-muted">{{ formatDate(row.lastModified) }}</td>
              <td v-if="colVisible.impactType">{{ row.impactType || '-' }}</td>
              <td v-if="colVisible.currency">{{ row.impactCurrency || '-' }}</td>
              <td v-if="colVisible.impact" class="tr fw">{{ row.impact ? Number(row.impact).toLocaleString() : '-' }}</td>
              <td v-if="colVisible.volumeCases" class="tr">{{ row.volumeImpact ? Number(row.volumeImpact).toLocaleString() : '-' }}</td>
              <template v-if="phasedImpactViews.length > 0">
                <td v-for="col in phasedColumns" :key="col.label" class="tc phased-cell">
                  {{ formatPhasedCell(getAggregatedImpact(row, col)) }}
                </td>
              </template>
              <td v-else-if="colVisible.impactPeriods">{{ formatImpactPeriods(row.childImpacts, row.impactPeriod, row.impactYear) }}</td>
              <td class="tc">
                <div class="action-btns">
                  <button class="action-icon" @click="$emit('history', row)" title="History">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  </button>
                  <button v-if="!isReadOnly && store.canCreate" class="action-icon" @click="$emit('duplicate', row)" title="Duplicate">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
                  </button>
                  <button v-if="!isReadOnly && canEditRow(row)" class="action-icon" @click="handleEditClick(row)" title="Edit">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                  </button>
                  <el-popconfirm v-if="!isReadOnly && canDeleteRow(row)" title="Delete all versions of this entry?" confirm-button-type="danger" @confirm="$emit('delete', row)">
                    <template #reference>
                      <button class="action-icon action-icon--danger" title="Delete">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                      </button>
                    </template>
                  </el-popconfirm>
                </div>
              </td>
            </tr>

            <template v-if="expandedRows.has(row.id) && row.childImpacts?.length">
              <tr v-for="(ci, cIdx) in row.childImpacts" :key="`${row.id}-c${cIdx}`" class="child-row">
                <td class="col-expand"></td>
                <td v-if="colVisible.department"     class="cell-muted">{{ row.department || '-' }}</td>
                <td v-if="colVisible.division"       class="cell-muted">{{ row.division }}</td>
                <td v-if="colVisible.country"        class="cell-muted">{{ formatCountry(row.country) }}</td>
                <td v-if="colVisible.categorisation" class="cell-muted">{{ row.categorisation }}</td>
                <td v-if="colVisible.description"    class="cell-muted">{{ row.shortDescription || '-' }}</td>
                <td v-if="colVisible.customer"       class="cell-muted">
                  <div v-if="row.account">{{ row.account }}</div>
                </td>
                <td v-if="colVisible.product"        class="cell-muted">
                  <div v-if="row.brand">{{ row.brand }}</div>
                </td>
                <td v-if="colVisible.rAndO"          class="cell-muted">{{ row.rAndO }}</td>
                <td v-if="colVisible.probability"    class="tc cell-muted">
                  <span :class="['prob-badge', `prob-${(row.probability||'').toLowerCase()}`, 'dim']">{{ (row.probability||'').charAt(0).toUpperCase() }}</span>
                </td>
                <td v-if="colVisible.addToForecastBy" class="cell-muted">-</td>
                <td v-if="colVisible.creator"        class="cell-muted">-</td>
                <td v-if="colVisible.owner"          class="cell-muted">-</td>
                <td v-if="colVisible.status"         class="cell-muted">
                  <span :class="['status-badge', statusClass(row.status), 'dim']">{{ row.status }}</span>
                </td>
                <td v-if="colVisible.lastModified"   class="cell-muted">-</td>
                <td v-if="colVisible.impactType"     class="cell-muted">{{ row.impactType || '-' }}</td>
                <td v-if="colVisible.currency"       class="cell-muted">{{ row.impactCurrency || '-' }}</td>
                <td v-if="colVisible.impact"         class="tr fw cell-muted">{{ ci.impact ? Number(ci.impact).toLocaleString() : '-' }}</td>
                <td v-if="colVisible.volumeCases"    class="tr cell-muted">{{ ci.volumeImpact ? Number(ci.volumeImpact).toLocaleString() : '-' }}</td>
                <template v-if="phasedImpactViews.length > 0">
                  <td v-for="col in phasedColumns" :key="col.label" class="tc cell-muted phased-cell">
                    {{ formatPhasedCellChild(ci, col) }}
                  </td>
                </template>
                <td v-else-if="colVisible.impactPeriods" class="cell-muted">
                  {{ ci.impactPeriod && ci.impactYear ? `${periodToMonthAbbr(ci.impactPeriod)} ${ci.impactYear}` : '-' }}
                </td>
                <td class="cell-muted tc">-</td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { ElMessage, ClickOutside as vClickOutside } from "element-plus";
import { useEntryStore } from "@/stores/entryStore";
import { useLookupStore } from "@/stores/lookupStore";
import { entryApi } from "@/services/api";
import type { Entry } from "@/types";
import { STATUS_OPTIONS } from "@/types";
import { formatDate, formatMoney, formatVol } from "@/utils/formatters";

// ─── Props / emits ────────────────────────────────────────────────────────────
const props = withDefaults(defineProps<{
  entries: Entry[];
  isReadOnly?: boolean;
  canApprove?: boolean;
  defaultSplitBy?: string[];
}>(), { isReadOnly: false, canApprove: false, defaultSplitBy: () => [] });

const emit = defineEmits<{
  edit:      [entry: Entry];
  duplicate: [entry: Entry];
  delete:    [entry: Entry];
  history:   [entry: Entry];
  approve:   [entry: Entry];
  add:       [];
}>();

// ─── Stores ───────────────────────────────────────────────────────────────────
const store        = useEntryStore();
const lookupStore = useLookupStore();

onMounted(() => {
  lookupStore.preload();
  if (store.users.length === 0) store.fetchUsers();
});

// ─── Quick filters ────────────────────────────────────────────────────────────
const quickFilters = ref({ openOnly: false, highPriority: false, recentlyModified: false });
const quickFilterDefs = [
  { key: "openOnly"         as const, label: "Show Open Only" },
  { key: "highPriority"     as const, label: "Show High Priority Only" },
  { key: "recentlyModified" as const, label: "Show Recently Modified Only" },
];
function toggleQuick(key: keyof typeof quickFilters.value) {
  quickFilters.value[key] = !quickFilters.value[key];
}
function toggleDepartment(dept: string) {
  store.filters.department = store.filters.department === dept ? "" : dept;
  store.fetchEntries();
}

// ─── All-filters panel ────────────────────────────────────────────────────────
const allFiltersOpen = ref(false);

// ─── Lookup options ───────────────────────────────────────────────────────────
const divisionOptions   = computed(() => lookupStore.getCached("division"));
const countryOptions    = computed(() => lookupStore.getCached("country"));
const channelOptions    = computed(() => lookupStore.getCached("channel"));
const categOptions      = computed(() => lookupStore.getCached("categorisation"));
const statusOptions     = computed(() => lookupStore.getCached("status"));
const departmentOptions = computed(() => lookupStore.getCached("department"));
const brandOptions      = computed(() => lookupStore.getCached("brand"));

const subChannelOptions = computed(() =>
  store.filters.channel
    ? lookupStore.getCached("sub_channel", store.filters.channel)
    : lookupStore.getCached("sub_channel")
);
const accountOptions = computed(() =>
  store.filters.sub_channel
    ? lookupStore.getCached("account", store.filters.sub_channel)
    : lookupStore.getCached("account")
);
const brandFamilyOptions = computed(() =>
  store.filters.brand
    ? lookupStore.getCached("brand_family", store.filters.brand)
    : lookupStore.getCached("brand_family")
);

watch(() => store.filters.channel, (val) => {
  store.filters.sub_channel = "";
  store.filters.account = "";
  if (val) lookupStore.loadChildren("sub_channel", val);
  store.fetchEntries();
});
watch(() => store.filters.sub_channel, (val) => {
  store.filters.account = "";
  if (val) lookupStore.loadChildren("account", val);
  store.fetchEntries();
});
watch(() => store.filters.brand, (val) => {
  store.filters.brand_family = "";
  if (val) lookupStore.loadChildren("brand_family", val);
  store.fetchEntries();
});

// ─── Filtered entries (client-side quick filters) ─────────────────────────────
const filteredEntries = computed(() => {
  let r = props.entries;
  if (quickFilters.value.openOnly)
    r = r.filter(e => e.status === "Open");
  if (quickFilters.value.highPriority)
    r = r.filter(e => e.probability === "High" || e.probability === "Very High");
  if (quickFilters.value.recentlyModified) {
    const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
    r = r.filter(e => e.lastModified && new Date(e.lastModified).getTime() > cutoff);
  }
  return r;
});

// ─── Split / group by ─────────────────────────────────────────────────────────
const splitByOptions = [
  { key: "country",     label: "Country" },
  { key: "division",    label: "Division" },
  { key: "department",  label: "Department" },
  { key: "rAndO",       label: "Risk vs. Opportunity" },
  { key: "probability", label: "Priority" },
];

const splitBy    = ref<string[]>(props.defaultSplitBy.length ? props.defaultSplitBy : ["country", "division"]);
const groupByOpen = ref(false);

const closeGroupBy = () => {
  groupByOpen.value = false;
};

function toggleSplitBy(key: string) {
  const i = splitBy.value.indexOf(key);
  if (i === -1) splitBy.value.push(key);
  else          splitBy.value.splice(i, 1);
}
function toggleAllSplitBy(checked: boolean) {
  splitBy.value = checked ? splitByOptions.map(o => o.key) : [];
}

const groupedEntries = computed(() => {
  const dims = splitBy.value;
  if (!dims.length) return [];
  const map = new Map<string, { entries: Entry[]; vals: string[] }>();
  for (const row of filteredEntries.value) {
    const vals = dims.map(d => (row as unknown as Record<string, unknown>)[d] as string || "—");
    const key  = vals.join("\0");
    if (!map.has(key)) map.set(key, { entries: [], vals });
    map.get(key)!.entries.push(row);
  }
  return Array.from(map.values())
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

// ─── Column visibility ────────────────────────────────────────────────────────
const colVisible = ref({
  department:     true,
  division:       false,
  country:        false,
  customer:       false,
  product:        false,
  rAndO:          true,
  probability:    true,
  addToForecastBy:false,
  categorisation: true,
  description:    true,
  impactType:     true,
  currency:       false,
  impact:         true,
  volumeCases:    false,
  impactPeriods:  true,
  subChannel:     true,
  account:        true,
  brandFamily:    true,
  creator:        false,
  owner:          false,
  status:         true,
  lastModified:   false,
});

// ─── Phased Impact View (multi-select) ───────────────────────────────────────
const phasedImpactViews = ref<string[]>([]);
const phasedMenuOpen    = ref(false);

const closePhasedMenu = () => {
  phasedMenuOpen.value = false;
};

const phasedViewOptions = [
  { key: "month",     label: "Month" },
  { key: "quarter",   label: "Quarter" },
  { key: "half-year", label: "Half Year" },
  { key: "year",      label: "Year" },
];

function togglePhasedView(key: string) {
  const i = phasedImpactViews.value.indexOf(key);
  if (i === -1) phasedImpactViews.value.push(key);
  else          phasedImpactViews.value.splice(i, 1);
}

function toggleAllPhasedViews(checked: boolean) {
  phasedImpactViews.value = checked ? phasedViewOptions.map(o => o.key) : [];
}

// Auto-enable Impact Type column when any phased view is active
watch(phasedImpactViews, (val) => {
  if (val.length > 0) colVisible.value.impactType = true;
});

interface PhasedCol {
  label:   string;
  periods: string[];
  year:    string;
}

const MONTH_ABBRS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function periodToMonthAbbr(period: string): string {
  const i = parseInt(period.replace("F","")) - 1;
  return (i >= 0 && i < 12) ? MONTH_ABBRS[i] : period;
}

// Build columns for all currently-selected phased views, in definition order
const phasedColumns = computed((): PhasedCol[] => {
  const cols: PhasedCol[] = [];
  const currentYear = new Date().getFullYear();
  const years = [currentYear, currentYear + 1];
  // Preserve the order defined in phasedViewOptions
  const activeKeys = phasedViewOptions.map(o => o.key).filter(k => phasedImpactViews.value.includes(k));

  for (const view of activeKeys) {
    if (view === "month") {
      for (const y of years)
        for (let m = 1; m <= 12; m++)
          cols.push({ label: `${MONTH_ABBRS[m-1]} ${y}`, periods: [`F${String(m).padStart(2,"0")}`], year: String(y) });
    } else if (view === "quarter") {
      for (const y of years)
        for (let q = 1; q <= 4; q++) {
          const sm = (q-1)*3 + 1;
          cols.push({ label: `Q${q} ${y}`, year: String(y),
            periods: [sm, sm+1, sm+2].map(m => `F${String(m).padStart(2,"0")}`) });
        }
    } else if (view === "half-year") {
      for (const y of years) {
        cols.push({ label: `H1 ${y}`, year: String(y), periods: ["F01","F02","F03","F04","F05","F06"] });
        cols.push({ label: `H2 ${y}`, year: String(y), periods: ["F07","F08","F09","F10","F11","F12"] });
      }
    } else if (view === "year") {
      for (const y of years)
        cols.push({ label: `${y} Total`, year: String(y),
          periods: Array.from({length:12},(_,i) => `F${String(i+1).padStart(2,"0")}`) });
    }
  }
  return cols;
});

function getImpactForPeriod(row: Entry, period: string, year: string): number {
  if (row.childImpacts?.length) {
    const ci = row.childImpacts.find(c => c.impactPeriod === period && c.impactYear === year);
    return ci ? (parseFloat((ci.impact as string) || "0") || 0) : 0;
  }
  return (row.impactPeriod === period && row.impactYear === year) ? (parseFloat((row.impact as string) || "0") || 0) : 0;
}

function getAggregatedImpact(row: Entry, col: PhasedCol): number {
  return col.periods.reduce((sum, p) => sum + getImpactForPeriod(row, p, col.year), 0);
}

function formatPhasedCell(val: number): string {
  return val !== 0 ? val.toLocaleString() : "-";
}

function formatPhasedCellChild(ci: NonNullable<Entry["childImpacts"]>[number], col: PhasedCol): string {
  if (!ci) return "-";
  if (col.periods.includes(ci.impactPeriod) && ci.impactYear === col.year)
    return parseFloat(ci.impact || "0").toLocaleString();
  return "-";
}

// ─── Impact period display ────────────────────────────────────────────────────
function formatImpactPeriods(
  childImpacts: Entry["childImpacts"],
  period?: string,
  year?: string
): string {
  if (!childImpacts?.length) {
    return period && year ? `${periodToMonthAbbr(period)} ${year}` : "-";
  }
  if (childImpacts && childImpacts.length === 1) {
    const c = childImpacts[0];
    return `${periodToMonthAbbr(c.impactPeriod)} ${c.impactYear}`;
  }
  const sorted = [...childImpacts]
    .filter(c => c.impactPeriod && c.impactYear)
    .sort((a, b) => {
      const yd = parseInt(a.impactYear) - parseInt(b.impactYear);
      return yd || parseInt(a.impactPeriod.substring(1)) - parseInt(b.impactPeriod.substring(1));
    });
  // Check continuity
  let continuous = true;
  for (let i = 1; i < sorted.length; i++) {
    const py = parseInt(sorted[i-1].impactYear), cy = parseInt(sorted[i].impactYear);
    const pp = parseInt(sorted[i-1].impactPeriod.replace("F","")), cp = parseInt(sorted[i].impactPeriod.replace("F",""));
    if (cy === py && cp !== pp + 1) { continuous = false; break; }
    if (cy === py + 1 && !(pp === 12 && cp === 1)) { continuous = false; break; }
    if (cy > py + 1) { continuous = false; break; }
  }
  if (continuous && sorted.length > 1) {
    const f = sorted[0], l = sorted[sorted.length - 1];
    return `${periodToMonthAbbr(f.impactPeriod)} ${f.impactYear} – ${periodToMonthAbbr(l.impactPeriod)} ${l.impactYear}`;
  }
  return sorted.map(c => `${periodToMonthAbbr(c.impactPeriod)} ${c.impactYear}`).join(", ");
}

// ─── Row expand ───────────────────────────────────────────────────────────────
const expandedRows = ref<Set<string | number>>(new Set());
function toggleExpand(id: string | number) {
  const s = new Set(expandedRows.value);
  s.has(id) ? s.delete(id) : s.add(id);
  expandedRows.value = s;
}

// ─── Row classes / status ─────────────────────────────────────────────────────
function rowClass(row: Entry): string {
  const m: Record<string, string> = {
    "Approved":             "row-approved",
    "Dismissed":            "row-dismissed",
    "Included in Forecast": "row-forecast",
  };
  return m[row.status ?? ""] ?? "";
}

function statusClass(status?: string): string {
  const m: Record<string, string> = {
    "Open":                 "status-open",
    "Approved":             "status-approved",
    "Dismissed":            "status-dismissed",
    "Included in Forecast": "status-forecast",
  };
  return m[status ?? ""] ?? "";
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
  const role = store.userRole, status = row.status;
  if (role === "System Admin") return true;
  if (role === "Department Approver") return status === "Open" || status === "Approved";
  if (role === "Finance Approver")    return status === "Approved" || status === "Dismissed" || status === "Included in Forecast";
  return false;
}

function allowedStatusRow(row: Entry): string[] {
  const role = store.userRole, status = row.status ?? "Open";
  if (role === "System Admin") return STATUS_OPTIONS;
  if (role === "Department Approver" && (status === "Open" || status === "Approved")) return ["Open","Approved"];
  if (role === "Finance Approver") return ["Approved","Dismissed","Included in Forecast"];
  return [status];
}

async function handleStatusChange(row: Entry, newStatus: string) {
  try {
    const { status: latest } = await entryApi.getStatus(row.id);
    if (latest !== row.status) {
      ElMessage.warning(`Status changed to "${latest}". Please review.`);
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

// ─── Formatters ───────────────────────────────────────────────────────────────
function formatCountry(c?: string): string {
  if (!c) return "—";
  return c === "Australia" ? "AU" : c === "New Zealand" ? "NZ" : c;
}

function formatBrandFamily(v?: string | string[]): string {
  if (!v) return "";
  if (Array.isArray(v)) return v.join(", ");
  try { const p = JSON.parse(v); return Array.isArray(p) ? p.join(", ") : v; } catch { return v; }
}

// ─── CSV Export ───────────────────────────────────────────────────────────────
function escapeCSV(v: string | number): string {
  if (v === null || v === undefined) return "";
  const s = String(v);
  return (s.includes(",") || s.includes('"') || s.includes("\n"))
    ? `"${s.replace(/"/g, '""')}"` : s;
}

function exportToCSV(rows: Entry[], filename = `entries_${new Date().toISOString().split("T")[0]}.csv`) {
  if (!rows.length) { ElMessage.warning("No entries to export"); return; }

  const headers: string[] = [];
  const cv = colVisible.value;
  if (cv.department)      headers.push("Department");
  if (cv.division)        headers.push("Division");
  if (cv.country)         headers.push("Country");
  if (cv.categorisation)  headers.push("Categorisation");
  if (cv.description)     headers.push("Short Description");
  if (cv.customer)        headers.push("Customer(s)");
  if (cv.product)         headers.push("Product");
  if (cv.rAndO)           headers.push("Risk vs. Opp.");
  if (cv.probability)     headers.push("Probability");
  if (cv.addToForecastBy) headers.push("Add to Forecast By");
  if (cv.creator)         headers.push("Creator");
  if (cv.owner)           headers.push("Owner");
  if (cv.status)          headers.push("Status");
  if (cv.lastModified)    headers.push("Last Modified");
  if (cv.impactType)      headers.push("Impact Type");
  if (cv.currency)        headers.push("Currency");
  if (cv.impact)          headers.push("Impact");
  if (cv.volumeCases)     headers.push("Volume (Cases)");
  if (phasedImpactViews.value.length > 0) {
    phasedColumns.value.forEach(c => headers.push(c.label));
  } else if (cv.impactPeriods) {
    headers.push("Impact Period(s)");
  }

  const data = rows.map(e => {
    const r: string[] = [];
    if (cv.department)      r.push(escapeCSV(e.department || ""));
    if (cv.division)        r.push(escapeCSV(e.division || ""));
    if (cv.country)         r.push(escapeCSV(e.country || ""));
    if (cv.categorisation)  r.push(escapeCSV(e.categorisation || ""));
    if (cv.description)     r.push(escapeCSV((e as any).shortDescription || e.description || ""));
    if (cv.customer)        r.push(escapeCSV([e.account, e.subChannel, e.channel].filter(Boolean).join(" / ")));
    if (cv.product)         r.push(escapeCSV([e.brand, formatBrandFamily(e.brandFamily)].filter(Boolean).join(" / ")));
    if (cv.rAndO)           r.push(escapeCSV(e.rAndO || ""));
    if (cv.probability)     r.push(escapeCSV(e.probability || ""));
    if (cv.addToForecastBy) r.push(escapeCSV(
      e.addToForecastByPeriod && e.addToForecastByYear
        ? `${e.addToForecastByPeriod} ${e.addToForecastByYear}`
        : (e.impactPeriod && e.impactYear ? `${e.impactPeriod} ${e.impactYear}` : "")));
    if (cv.creator)         r.push(escapeCSV((e as any).creator || ""));
    if (cv.owner)           r.push(escapeCSV(e.owner || ""));
    if (cv.status)          r.push(escapeCSV(e.status || "Open"));
    if (cv.lastModified)    r.push(escapeCSV(formatDate(e.lastModified)));
    if (cv.impactType)      r.push(escapeCSV(e.impactType || ""));
    if (cv.currency)        r.push(escapeCSV(e.impactCurrency || ""));
    if (cv.impact)          r.push(e.impact ? String(parseFloat(e.impact)) : "");
    if (cv.volumeCases)     r.push((e as any).volumeImpact ? String(parseFloat((e as any).volumeImpact)) : "");
    if (phasedImpactViews.value.length > 0) {
      phasedColumns.value.forEach(col => {
        const v = getAggregatedImpact(e, col);
        r.push(v !== 0 ? String(v) : "");
      });
    } else if (cv.impactPeriods) {
      r.push(escapeCSV(formatImpactPeriods(e.childImpacts, e.impactPeriod, e.impactYear)));
    }
    return r.join(",");
  });

  const blob = new Blob([[headers.join(","), ...data].join("\n")], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  ElMessage.success(`Exported ${rows.length} entries`);
}

// ─── Misc ─────────────────────────────────────────────────────────────────────
function clearFilters() {
  store.resetFilters();
  quickFilters.value = { openOnly: false, highPriority: false, recentlyModified: false };
  store.fetchEntries();
}
</script>

<style scoped>
/* ── Wrapper ──────────────────────────────────────────── */
.entries-table-wrapper {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #ddd;
  overflow: visible;
  box-shadow: none;
}

/* ── Quick filters ────────────────────────────────────── */
.quick-filters-section {
  padding: 16px 24px 12px;
  border-bottom: 1px solid var(--border-color);
}
.section-label { font-size:13px; font-weight:600; color:var(--text-secondary); margin:0 0 10px; }
.quick-filter-row { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:8px; }
.quick-filter-row:last-child { margin-bottom:0; }
.quick-btn {
  display:inline-flex; align-items:center;
  padding:5px 14px; border-radius:6px;
  border:1px solid var(--border-color);
  background:var(--bg-primary); color:var(--text-primary);
  font-size:13px; font-weight:500; cursor:pointer; transition:all 0.15s;
}
.quick-btn:hover { border-color:#6b7280; background:#f5f7fa; }
.quick-btn.active { border-color:var(--primary,#030213); background:var(--primary,#030213); color:#fff; }

/* ── All filters ──────────────────────────────────────── */
.all-filters-section { border-bottom:1px solid var(--border-color); }
.all-filters-header {
  display:flex; align-items:center; gap:6px;
  padding:12px 24px; cursor:pointer; user-select:none;
  font-size:14px; font-weight:600; color:var(--text-primary);
}
.all-filters-header:hover { background:#f9fafb; }
.chevron-icon { width:16px; height:16px; color:var(--text-secondary); transition:transform 0.2s; flex-shrink:0; }
.chevron-icon.open { transform:rotate(180deg); }
.all-filters-body { padding:4px 24px 16px; }
.filter-row { margin-bottom:12px; }
.filter-label { display:block; font-size:12px; font-weight:500; color:var(--text-secondary); margin-bottom:4px; }
.filter-group-label { font-size:12px; font-weight:600; color:#8b5cf6; margin:4px 0 10px; }
:deep(.all-filters-body .el-select),
:deep(.all-filters-body .el-input) { width:100%; }
.filter-actions { margin-top:4px; display:flex; justify-content:flex-end; }

/* ── Toolbar ──────────────────────────────────────────── */
.table-toolbar {
  display:flex; justify-content:space-between; align-items:center;
  padding:16px 24px; border-bottom:1px solid var(--border-color);
  background:linear-gradient(180deg,rgba(245,247,251,.8) 0%,rgba(241,245,252,.9) 100%);
}
.entry-count { font-size:14px; color:var(--text-secondary); font-weight:500; }
.toolbar-right { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
.split-view-control { display:flex; align-items:center; gap:8px; }
.split-view-label { font-size:13px; color:var(--text-secondary); white-space:nowrap; }

.phased-view-text {
  color: #000;
  font-weight: 500;
}

.phased-view-active {
  background-color: #000 !important;
  border-color: #000 !important;
}

.phased-view-active .phased-view-text {
  color: #fff !important;
}

.phased-view-active svg {
  stroke: #fff !important;
}

/* ── Phased view dropdown (now multi-select) ──────────── */
.phased-view-control { position:relative; }
.phased-view-trigger {
  display:flex; align-items:center; gap:6px;
  padding:5px 10px 5px 12px;
  border:1px solid var(--border-color); border-radius:6px;
  background:var(--bg-primary); font-size:13px; cursor:pointer;
  justify-content:space-between; min-width:160px;
}
.phased-view-trigger svg { width:14px; height:14px; flex-shrink:0; }
.phased-view-dropdown {
  position:absolute; top:calc(100% + 4px); right:0; z-index:9999;
  background:var(--el-bg-color-overlay); border:1px solid var(--el-border-color-light);
  border-radius:6px; box-shadow:var(--el-box-shadow-light);
  min-width:200px; padding:6px 0;
}

/* ── Group-by dropdown (multi-checkbox) ──────────────── */
.group-by-wrap { position:relative; }
.group-by-trigger {
  display:flex; align-items:center; gap:6px;
  padding:5px 10px 5px 12px;
  border:1px solid var(--border-color); border-radius:6px;
  background:var(--bg-primary); font-size:13px; cursor:pointer;
  min-width:140px; justify-content:space-between;
}
.group-by-trigger .has-value { color:var(--text-primary); }
.group-by-trigger .placeholder { color:var(--el-text-color-placeholder); }
.chevron-sm { width:14px; height:14px; color:var(--text-secondary); flex-shrink:0; }
.group-by-dropdown {
  position:absolute; top:calc(100% + 4px); left:0; z-index:9999;
  background:var(--el-bg-color-overlay); border:1px solid var(--el-border-color-light);
  border-radius:6px; box-shadow:var(--el-box-shadow-light);
  min-width:200px; padding:6px 0;
}
.gbd-item {
  display:flex; align-items:center; gap:8px;
  padding:6px 12px; font-size:13px; cursor:pointer;
  color:var(--el-text-color-regular);
}
.gbd-item:hover { background:var(--el-fill-color); }
.gbd-all { border-bottom:1px solid var(--el-border-color-lighter); }
.gbd-label-bold { font-weight:600; }
.gbd-divider { height:1px; background:var(--el-border-color-lighter); margin:2px 0; }

/* ── Column selector popover ─────────────────────────── */
.column-popover {
  padding: 12px 0 12px 12px !important;
}

.column-selector-container { display: flex; flex-direction: column; }
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

/* ── Table scroll wrapper ─────────────────────────────── */
.table-scroll-wrap { overflow-x:auto; -webkit-overflow-scrolling:touch; }

/* ── Data table ───────────────────────────────────────── */
.data-table {
  width:100%; border-collapse:collapse;
  font-size:13px; color:var(--text-primary);
}
.data-table th {
  background:#f8f9fc; font-weight:600; font-size:12px;
  padding:9px 12px; white-space:nowrap;
  border-bottom:1px solid var(--border-color);
  color:var(--text-secondary); text-align:left;
}
.data-table td {
  padding:8px 12px; border-bottom:1px solid #f0f2f5;
  vertical-align:middle; white-space:nowrap;
}
.data-table tr:last-child td { border-bottom:none; }
.data-table tbody tr:hover td { background:#f9fafb; }

/* Row state styles */
.row-approved td  { background:#f0fdf4 !important; }
.row-dismissed td { background:#f3f4f6 !important; }
.row-forecast td  { background:#eff6ff !important; }

/* Child rows */
.child-row td { background:#fafafa; padding-left:24px; }
.child-row:hover td { background:#f3f4f6 !important; }

/* Column width helpers */
.col-expand  { width:36px; }
.col-sm      { min-width:80px; }
.col-md      { min-width:120px; }
.col-lg      { min-width:150px; }
.col-xl      { min-width:200px; max-width:240px; overflow:hidden; text-overflow:ellipsis; }
.col-phased  { min-width:90px; }
.col-actions { width:120px; }

/* Text alignment helpers */
.tc { text-align:center; }
.tr { text-align:left; }
.fw { font-weight:600; }

/* ── Expand button ────────────────────────────────────── */
.expand-btn {
  display:inline-flex; align-items:center; justify-content:center;
  width:22px; height:22px; border:none; background:transparent;
  border-radius:4px; cursor:pointer; color:#6b7280; padding:0;
}
.expand-btn:hover { background:#f3f4f6; }
.expand-icon { width:14px; height:14px; transition:transform 0.2s; }
.expand-icon.rotated { transform:rotate(90deg); }

/* ── Cell helpers ─────────────────────────────────────── */
.cell-muted { color:#9ca3af; }
.cell-sub { font-size:11px; color:#9ca3af; }
.italic { font-style:italic; }
.phased-cell { font-variant-numeric:tabular-nums; }

/* ── Status badge ─────────────────────────────────────── */
.status-badge {
  display:inline-block; padding:2px 8px; border-radius:4px;
  font-size:12px; font-weight:500;
}
.status-open     { background:#f3f4f6; color:#374151; }
.status-approved { background:#dcfce7; color:#166534; }
.status-dismissed{ background:#6b7280; color:#fff; }
.status-forecast { background:#dbeafe; color:#1e40af; }
.dim { opacity:.5; }

/* ── Probability badge ────────────────────────────────── */
.prob-badge {
  display:inline-flex; align-items:center; justify-content:center;
  width:28px; height:28px; border-radius:6px;
  font-size:12px; font-weight:700; cursor:default;
}
.prob-high   { background:#0d9488; color:#fff; }
.prob-medium { background:#cffafe; color:#0e7490; }
.prob-low    { background:#e0f2fe; color:#0369a1; }

/* ── Action buttons ───────────────────────────────────── */
.action-btns { display:flex; align-items:center; justify-content:center; gap:4px; }
.action-icon {
  display:inline-flex; align-items:center; justify-content:center;
  width:28px; height:28px; border:none; background:transparent;
  border-radius:6px; cursor:pointer; color:#6b7280;
  transition:background 0.15s, color 0.15s; padding:0;
}
.action-icon svg { width:15px; height:15px; }
.action-icon:hover { background:#f3f4f6; color:#111827; }
.action-icon--danger { color:#d4183d; }
.action-icon--danger:hover { background:#fff1f3; color:#d4183d; }

/* ── Split group ──────────────────────────────────────── */
.split-group { margin-bottom:24px; }
.split-group-header {
  display:flex; align-items:center; justify-content:space-between;
  padding:10px 16px; background:#f8f9fc;
  border-left:3px solid #030213;
  border-top:1px solid var(--border-color);
  border-bottom:1px solid var(--border-color);
}
.split-group-breadcrumb { display:flex; align-items:center; gap:4px; flex-wrap:wrap; }
.split-sep { color:#9ca3af; font-size:13px; padding:0 2px; }
.split-chip {
  display:inline-flex; align-items:center; gap:5px;
  background:#fff; border:1px solid #e5e7eb;
  border-radius:6px; padding:3px 9px; font-size:12px;
}
.split-chip-label { color:#9ca3af; font-weight:500; }
.split-chip-val   { color:#111827; font-weight:600; }
.split-group-actions { display:flex; align-items:center; gap:8px; }
.split-count {
  font-size:12px; font-weight:600; color:#fff;
  background:#030213; border-radius:20px;
  padding:2px 12px; white-space:nowrap; flex-shrink:0;
}

/* ── Scrollbar styling ────────────────────────────────── */
.table-scroll-wrap::-webkit-scrollbar { height:8px; }
.table-scroll-wrap::-webkit-scrollbar-track { background:transparent; }
.table-scroll-wrap::-webkit-scrollbar-thumb { background:rgba(0,0,0,.22); border-radius:4px; }
.table-scroll-wrap::-webkit-scrollbar-thumb:hover { background:rgba(0,0,0,.42); }
</style>