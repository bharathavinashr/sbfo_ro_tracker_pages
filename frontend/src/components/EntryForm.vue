<template>
  <div class="entry-form-wrapper">
    <div class="form-header">
      <h2 class="form-title">{{ props.entry?.id ? "Edit Entry" : "Create New Entry" }}</h2>
    </div>
  <el-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    label-position="top"
  >
    <!-- ───────────────────────────────────────────────
         SECTION 1 · Entry Owner
    ─────────────────────────────────────────────── -->
    <!-- <el-divider content-position="left">Entry Owner</el-divider> -->
    <el-row :gutter="16">
      <!-- Creator (read-only) -->
      <el-col :span="12">
        <el-form-item label="Creator" prop="creator">
          <el-input v-model="formData.creator" disabled />
        </el-form-item>
      </el-col>

      <!-- Owner -->
      <el-col :span="12">
        <el-form-item label="Owner" prop="owner">
          <div class="owner-wrap">
            <el-checkbox v-model="ownerSameAsCreator" @change="onOwnerCheckboxChange">
              Same as Creator
            </el-checkbox>
            <el-select
              v-if="!ownerSameAsCreator"
              v-model="formData.owner"
              style="width: 100%; margin-top: 8px"
              filterable
            >
              <el-option
                v-for="u in ownerOptions"
                :key="u.email"
                :value="u.email"
                :label="u.display_name ? `${u.display_name} (${u.email})` : u.email"
              />
            </el-select>
          </div>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- ───────────────────────────────────────────────
         SECTION 2 · Period fields (Creation + Forecast)
    ─────────────────────────────────────────────── -->
    <el-divider content-position="left">Periods</el-divider>
    <el-row :gutter="16">
      <!-- Creation Period -->
      <el-col :span="12">
        <el-form-item label="Creation Period" prop="creationDatePeriod">
          <div class="period-pair">
            <el-select v-model="formData.creationDatePeriod" class="period-select">
              <el-option
                v-for="p in PERIODS"
                :key="p"
                :value="p"
                :label="periodToMonth(p)"
              />
            </el-select>
            <el-select v-model="formData.creationDateYear" class="year-select">
              <el-option
                v-for="y in yearOptions"
                :key="y"
                :value="String(y)"
                :label="String(y)"
              />
            </el-select>
          </div>
        </el-form-item>
      </el-col>

      <!-- Add to Forecast By -->
      <el-col :span="12">
        <el-form-item label="Add to Forecast By" prop="addToForecastByPeriod">
          <div class="period-pair">
            <el-select v-model="formData.addToForecastByPeriod" class="period-select">
              <el-option
                v-for="p in PERIODS"
                :key="p"
                :value="p"
                :label="p"
              />
            </el-select>
            <el-select v-model="formData.addToForecastByYear" class="year-select">
              <el-option
                v-for="y in yearOptions"
                :key="y"
                :value="String(y)"
                :label="String(y)"
              />
            </el-select>
          </div>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- ───────────────────────────────────────────────
         SECTION 3 · Organisation
    ─────────────────────────────────────────────── -->
    <el-divider content-position="left">Organisation</el-divider>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="Department" prop="department">
          <el-select v-model="formData.department" style="width: 100%">
            <el-option v-for="d in departmentOptions" :key="d" :value="d" :label="d" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Division" prop="division">
          <el-select v-model="formData.division" style="width: 100%">
            <el-option v-for="d in divisionOptions" :key="d" :value="d" :label="d" />
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item label="Country" prop="country">
          <el-select v-model="formData.country" style="width: 100%">
            <el-option v-for="c in countryOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- Categorisation (conditional) -->
    <el-row :gutter="16">
      <el-col :span="24">
        <el-form-item
          label="Categorisation"
          prop="categorisation"
          :required="categActive"
        >
          <el-select
            v-model="formData.categorisation"
            style="width: 100%"
            :disabled="!categActive"
            :placeholder="categActive ? 'Select categorisation' : 'Only available for Portfolio Review, Demand Review, Supply Review, or Pre-Exec Review'"
          >
            <el-option v-for="c in categOptions" :key="c" :value="c" :label="c" />
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- ───────────────────────────────────────────────
         SECTION 4 · Description
    ─────────────────────────────────────────────── -->
    <el-divider content-position="left">Description</el-divider>
    <el-row :gutter="16">
      <el-col :span="24">
        <el-form-item prop="shortDescription">
          <template #label>
            Short Description <span style="color: #d4183d">*</span>
            <span class="char-count">
              ({{ formData.shortDescription.length }}/100)
            </span>
          </template>
          <el-input
            v-model="formData.shortDescription"
            placeholder="Enter a brief description (max 100 characters)..."
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="24">
        <el-form-item label="Detailed Description" prop="detailedDescription">
          <el-input
            v-model="formData.detailedDescription"
            type="textarea"
            :rows="4"
            placeholder="Enter a detailed description (optional)..."
          />
        </el-form-item>
      </el-col>
    </el-row>

    <!-- ───────────────────────────────────────────────
         SECTION 5 · Customer
    ─────────────────────────────────────────────── -->
    <el-divider content-position="left">Customer</el-divider>
    <el-row :gutter="16">
      <!-- Channel – combobox -->
      <el-col :span="12">
        <el-form-item label="Channel" prop="channel">
          <div class="combo-wrap">
            <el-input
              v-model="channelSearch"
              :placeholder="formData.channel || 'Select or enter channel'"
              @focus="channelOpen = true"
              @blur="onChannelBlur"
              @input="channelOpen = true"
              clearable
              @clear="formData.channel = ''; channelSearch = ''"
            >
              <template #suffix>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </template>
            </el-input>
            <div v-if="channelOpen" class="combo-dropdown">
              <div
                v-for="c in filteredChannels"
                :key="c"
                class="combo-item"
                :class="{ 'is-disabled': isChannelDisabled(c) }"
                @mousedown.prevent="selectChannel(c)"
              >
                {{ c }}
              </div>
              <div
                v-if="filteredChannels.length === 0 && channelSearch"
                class="combo-custom"
                @mousedown.prevent="formData.channel = channelSearch; channelOpen = false"
              >
                Use custom value: "{{ channelSearch }}"
              </div>
              <div v-if="filteredChannels.length === 0 && !channelSearch" class="combo-empty">
                No matches found
              </div>
            </div>
          </div>
        </el-form-item>
      </el-col>

      <!-- Brand – combobox -->
      <el-col :span="12">
        <el-form-item label="Brand" prop="brand">
          <div class="combo-wrap">
            <el-input
              v-model="brandSearch"
              :placeholder="formData.brand || 'Select or enter brand'"
              @focus="brandOpen = true"
              @blur="onBrandBlur"
              @input="brandOpen = true"
              clearable
              @clear="formData.brand = ''; brandSearch = ''"
            >
              <template #suffix>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </template>
            </el-input>
            <div v-if="brandOpen" class="combo-dropdown">
              <div
                v-for="b in filteredBrands"
                :key="b"
                class="combo-item"
                @mousedown.prevent="formData.brand = b; brandSearch = ''; brandOpen = false"
              >
                {{ b }}
              </div>
              <div
                v-if="filteredBrands.length === 0 && brandSearch"
                class="combo-custom"
                @mousedown.prevent="formData.brand = brandSearch; brandOpen = false"
              >
                Use custom value: "{{ brandSearch }}"
              </div>
              <div v-if="filteredBrands.length === 0 && !brandSearch" class="combo-empty">
                No matches found
              </div>
            </div>
          </div>
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <!-- Sub-Channel – combobox -->
      <el-col :span="8">
        <el-form-item label="Sub-Channel" prop="subChannel">
          <div class="combo-wrap">
            <el-input
              v-model="subChannelSearch"
              :placeholder="formData.subChannel || 'Select or enter sub-channel'"
              @focus="subChannelOpen = true"
              @blur="onSubChannelBlur"
              @input="subChannelOpen = true"
              clearable
              @clear="formData.subChannel = ''; subChannelSearch = ''"
            >
              <template #suffix>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </template>
            </el-input>
            <div v-if="subChannelOpen" class="combo-dropdown">
              <div
                v-for="s in filteredSubChannels"
                :key="s"
                class="combo-item"
                @mousedown.prevent="formData.subChannel = s; subChannelSearch = ''; subChannelOpen = false"
              >
                {{ s }}
              </div>
              <div
                v-if="filteredSubChannels.length === 0 && subChannelSearch"
                class="combo-custom"
                @mousedown.prevent="formData.subChannel = subChannelSearch; subChannelOpen = false"
              >
                Use custom value: "{{ subChannelSearch }}"
              </div>
              <div v-if="filteredSubChannels.length === 0 && !subChannelSearch" class="combo-empty">
                No matches found
              </div>
            </div>
          </div>
        </el-form-item>
      </el-col>

      <!-- Brand Family – multi-select combobox -->
      <el-col :span="8">
        <el-form-item label="Brand Family" prop="brandFamily">
          <div class="combo-wrap" ref="brandFamilyRef">
            <div
              class="combo-trigger"
              @click="brandFamilyOpen = !brandFamilyOpen"
            >
              <span :class="formData.brandFamily.length ? 'has-value' : 'placeholder'">
                {{ formData.brandFamily.length ? formData.brandFamily.join(', ') : 'Select one or more brand families' }}
              </span>
              <el-icon class="combo-arrow"><ArrowDown /></el-icon>
            </div>
            <div v-if="brandFamilyOpen" class="combo-dropdown brand-family-dropdown">
              <el-input
                v-model="brandFamilySearch"
                placeholder="Type to search or add custom..."
                class="bf-search"
                @keydown.enter.prevent="addCustomBrandFamily"
              />
              <div
                v-if="brandFamilySearch.trim() && !brandFamilyOptions.some(f => f.toLowerCase() === brandFamilySearch.toLowerCase())"
                class="combo-custom"
                @mousedown.prevent="addCustomBrandFamily"
              >
                + Add custom: "{{ brandFamilySearch }}"
              </div>

              <!-- Custom values already selected -->
              <template v-if="formData.brandFamily.filter(f => !brandFamilyOptions.includes(f)).length">
                <div class="bf-section-label">Custom Values</div>
                <div
                  v-for="f in formData.brandFamily.filter(fv => !brandFamilyOptions.includes(fv))"
                  :key="f"
                  class="combo-item combo-check-item"
                  @mousedown.prevent="toggleBrandFamily(f)"
                >
                  <el-checkbox :model-value="true" />
                  <span>{{ f }}</span>
                </div>
                <div class="bf-divider" />
              </template>

              <!-- Select All -->
              <div
                class="combo-item combo-check-item bf-select-all"
                @mousedown.prevent="toggleAllBrandFamilies"
              >
                <el-checkbox :model-value="allBrandFamiliesSelected" />
                <span class="bf-select-all-label">Select All Suggestions</span>
              </div>

              <!-- Predefined -->
              <div
                v-for="f in filteredBrandFamilies"
                :key="f"
                class="combo-item combo-check-item"
                @mousedown.prevent="toggleBrandFamily(f)"
              >
                <el-checkbox :model-value="formData.brandFamily.includes(f)" />
                <span>{{ f }}</span>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-col>

      <!-- Account – combobox -->
      <el-col :span="8">
        <el-form-item label="Account" prop="account">
          <div class="combo-wrap">
            <el-input
              v-model="accountSearch"
              :placeholder="formData.account || 'Select or enter account'"
              @focus="accountOpen = true"
              @blur="onAccountBlur"
              @input="accountOpen = true"
              clearable
              @clear="formData.account = ''; accountSearch = ''"
            >
              <template #suffix>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </template>
            </el-input>
            <div v-if="accountOpen" class="combo-dropdown">
              <div
                v-for="a in filteredAccounts"
                :key="a"
                class="combo-item"
                @mousedown.prevent="formData.account = a; accountSearch = ''; accountOpen = false"
              >
                {{ a }}
              </div>
              <div
                v-if="filteredAccounts.length === 0 && accountSearch"
                class="combo-custom"
                @mousedown.prevent="formData.account = accountSearch; accountOpen = false"
              >
                Use custom value: "{{ accountSearch }}"
              </div>
              <div v-if="filteredAccounts.length === 0 && !accountSearch" class="combo-empty">
                No matches found
              </div>
            </div>
          </div>
        </el-form-item>
      </el-col>
    </el-row>

    <!-- ───────────────────────────────────────────────
         SECTION 6 · Risk & Opportunity
    ─────────────────────────────────────────────── -->
    <el-divider content-position="left">Risk &amp; Opportunity</el-divider>
    <el-row :gutter="16">
      <!-- R&O Type -->
      <el-col :span="8">
        <el-form-item label="R&O Type" prop="rAndO">
          <div class="toggle-group">
            <button
              type="button"
              class="toggle-btn"
              :class="{ 'is-active': formData.rAndO === 'Risk' }"
              @click="formData.rAndO = 'Risk'"
            >Risk</button>
            <button
              type="button"
              class="toggle-btn"
              :class="{ 'is-active': formData.rAndO === 'Opportunity' }"
              @click="formData.rAndO = 'Opportunity'"
            >Opportunity</button>
          </div>
        </el-form-item>
      </el-col>

      <!-- Probability -->
      <el-col :span="8">
        <el-form-item label="Probability" prop="probability">
          <div class="toggle-group">
            <button
              v-for="p in probabilityOptions"
              :key="p"
              type="button"
              class="toggle-btn"
              :class="{ 'is-active': formData.probability === p }"
              @click="formData.probability = p"
            >{{ p }}</button>
          </div>
        </el-form-item>
      </el-col>

      <!-- Categorisation (already shown above; kept here for grouping if needed) -->
      <el-col :span="8" />
    </el-row>

    <!-- ───────────────────────────────────────────────
         SECTION 7 · Impact Details
    ─────────────────────────────────────────────── -->
    <el-divider content-position="left">Impact Details</el-divider>

    <!-- Country gate -->
    <div v-if="!formData.country" class="impact-locked">
      <el-icon><InfoFilled /></el-icon>
      Please select a Country first to enable Impact Details.
    </div>

    <template v-else>
      <!-- Primary impact card -->
      <div class="impact-card" :class="{ 'has-children': hasChildImpacts }">
        <el-row :gutter="16">
          <!-- Left: Period -->
          <el-col :span="12">
            <div class="impact-field-label">
              Primary Impact Period <span class="impact-required">*</span>
            </div>

            <!-- Summary when children exist -->
            <el-input
              v-if="hasChildImpacts"
              :model-value="impactPeriodSummary || 'Add child impact periods'"
              disabled
              class="mt-2"
            />

            <!-- Period range mode -->
            <template v-else-if="usePeriodRange">
              <div class="range-block mt-2">
                <div class="range-label">Start Period</div>
                <div class="period-pair">
                  <el-select v-model="periodRangeStart.period" class="period-select">
                    <el-option v-for="p in PERIODS" :key="p" :value="p" :label="periodToMonth(p)" />
                  </el-select>
                  <el-select v-model="periodRangeStart.year" class="year-select">
                    <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
                  </el-select>
                </div>
                <div class="range-label mt-2">End Period</div>
                <div class="period-pair">
                  <el-select v-model="periodRangeEnd.period" class="period-select">
                    <el-option v-for="p in PERIODS" :key="p" :value="p" :label="periodToMonth(p)" />
                  </el-select>
                  <el-select v-model="periodRangeEnd.year" class="year-select">
                    <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
                  </el-select>
                </div>
                <el-button
                  type="primary"
                  style="width: 100%; margin-top: 10px"
                  :disabled="!periodRangeStart.period || !periodRangeStart.year || !periodRangeEnd.period || !periodRangeEnd.year || !formData.impactValue"
                  @click="createChildImpactsFromRange"
                >Generate Prorated Impacts</el-button>
              </div>
            </template>

            <!-- Normal single period -->
            <template v-else>
              <div class="period-pair mt-2">
                <el-select v-model="formData.impactPeriod" :disabled="hasChildImpacts" class="period-select">
                  <el-option v-for="p in PERIODS" :key="p" :value="p" :label="periodToMonth(p)" />
                </el-select>
                <el-select v-model="formData.impactYear" :disabled="hasChildImpacts" class="year-select">
                  <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
                </el-select>
              </div>
              <div v-if="!hasChildImpacts" class="period-range-check">
                <el-checkbox v-model="usePeriodRange">Use Period Range</el-checkbox>
              </div>
            </template>
          </el-col>

          <!-- Right: Impact type + values -->
          <el-col :span="12">
            <!-- Impact Type toggle -->
            <div class="impact-field-label">Impact Type <span class="impact-required">*</span></div>
            <div class="toggle-group mt-2">
              <button
                type="button"
                class="toggle-btn"
                :class="{ 'is-active': formData.primaryImpact !== 'Volume' && formData.impactType === 'NSV' }"
                @click="formData.impactType = 'NSV'"
              >NSV</button>
              <button
                type="button"
                class="toggle-btn"
                :class="{ 'is-active': formData.primaryImpact !== 'Volume' && formData.impactType === 'COGS' }"
                @click="formData.impactType = 'COGS'"
              >COGS</button>
              <button
                type="button"
                class="toggle-btn"
                :class="{ 'is-active': formData.primaryImpact !== 'Volume' && formData.impactType === 'LOGS' }"
                @click="formData.impactType = 'LOGS'"
              >LOGS</button>
              <button
                type="button"
                class="toggle-btn"
                :class="{ 'is-active': formData.impactType === 'OI' }"
                @click="formData.impactType = 'OI'"
              >OI</button>
            </div>

            <!-- Primary impact value (based on selected Impact Type) -->
            <div class="impact-field-label mt-3">
              {{ getImpactTypeLabel(formData.impactType) }}
              <span class="impact-required">*</span>
            </div>
            <div class="input-unit-row mt-1">
              <div class="unit-chip">{{ getImpactTypeLabel(formData.impactType) }}</div>
              <el-input
                :model-value="formData.impactValue"
                :disabled="hasChildImpacts"
                :placeholder="`Enter ${getImpactTypeLabel(formData.impactType)} value`"
                @input="formData.impactValue = cleanNumStr($event as string)"
                @blur="formData.impactValue = formatNumStr(formData.impactValue)"
                @focus="formData.impactValue = cleanNumStr(formData.impactValue)"
              />
            </div>

            <!-- Secondary value (Volume) - only shown for NSV and COGS -->
            <template v-if="['NSV', 'COGS'].includes(formData.impactType)">
              <div class="impact-field-label mt-3">
                Volume (Cases)
                <span v-if="formData.impactType === 'COGS'" class="optional-tag">(optional)</span>
                <span v-else class="impact-required">*</span>
              </div>
              <div class="input-unit-row mt-1">
                <div class="unit-chip">Volume (Cases)</div>
                <el-input
                  :model-value="formData.secondaryValue"
                  :disabled="hasChildImpacts"
                  placeholder="Enter volume in cases"
                  @input="formData.secondaryValue = cleanNumStr($event as string)"
                  @blur="formData.secondaryValue = formatNumStr(formData.secondaryValue)"
                  @focus="formData.secondaryValue = cleanNumStr(formData.secondaryValue)"
                />
              </div>
            </template>
          </el-col>
        </el-row>

        <div class="add-impact-row">
          <el-button plain @click="addChild">
            <el-icon><Plus /></el-icon>
            Add Impact
          </el-button>
        </div>
      </div>

      <!-- Child impact rows -->
      <div
        v-for="(child, idx) in formData.childImpacts"
        :key="idx"
        class="impact-child-card"
      >
        <el-row :gutter="16" align="middle">
          <el-col :span="['NSV', 'COGS'].includes(formData.impactType) ? 6 : 8">
            <div class="impact-field-label">Period <span class="impact-required">*</span></div>
            <el-select v-model="child.impactPeriod" placeholder="Period" style="width: 100%; margin-top: 6px">
              <el-option v-for="p in PERIODS" :key="p" :value="p" :label="periodToMonth(p)" />
            </el-select>
          </el-col>
          <el-col :span="['NSV', 'COGS'].includes(formData.impactType) ? 6 : 8">
            <div class="impact-field-label">Year</div>
            <el-select v-model="child.impactYear" style="width: 100%; margin-top: 6px">
              <el-option v-for="y in yearOptions" :key="y" :value="String(y)" :label="String(y)" />
            </el-select>
          </el-col>
          <el-col :span="['NSV', 'COGS'].includes(formData.impactType) ? 6 : 8">
            <div class="impact-field-label">{{ getImpactTypeLabel(formData.impactType) }} <span class="impact-required">*</span></div>
            <el-input
              :model-value="child.impactValue"
              placeholder="Enter value"
              style="margin-top: 6px"
              @input="child.impactValue = cleanNumStr($event as string)"
              @blur="child.impactValue = formatNumStr(child.impactValue)"
              @focus="child.impactValue = cleanNumStr(child.impactValue)"
            />
          </el-col>
          <el-col v-if="['NSV', 'COGS'].includes(formData.impactType)" :span="6">
            <div class="impact-field-label">
              Volume (Cases)
              <span v-if="formData.impactType === 'COGS'" class="optional-tag">(optional)</span>
              <span v-else class="impact-required">*</span>
            </div>
            <el-input
              :model-value="child.secondaryValue"
              placeholder="Enter value"
              style="margin-top: 6px"
              @input="child.secondaryValue = cleanNumStr($event as string)"
              @blur="child.secondaryValue = formatNumStr(child.secondaryValue)"
              @focus="child.secondaryValue = cleanNumStr(child.secondaryValue)"
            />
          </el-col>
        </el-row>
        <div class="child-remove-row">
          <el-button type="danger" link @click="removeChild(idx)">
            <el-icon><Delete /></el-icon>
            Remove
          </el-button>
        </div>
      </div>

      <!-- Totals -->
      <div v-if="hasChildImpacts" class="totals-bar">
        <div class="totals-item">
          <span class="totals-label">Total {{ getImpactTypeLabel(formData.impactType) }}</span>
          <span class="totals-value">{{ formatNumStr(totalPrimaryImpact) }} {{ currencyCode }}</span>
        </div>
        <div v-if="secondaryTotalVisible && ['NSV', 'COGS'].includes(formData.impactType)" class="totals-item">
          <span class="totals-label">Total Volume (Cases)</span>
          <span class="totals-value">{{ formatNumStr(totalSecondaryImpact) }}</span>
        </div>
      </div>
    </template>

  </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from "vue";
import { Delete, InfoFilled, ArrowDown, Plus } from "@element-plus/icons-vue";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import type { Entry } from "@/types";
import { PERIODS } from "@/types";
import { useLookupStore } from "@/stores/lookupStore";
import { useEntryStore } from "@/stores/entryStore";

// ─────────────────────────────────────────────────────────────────────────────
// Stores & user info
// ─────────────────────────────────────────────────────────────────────────────
const lookupStore = useLookupStore();
const entryStore  = useEntryStore();

const currentUserEmail = computed(() => entryStore.currentUser?.email ?? "");
const ownerOptions = computed(() =>
  entryStore.users.filter((u) => u.role === 0 || u.role === 1)
);

onMounted(() => {
  lookupStore.preload();
  if (entryStore.users.length === 0) entryStore.fetchUsers();
  document.addEventListener("mousedown", handleBrandFamilyClickOutside);
});
onBeforeUnmount(() => {
  document.removeEventListener("mousedown", handleBrandFamilyClickOutside);
});

// ─────────────────────────────────────────────────────────────────────────────
// Lookup options (from store)
// ─────────────────────────────────────────────────────────────────────────────
const divisionOptions    = computed(() => lookupStore.getCached("division"));
const countryOptions     = computed(() => lookupStore.getCached("country"));
const probabilityOptions = computed(() => lookupStore.getCached("probability"));
const ibpStepOptions     = computed(() => lookupStore.getCached("ibp_step"));
const departmentOptions   = computed(() => lookupStore.getCached("department"));

// Categorisation: switches list based on department + division (mirrors React prototype)
const CATEG_ACTIVE_DEPTS = ["Portfolio Review", "Demand Review", "Supply Review", "Overheads (Pre-Exec)"];
const categActive = computed(() => CATEG_ACTIVE_DEPTS.includes(formData.value.department));

const supplyCategorisations   = ["Conversion (Wiri)", "Conversion (Swanbank)", "Co-Pack", "Agency", "Materials", "Stock", "Int/TT Freight", "Other"];
const overheadsCategorisations = ["People Costs", "Other People Costs", "Total People Costs", "Strategic Projects", "Vehicles", "Travel & Entertainment", "Communication", "Leases & Rentals", "Utilities", "Repairs & Maintenance", "Depreciation", "Printing & Stationery", "Administration", "Professional Fees", "IT Supplies", "Market Research", "3rd Party Merchandisers", "Insurance", "Group recharges / Sundry Income"];
const alcoholCategorisations  = ["Customer SOH", "Ranging", "Phasing", "Excise", "Rate", "Allocations"];
const baseCategorisations     = ["Baseline/Run Rates", "Brand Activations", "Deletions", "Long Term Forecast", "NPD", "New Business", "OOS", "Promotional Pricing", "Strategic/MTP/Trading Terms"];

const categOptions = computed(() => {
  if (formData.value.department === "Supply Review") return supplyCategorisations;
  if (formData.value.department === "Overheads (Pre-Exec)") return overheadsCategorisations;
  if (
    formData.value.division === "Alcohol" &&
    (formData.value.department === "Portfolio Review" || formData.value.department === "Demand Review")
  ) return [...baseCategorisations, ...alcoholCategorisations];
  return baseCategorisations;
});

// ─────────────────────────────────────────────────────────────────────────────
// Combobox data (from lookupStore)
// ─────────────────────────────────────────────────────────────────────────────
const channelOptions    = computed(() => lookupStore.getCached("channel"));
const subChannelOptions = computed(() =>
  formData.value.channel
    ? lookupStore.getCached("sub_channel", formData.value.channel)
    : lookupStore.getCached("sub_channel")
);
const accountOptions    = computed(() =>
  formData.value.subChannel
    ? lookupStore.getCached("account", formData.value.subChannel)
    : lookupStore.getCached("account")
);
const brandOptions      = computed(() => lookupStore.getCached("brand"));
const brandFamilyOptions = computed(() =>
  formData.value.brand
    ? lookupStore.getCached("brand_family", formData.value.brand)
    : lookupStore.getCached("brand_family")
);

// Combobox open/search state
const channelOpen      = ref(false);
const channelSearch    = ref("");
const subChannelOpen   = ref(false);
const subChannelSearch = ref("");
const brandOpen        = ref(false);
const brandSearch      = ref("");
const brandFamilyOpen  = ref(false);
const brandFamilySearch = ref("");
const accountOpen      = ref(false);
const accountSearch    = ref("");
const brandFamilyRef = ref<HTMLElement | null>(null);

function handleBrandFamilyClickOutside(event: MouseEvent) {
  if (brandFamilyRef.value && !brandFamilyRef.value.contains(event.target as Node)) {
    brandFamilyOpen.value = false;
  }
}

// Filtered lists
const filteredChannels    = computed(() => channelOptions.value.filter(c => c.toLowerCase().includes(channelSearch.value.toLowerCase())));
const filteredSubChannels = computed(() => subChannelOptions.value.filter(s => s.toLowerCase().includes(subChannelSearch.value.toLowerCase())));
const filteredBrands      = computed(() => brandOptions.value.filter(b => b.toLowerCase().includes(brandSearch.value.toLowerCase())));
const filteredAccounts    = computed(() => accountOptions.value.filter(a => a.toLowerCase().includes(accountSearch.value.toLowerCase())));
const filteredBrandFamilies = computed(() =>
  brandFamilyOptions.value.filter(f => f.toLowerCase().includes(brandFamilySearch.value.toLowerCase()))
);
const allBrandFamiliesSelected = computed(() =>
  brandFamilyOptions.value.length > 0 && brandFamilyOptions.value.every(f => formData.value.brandFamily.includes(f))
);

function isChannelDisabled(ch: string) {
  if (formData.value.division === "Non-Alcohol") return ch === "Licensed" || ch === "Route";
  if (formData.value.division === "Alcohol")     return ch === "Convenience" || ch === "Grocery";
  return false;
}
function selectChannel(ch: string) {
  if (!isChannelDisabled(ch)) {
    formData.value.channel = ch;
    channelSearch.value = "";
    channelOpen.value = false;
  }
}
function onChannelBlur()    { setTimeout(() => { channelOpen.value    = false; }, 120); }
function onSubChannelBlur() { setTimeout(() => { subChannelOpen.value = false; }, 120); }
function onBrandBlur()      { setTimeout(() => { brandOpen.value      = false; }, 120); }
function onAccountBlur()    { setTimeout(() => { accountOpen.value    = false; }, 120); }

// Brand family multi-select helpers
function toggleBrandFamily(f: string) {
  const idx = formData.value.brandFamily.indexOf(f);
  if (idx === -1) formData.value.brandFamily.push(f);
  else            formData.value.brandFamily.splice(idx, 1);
}
function addCustomBrandFamily() {
  const val = brandFamilySearch.value.trim();
  if (val && !formData.value.brandFamily.includes(val)) {
    formData.value.brandFamily.push(val);
  }
  brandFamilySearch.value = "";
}
function toggleAllBrandFamilies() {
  const predefined = brandFamilyOptions.value;
  if (allBrandFamiliesSelected.value) {
    formData.value.brandFamily = formData.value.brandFamily.filter(f => !predefined.includes(f));
  } else {
    const custom = formData.value.brandFamily.filter(f => !predefined.includes(f));
    formData.value.brandFamily = [...predefined, ...custom];
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Form data types
// ─────────────────────────────────────────────────────────────────────────────
interface ChildImpactForm {
  impactYear:     string;
  impactPeriod:   string;
  impactValue:    string;
  impactUnit:     string;
  secondaryValue: string;
  secondaryUnit:  string;
}

interface FormData {
  creationDatePeriod:    string;
  creationDateYear:      string;
  addToForecastByPeriod: string;
  addToForecastByYear:   string;
  division:              string;
  department:            string;
  country:               string;
  channel:               string;
  subChannel:            string;
  account:               string;
  brand:                 string;
  brandFamily:           string[];
  rAndO:                 string;
  probability:           string;
  categorisation:        string;
  impactPeriod:          string;
  impactYear:            string;
  impactValue:           string;
  primaryImpact:         string;
  secondaryValue:        string;
  secondaryUnit:         string;
  impactType:            string;
  owner:                 string;
  creator:               string;
  status:                string;
  shortDescription:      string;
  detailedDescription:   string;
  childImpacts:          ChildImpactForm[];
}

const props = defineProps<{ entry?: Entry | null }>();

// ─────────────────────────────────────────────────────────────────────────────
// Owner checkbox
// ─────────────────────────────────────────────────────────────────────────────
const ownerSameAsCreator = ref(true);
const isInitialLoadRef   = ref(true);

function onOwnerCheckboxChange(val: boolean) {
  if (val) formData.value.owner = formData.value.creator;
}

// ─────────────────────────────────────────────────────────────────────────────
// Period range state
// ─────────────────────────────────────────────────────────────────────────────
const usePeriodRange    = ref(false);
const periodRangeStart  = ref({ period: "", year: "" });
const periodRangeEnd    = ref({ period: "", year: "" });

// ─────────────────────────────────────────────────────────────────────────────
// Form ref & year options
// ─────────────────────────────────────────────────────────────────────────────
const formRef      = ref<FormInstance>();
const currentYear  = new Date().getFullYear();
const currentMonth = new Date().getMonth() + 1;
const currentPeriod = `F${String(currentMonth).padStart(2, "0")}`;
const yearOptions   = Array.from({ length: 10 }, (_, i) => currentYear - 2 + i);

const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];
function periodToMonth(period: string): string {
  if (!period) return period;
  const n = parseInt(period.replace("F", ""), 10);
  if (isNaN(n) || n < 1 || n > 12) return period;
  return monthNames[n - 1];
}

// ─────────────────────────────────────────────────────────────────────────────
// Default form
// ─────────────────────────────────────────────────────────────────────────────
function defaultForm(): FormData {
  const email = currentUserEmail.value;
  return {
    creationDatePeriod:    currentPeriod,
    creationDateYear:      String(currentYear),
    addToForecastByPeriod: currentPeriod,
    addToForecastByYear:   String(currentYear),
    division:       "",
    department:     "",
    country:        "",
    channel:        "",
    subChannel:     "",
    account:        "",
    brand:          "",
    brandFamily:    [],
    rAndO:          "Risk",
    probability:    "",
    categorisation: "",
    impactPeriod:   currentPeriod,
    impactYear:     String(currentYear),
    impactValue:    "",
    primaryImpact:  "AUD",
    secondaryValue: "",
    secondaryUnit:  "Volume",
    impactType:     "NSV",
    owner:          email,
    creator:        email,
    status:         "Open",
    shortDescription:   "",
    detailedDescription:"",
    childImpacts:   [],
  };
}

const formData = ref<FormData>(defaultForm());

const isLoadingEntry  = ref(false);
const hasChildImpacts = computed(() => formData.value.childImpacts.length > 0);

// ─────────────────────────────────────────────────────────────────────────────
// Unit helpers (country-aware, alcohol-aware)
// ─────────────────────────────────────────────────────────────────────────────
function getUnitOptions(country: string): string[] {
  if (country === "Australia")   return ["AUD", "Volume"];
  if (country === "New Zealand") return ["NZD", "Volume"];
  return ["AUD", "NZD", "Volume"];
}
const unitOptions = computed(() => getUnitOptions(formData.value.country));

const isAlcohol = computed(() => {
  const d = formData.value.division.toLowerCase();
  return d.includes("alcohol") && !d.includes("non-alcohol");
});

const unitLabels = computed<Record<string, string>>(() => ({
  AUD:    "NSV (AUD)",
  NZD:    "NSV (NZD)",
  Volume: isAlcohol.value ? "Vol. (9L)" : "Vol. (L)",
}));

function getImpactTypeLabel(impactType: string): string {
  const currency = formData.value.primaryImpact === "NZD" ? "NZD" : "AUD";
  const labels: Record<string, string> = {
    NSV:  `NSV (${currency})`,
    COGS: `COGS (${currency})`,
    LOGS: `LOGS (${currency})`,
    OI:   `OI (${currency})`,
  };
  return labels[impactType] || "Impact Value";
}

const currencyCode = computed(() =>
  formData.value.primaryImpact === "NZD" ? "NZD" :
  formData.value.primaryImpact === "AUD" ? "AUD" : ""
);

// ─────────────────────────────────────────────────────────────────────────────
// Totals (for child rows)
// ─────────────────────────────────────────────────────────────────────────────
const totalPrimaryImpact = computed(() => {
  const sum = formData.value.childImpacts.reduce((acc, ci) => {
    const n = parseFloat(cleanNumStr(ci.impactValue));
    return acc + (isNaN(n) ? 0 : n);
  }, 0);
  return sum.toString();
});

const totalSecondaryImpact = computed(() => {
  const sum = formData.value.childImpacts.reduce((acc, ci) => {
    const n = parseFloat(cleanNumStr(ci.secondaryValue));
    return acc + (isNaN(n) ? 0 : n);
  }, 0);
  return sum.toString();
});

const secondaryTotalVisible = computed(() =>
  formData.value.childImpacts.some(ci => ci.secondaryValue.trim())
);

const impactPeriodSummary = computed(() => {
  const valid = formData.value.childImpacts.filter(ci => ci.impactPeriod && ci.impactYear);
  if (!valid.length) return "";
  const sorted = [...valid].sort((a, b) => {
    const yd = parseInt(a.impactYear) - parseInt(b.impactYear);
    if (yd) return yd;
    return parseInt(a.impactPeriod.substring(1)) - parseInt(b.impactPeriod.substring(1));
  });
  return sorted.map(ci => `${periodToMonth(ci.impactPeriod)} ${ci.impactYear}`).join(", ");
});

// ─────────────────────────────────────────────────────────────────────────────
// Watchers
// ─────────────────────────────────────────────────────────────────────────────
watch(currentUserEmail, (email) => {
  if (email && !props.entry) {
    formData.value.creator = email;
    if (ownerSameAsCreator.value) formData.value.owner = email;
  }
});

watch(() => formData.value.country, (country) => {
  const opts = getUnitOptions(country);
  if (country === "New Zealand" && !opts.includes(formData.value.primaryImpact)) {
    formData.value.primaryImpact = "NZD";
  } else if (country === "Australia" && !opts.includes(formData.value.primaryImpact)) {
    formData.value.primaryImpact = "AUD";
  }
  if (!opts.includes(formData.value.primaryImpact)) formData.value.primaryImpact = opts[0];
  const secOpts = opts.filter(u => u !== formData.value.primaryImpact);
  if (!secOpts.includes(formData.value.secondaryUnit)) formData.value.secondaryUnit = secOpts[0] ?? "";
  formData.value.childImpacts.forEach(ci => {
    if (!opts.includes(ci.impactUnit)) ci.impactUnit = opts[0];
    const cs = opts.filter(u => u !== ci.impactUnit);
    if (!cs.includes(ci.secondaryUnit)) ci.secondaryUnit = cs[0] ?? "";
  });
});

watch(() => formData.value.primaryImpact, (newUnit, oldUnit) => {
  if (!oldUnit || newUnit === oldUnit || isLoadingEntry.value) return;
  const vals: Record<string, string> = {
    [oldUnit]: formData.value.impactValue,
    [formData.value.secondaryUnit]: formData.value.secondaryValue,
  };
  formData.value.impactValue = vals[newUnit] ?? "";
  const secOpts = unitOptions.value.filter(u => u !== newUnit);
  const newSecUnit = secOpts.includes(oldUnit) ? oldUnit : (secOpts[0] ?? "");
  formData.value.secondaryUnit  = newSecUnit;
  formData.value.secondaryValue = vals[newSecUnit] ?? "";
  formData.value.childImpacts.forEach(ci => {
    const ciVals: Record<string, string> = {
      [ci.impactUnit]: ci.impactValue,
      [ci.secondaryUnit]: ci.secondaryValue,
    };
    ci.impactUnit     = newUnit;
    ci.impactValue    = ciVals[newUnit] ?? "";
    ci.secondaryUnit  = newSecUnit;
    ci.secondaryValue = ciVals[newSecUnit] ?? "";
  });
});

watch(() => formData.value.secondaryUnit, (val) => {
  if (isLoadingEntry.value) return;
  formData.value.childImpacts.forEach(ci => { ci.secondaryUnit = val; });
});

watch(() => formData.value.channel, (val) => {
  if (!isLoadingEntry.value) {
    formData.value.subChannel = "";
    formData.value.account = "";
  }
  if (val) lookupStore.loadChildren("sub_channel", val);
});

watch(() => formData.value.subChannel, (val) => {
  if (!isLoadingEntry.value) formData.value.account = "";
  if (val) lookupStore.loadChildren("account", val);
});

watch(() => formData.value.brand, (val) => {
  if (!isLoadingEntry.value) formData.value.brandFamily = [];
  if (val) lookupStore.loadChildren("brand_family", val);
});

watch(() => formData.value.department, (val) => {
  if (isInitialLoadRef.value) return;
  if (!CATEG_ACTIVE_DEPTS.includes(val)) formData.value.categorisation = "";
  if (val === "Demand Review") {
    formData.value.impactType = "NSV";
  } else if (formData.value.impactType === "NSV") {
    formData.value.impactType = "OI";
  }
});

watch(() => formData.value.rAndO, (val) => {
  if (isInitialLoadRef.value) return;
  function applySign(v: string, shouldBeNeg: boolean): string {
    const n = parseFloat(cleanNumStr(v));
    if (isNaN(n)) return v;
    return shouldBeNeg ? (n > 0 ? String(-n) : v) : (n < 0 ? String(Math.abs(n)) : v);
  }
  const neg = val === "Risk";
  formData.value.impactValue = applySign(formData.value.impactValue, neg);
  formData.value.childImpacts.forEach(ci => { ci.impactValue = applySign(ci.impactValue, neg); });
});

watch(
  () => props.entry,
  async (entry) => {
    isLoadingEntry.value = true;
    if (entry) {
      isInitialLoadRef.value = true;
      const _d = (entry.division || "").toLowerCase();
      const entryIsAlcohol = _d.includes("alcohol") && !_d.includes("non-alcohol");
      const fromStorage = (unit: string, val: string): string => {
        if (!val || unit !== "Volume" || !entryIsAlcohol) return val;
        const n = parseFloat(val);
        return isNaN(n) ? val : String(n / 9);
      };

      let brandFamilyArray: string[] = [];
      if (entry.brandFamily) {
        if (Array.isArray(entry.brandFamily)) {
          brandFamilyArray = entry.brandFamily as unknown as string[];
        } else {
          try {
            const parsed = JSON.parse(entry.brandFamily as unknown as string);
            brandFamilyArray = Array.isArray(parsed) ? parsed : [entry.brandFamily as unknown as string];
          } catch {
            brandFamilyArray = [entry.brandFamily as unknown as string];
          }
        }
      }

      const creator = entry.creator || currentUserEmail.value;
      const owner   = entry.owner   || currentUserEmail.value;
      const shouldBeSame = owner === creator;
      ownerSameAsCreator.value = shouldBeSame;

      formData.value = {
        creationDatePeriod:    entry.creationDatePeriod    || currentPeriod,
        creationDateYear:      entry.creationDateYear      || String(currentYear),
        addToForecastByPeriod: entry.addToForecastByPeriod || currentPeriod,
        addToForecastByYear:   entry.addToForecastByYear   || String(currentYear),
        division:       entry.division      || "",
        department:     entry.department    || "",
        country:        entry.country       || "",
        channel:        entry.channel       || "",
        subChannel:     entry.subChannel    || "",
        account:        entry.account       || "",
        brand:          entry.brand         || "",
        brandFamily:    brandFamilyArray,
        rAndO:          entry.rAndO         || "Risk",
        probability:    entry.probability   || "",
        categorisation: entry.categorisation|| "",
        impactPeriod:   entry.impactPeriod  || "",
        impactYear:     entry.impactYear    || (entry.childImpacts?.length ? "" : String(currentYear)),
        primaryImpact:  entry.primaryImpact || "AUD",
        impactType:     entry.impactType    || "OI",
        impactValue: formatNumStr(
          entry.primaryImpact === "NZD" ? (entry.nsvNzd || "")
          : entry.primaryImpact === "Volume" ? fromStorage("Volume", entry.volumeLitres || "")
          : (entry.nsvAud || "")
        ),
        ...((): { secondaryUnit: string; secondaryValue: string } => {
          const pi = entry.primaryImpact || "AUD";
          const candidates = [
            { unit: "AUD",    val: entry.nsvAud    || "" },
            { unit: "NZD",    val: entry.nsvNzd    || "" },
            { unit: "Volume", val: fromStorage("Volume", entry.volumeLitres || "") },
          ].filter(c => c.unit !== pi);
          const found = candidates.find(c => c.val) ?? candidates[0];
          return { secondaryUnit: found.unit, secondaryValue: formatNumStr(found.val) };
        })(),
        owner:   owner,
        creator: entry.id === 0 ? (currentUserEmail.value || creator) : creator,
        status:  entry.status || "Open",
        shortDescription:    entry.shortDescription    || "",
        detailedDescription: entry.detailedDescription || "",
        childImpacts: (entry.childImpacts || []).map(ci => {
          const primary = entry.primaryImpact || "AUD";
          const secondaryCandidates = [
            { unit: "AUD",    val: ci.nsvAud    || "" },
            { unit: "NZD",    val: ci.nsvNzd    || "" },
            { unit: "Volume", val: fromStorage("Volume", ci.volumeLitres || "") },
          ].filter(c => c.unit !== primary);
          const sec = secondaryCandidates.find(c => c.val) ?? secondaryCandidates[0];
          return {
            impactYear:     ci.impactYear   || "",
            impactPeriod:   ci.impactPeriod || "",
            impactUnit:     primary,
            impactValue: formatNumStr(
              primary === "NZD" ? (ci.nsvNzd || "")
              : primary === "Volume" ? fromStorage("Volume", ci.volumeLitres || "")
              : (ci.nsvAud || "")
            ),
            secondaryUnit:  sec.unit,
            secondaryValue: formatNumStr(sec.val),
          };
        }),
      };
      await nextTick();
      isInitialLoadRef.value = false;
    } else {
      formData.value = defaultForm();
      ownerSameAsCreator.value = true;
      usePeriodRange.value = false;
      periodRangeStart.value = { period: "", year: "" };
      periodRangeEnd.value   = { period: "", year: "" };
    }
    isLoadingEntry.value = false;
  },
  { immediate: true }
);

// ─────────────────────────────────────────────────────────────────────────────
// Validation rules
// ─────────────────────────────────────────────────────────────────────────────
const rules: FormRules = {
  creationDatePeriod: [{ required: true, message: "Required", trigger: "change" }],
  creationDateYear:   [{ required: true, message: "Required", trigger: "change" }],
  division:           [{ required: true, message: "Required", trigger: "change" }],
  department:         [{ required: true, message: "Required", trigger: "change" }],
  country:            [{ required: true, message: "Required", trigger: "change" }],
  channel:            [{ required: true, message: "Required", trigger: "change" }],
  subChannel:         [{ required: true, message: "Required", trigger: "change" }],
  account:            [{ required: true, message: "Required", trigger: "blur"   }],
  brand:              [{ required: true, message: "Required", trigger: "change" }],
  brandFamily:        [{ required: true, message: "Required", trigger: "change" }],
  rAndO:              [{ required: true, message: "Required", trigger: "change" }],
  probability:        [{ required: true, message: "Required", trigger: "change" }],
  categorisation: [{
    validator: (_rule: unknown, value: string, callback: (e?: Error) => void) => {
      if (categActive.value && !value) callback(new Error("Required"));
      else callback();
    },
    trigger: "change",
  }],
  owner:            [{ required: true, message: "Required", trigger: "change" }],
  creator:          [{ required: true, message: "Required", trigger: "blur"   }],
  shortDescription: [{ required: true, message: "Required", trigger: "blur"   }],
};

// ─────────────────────────────────────────────────────────────────────────────
// Child impact helpers
// ─────────────────────────────────────────────────────────────────────────────
function addChild() {
  const isFirst = formData.value.childImpacts.length === 0;
  if (isFirst) {
    const count = 2;
    for (let i = 0; i < count; i++) {
      formData.value.childImpacts.push({
        impactYear:     String(currentYear),
        impactPeriod:   i === 0 ? (formData.value.impactPeriod || "") : "",
        impactValue:    i === 0 ? formData.value.impactValue : "",
        impactUnit:     formData.value.primaryImpact,
        secondaryValue: i === 0 ? formData.value.secondaryValue : "",
        secondaryUnit:  formData.value.secondaryUnit,
      });
    }
    formData.value.impactPeriod   = "";
    formData.value.impactYear     = "";
    formData.value.impactValue    = "";
    formData.value.secondaryValue = "";
  } else {
    formData.value.childImpacts.push({
      impactYear:     String(currentYear),
      impactPeriod:   "",
      impactValue:    "",
      impactUnit:     formData.value.primaryImpact,
      secondaryValue: "",
      secondaryUnit:  formData.value.secondaryUnit,
    });
  }
}

function removeChild(idx: number) {
  formData.value.childImpacts.splice(idx, 1);
  if (formData.value.childImpacts.length === 1) {
    const last = formData.value.childImpacts[0];
    formData.value.impactPeriod   = last.impactPeriod || currentPeriod;
    formData.value.impactYear     = last.impactYear   || String(currentYear);
    formData.value.impactValue    = last.impactValue;
    formData.value.secondaryValue = last.secondaryValue;
    formData.value.childImpacts   = [];
  } else if (formData.value.childImpacts.length === 0) {
    formData.value.impactPeriod = currentPeriod;
    formData.value.impactYear   = String(currentYear);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Period range helpers
// ─────────────────────────────────────────────────────────────────────────────
function isPeriodAfter(p1: string, y1: string, p2: string, y2: string): boolean {
  const Y1 = parseInt(y1), Y2 = parseInt(y2);
  if (Y1 > Y2) return true;
  if (Y1 < Y2) return false;
  return parseInt(p1.replace("F","")) > parseInt(p2.replace("F",""));
}
function isPeriodAfterOrEqual(p1: string, y1: string, p2: string, y2: string): boolean {
  const Y1 = parseInt(y1), Y2 = parseInt(y2);
  if (Y1 > Y2) return true;
  if (Y1 < Y2) return false;
  return parseInt(p1.replace("F","")) >= parseInt(p2.replace("F",""));
}
function generatePeriodRange(sp: string, sy: string, ep: string, ey: string) {
  const result: { period: string; year: string }[] = [];
  let cp = parseInt(sp.replace("F","")), cy = parseInt(sy);
  const endP = parseInt(ep.replace("F","")), endY = parseInt(ey);
  let safety = 0;
  while ((cy < endY || (cy === endY && cp <= endP)) && safety < 120) {
    result.push({ period: `F${String(cp).padStart(2,"0")}`, year: String(cy) });
    cp++; if (cp > 12) { cp = 1; cy++; }
    safety++;
  }
  return result;
}

function createChildImpactsFromRange() {
  const { period: sp, year: sy } = periodRangeStart.value;
  const { period: ep, year: ey } = periodRangeEnd.value;
  if (!sp || !sy || !ep || !ey) {
    ElMessage.error("Please select both start and end periods for the range");
    return;
  }
  if (!isPeriodAfterOrEqual(ep, ey, sp, sy)) {
    ElMessage.error("End period must be after or equal to start period");
    return;
  }
  if (!isPeriodAfter(sp, sy, formData.value.addToForecastByPeriod, formData.value.addToForecastByYear)) {
    ElMessage.error("Start period must be after Add to Forecast By period");
    return;
  }
  const periods = generatePeriodRange(sp, sy, ep, ey);
  if (!periods.length) { ElMessage.error("No periods in range"); return; }

  const totalPrimary   = parseFloat(cleanNumStr(formData.value.impactValue)) || 0;
  const totalSecondary = parseFloat(cleanNumStr(formData.value.secondaryValue)) || 0;

  formData.value.childImpacts = periods.map(({ period, year }) => ({
    impactYear:     year,
    impactPeriod:   period,
    impactValue:    String(totalPrimary / periods.length),
    impactUnit:     formData.value.primaryImpact,
    secondaryValue: String(totalSecondary / periods.length),
    secondaryUnit:  formData.value.secondaryUnit,
  }));

  formData.value.impactPeriod   = "";
  formData.value.impactValue    = "";
  formData.value.secondaryValue = "";
  usePeriodRange.value    = false;
  periodRangeStart.value  = { period: "", year: "" };
  periodRangeEnd.value    = { period: "", year: "" };
  ElMessage.success(`Created ${periods.length} child impacts with prorated values`);
}

// ─────────────────────────────────────────────────────────────────────────────
// Number formatting
// ─────────────────────────────────────────────────────────────────────────────
function cleanNumStr(val: string): string {
  let s = val.replace(/,/g, "").replace(/[^\d.]/g, "");
  const d = s.indexOf(".");
  if (d !== -1) s = s.slice(0, d + 1) + s.slice(d + 1).replace(/\./g, "");
  return s;
}
function formatNumStr(val: string): string {
  const s = cleanNumStr(val);
  if (!s) return "";
  const parts = s.split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return parts.join(".");
}
function isValidNum(val: string): boolean {
  const s = cleanNumStr(val).trim();
  return s !== "" && !isNaN(Number(s));
}

// ─────────────────────────────────────────────────────────────────────────────
// Storage mapping (9L conversion)
// ─────────────────────────────────────────────────────────────────────────────
function toStorage(unit: string, val: string): string {
  if (!val || unit !== "Volume" || !isAlcohol.value) return val;
  const n = parseFloat(val);
  return isNaN(n) ? val : String(n * 9);
}
function mapToFields(primaryUnit: string, primaryVal: string, secUnit: string, secVal: string) {
  const set = (unit: string) =>
    unit === primaryUnit ? toStorage(unit, primaryVal)
    : unit === secUnit   ? toStorage(unit, secVal)
    : "";
  return { nsvAud: set("AUD"), nsvNzd: set("NZD"), volumeLitres: set("Volume") };
}

// ─────────────────────────────────────────────────────────────────────────────
// Public API: validate / reset
// ─────────────────────────────────────────────────────────────────────────────
async function validate() {
  try {
    await formRef.value!.validate();

    if (hasChildImpacts.value) {
      for (let i = 0; i < formData.value.childImpacts.length; i++) {
        const ci = formData.value.childImpacts[i];
        if (!ci.impactPeriod)               { ElMessage.error(`Row ${i+1}: Impact Period is required.`);            return null; }
        if (!ci.impactYear)                  { ElMessage.error(`Row ${i+1}: Impact Year is required.`);              return null; }
        if (!ci.impactValue.trim())          { ElMessage.error(`Row ${i+1}: Primary Impact value is required.`);     return null; }
        if (!isValidNum(ci.impactValue))     { ElMessage.error(`Row ${i+1}: Primary Impact must be a valid number.`);return null; }
        if (ci.secondaryValue.trim() && !isValidNum(ci.secondaryValue)) {
          ElMessage.error(`Row ${i+1}: Secondary Impact must be a valid number.`);
          return null;
        }
        if (!isPeriodAfter(ci.impactPeriod, ci.impactYear, formData.value.addToForecastByPeriod, formData.value.addToForecastByYear)) {
          ElMessage.error(`Row ${i+1}: Impact Period must be after Add to Forecast By period`);
          return null;
        }
        ci.impactValue    = cleanNumStr(ci.impactValue);
        ci.secondaryValue = cleanNumStr(ci.secondaryValue);
      }
    } else {
      if (!formData.value.impactPeriod)             { ElMessage.error("Impact Period is required.");                 return null; }
      if (!formData.value.impactYear)               { ElMessage.error("Impact Year is required.");                   return null; }
      if (!formData.value.impactValue.trim())       { ElMessage.error("Primary Impact value is required.");          return null; }
      if (!isValidNum(formData.value.impactValue))  { ElMessage.error("Primary Impact must be a valid number.");     return null; }
      if (formData.value.secondaryValue.trim() && !isValidNum(formData.value.secondaryValue)) {
        ElMessage.error("Secondary Impact must be a valid number."); return null;
      }
      if (!isPeriodAfter(formData.value.impactPeriod, formData.value.impactYear, formData.value.addToForecastByPeriod, formData.value.addToForecastByYear)) {
        ElMessage.error("Primary Impact Period must be after Add to Forecast By period"); return null;
      }
      formData.value.impactValue    = cleanNumStr(formData.value.impactValue);
      formData.value.secondaryValue = cleanNumStr(formData.value.secondaryValue);
    }

    const { nsvAud, nsvNzd, volumeLitres } = mapToFields(
      formData.value.primaryImpact, formData.value.impactValue,
      formData.value.secondaryUnit,  formData.value.secondaryValue,
    );
    return {
      ...formData.value,
      nsvAud, nsvNzd, volumeLitres,
      childImpacts: formData.value.childImpacts.map(ci => {
        const m = mapToFields(ci.impactUnit, ci.impactValue, ci.secondaryUnit, ci.secondaryValue);
        return { impactYear: ci.impactYear, impactPeriod: ci.impactPeriod, ...m };
      }),
    };
  } catch {
    return null;
  }
}

function reset() {
  formData.value = defaultForm();
  ownerSameAsCreator.value = true;
  usePeriodRange.value = false;
  formRef.value?.clearValidate();
}

defineExpose({ validate, reset });
</script>

<style scoped>
/* ── Form header ────────────────────────────────────────────────────────── */
.entry-form-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-header {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.form-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0;
  color: var(--el-text-color-primary);
}

/* ── Layout helpers ─────────────────────────────────────────────────────── */
.period-pair {
  display: flex;
  gap: 8px;
  width: 100%;
}
.period-select { flex: 1; }
.year-select   { width: 110px; flex-shrink: 0; }

.owner-wrap { display: flex; flex-direction: column; }

.char-count {
  color: var(--el-text-color-secondary);
  font-weight: 400;
  font-size: 12px;
  margin-left: 6px;
}

/* ── Toggle buttons (Risk/Opportunity, Probability) ─────────────────────── */
.toggle-group {
  display: flex;
  gap: 0;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--el-border-color);
}
.toggle-btn {
  flex: 1;
  padding: 7px 14px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.toggle-btn + .toggle-btn {
  border-left: 1px solid var(--el-border-color);
}
.toggle-btn:hover { background: var(--el-fill-color-light); }
.toggle-btn.is-active {
  background: var(--el-color-primary);
  color: #fff;
}

/* ── Combobox ────────────────────────────────────────────────────────────── */
.combo-wrap { position: relative; width: 100%; }
.combo-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  box-shadow: var(--el-box-shadow-light);
  z-index: 9999;
  max-height: 240px;
  overflow-y: auto;
  padding: 4px 0;
}
.combo-item {
  padding: 7px 12px;
  font-size: 13px;
  cursor: pointer;
  color: var(--el-text-color-regular);
  transition: background 0.1s;
}
.combo-item:hover { background: var(--el-fill-color); }
.combo-item.is-disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.combo-custom {
  padding: 7px 12px;
  font-size: 13px;
  color: var(--el-color-primary);
  cursor: pointer;
}
.combo-custom:hover { background: var(--el-fill-color); }
.combo-empty {
  padding: 7px 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.combo-arrow {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

/* Brand Family specific */
.combo-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-height: 32px;
  padding: 0 11px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  background: var(--el-fill-color-blank);
  cursor: pointer;
  font-size: 14px;
  box-sizing: border-box;
}
.combo-trigger .has-value { color: var(--el-text-color-regular); }
.combo-trigger .placeholder { color: var(--el-text-color-placeholder); }
.brand-family-dropdown { padding: 8px 0; }
.bf-search { padding: 0 8px; margin-bottom: 6px; }
.combo-check-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.bf-section-label {
  padding: 4px 12px 2px;
  font-size: 11px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.bf-divider {
  height: 1px;
  background: var(--el-border-color-lighter);
  margin: 4px 0;
}
.bf-select-all {
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 2px;
}
.bf-select-all-label { font-weight: 600; }

/* ── Impact card ─────────────────────────────────────────────────────────── */
.impact-card {
  border: 1px solid var(--el-border-color);
  border-radius: 0.625rem;
  padding: 20px;
  margin-bottom: 12px;
  background: var(--el-fill-color-extra-light);
}

.impact-child-card {
  border: 1px solid var(--el-border-color);
  border-radius: 0.625rem;
  padding: 16px 20px;
  margin-bottom: 10px;
  background: var(--el-bg-color);
}

.impact-field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-regular);
}
.impact-required { color: #d4183d; }
.optional-tag {
  color: var(--el-text-color-secondary);
  font-weight: 400;
  font-size: 12px;
  margin-left: 4px;
}

.input-unit-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.unit-chip {
  min-width: 90px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  background: var(--el-fill-color-light);
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  white-space: nowrap;
  flex-shrink: 0;
}

.add-impact-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}

.child-remove-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

/* ── Totals bar ──────────────────────────────────────────────────────────── */
.totals-bar {
  display: flex;
  justify-content: flex-end;
  gap: 32px;
  padding: 12px 20px;
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: 4px;
}
.totals-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.totals-label { font-size: 13px; font-weight: 500; color: var(--el-text-color-regular); }
.totals-value { font-size: 16px; font-weight: 700; color: var(--el-text-color-primary); }

/* ── Locked impact ───────────────────────────────────────────────────────── */
.impact-locked {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 18px;
  border: 1px dashed var(--el-border-color);
  border-radius: 0.625rem;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  margin-bottom: 12px;
}

/* ── Period range ────────────────────────────────────────────────────────── */
.range-block { display: flex; flex-direction: column; gap: 2px; }
.range-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}
.period-range-check { margin-top: 8px; }

/* ── Spacing utilities ───────────────────────────────────────────────────── */
.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
</style>