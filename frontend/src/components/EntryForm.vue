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
      class="custom-form"
      require-asterisk-position="right"
    >
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Creator" prop="creator">
            <el-input v-model="formData.creator" disabled />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Creation Period" prop="creationDatePeriod">
            <div class="period-pair">
              <div class="combo-wrap period-select">
                <el-input
                  v-model="creationPeriodSearch"
                  :placeholder="formData.creationDatePeriod ? periodToMonth(formData.creationDatePeriod) : 'Select period'"
                  @focus="creationPeriodOpen = true"
                  @blur="onCreationPeriodBlur"
                  @input="creationPeriodOpen = true"
                  clearable
                  @clear="formData.creationDatePeriod = ''; creationPeriodSearch = ''"
                >
                  <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                </el-input>
                <div v-if="creationPeriodOpen" class="combo-dropdown">
                  <div v-for="p in filteredCreationPeriods" :key="p" class="combo-item" @mousedown.prevent="formData.creationDatePeriod = p; creationPeriodSearch = ''; creationPeriodOpen = false">{{ periodToMonth(p) }}</div>
                  <div v-if="filteredCreationPeriods.length === 0 && creationPeriodSearch" class="combo-custom" @mousedown.prevent="formData.creationDatePeriod = creationPeriodSearch; creationPeriodOpen = false">Use custom value: "{{ creationPeriodSearch }}"</div>
                </div>
              </div>

              <div class="combo-wrap year-select">
                <el-input
                  v-model="creationYearSearch"
                  :placeholder="formData.creationDateYear || 'Select year'"
                  @focus="creationYearOpen = true"
                  @blur="onCreationYearBlur"
                  @input="creationYearOpen = true"
                  clearable
                  @clear="formData.creationDateYear = ''; creationYearSearch = ''"
                >
                  <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                </el-input>
                <div v-if="creationYearOpen" class="combo-dropdown">
                  <div v-for="y in filteredCreationYears" :key="y" class="combo-item" @mousedown.prevent="formData.creationDateYear = y; creationYearSearch = ''; creationYearOpen = false">{{ y }}</div>
                  <div v-if="filteredCreationYears.length === 0 && creationYearSearch" class="combo-custom" @mousedown.prevent="formData.creationDateYear = creationYearSearch; creationYearOpen = false">Use custom value: "{{ creationYearSearch }}"</div>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Owner" prop="owner">
            <div class="owner-wrap">
              <el-checkbox v-model="ownerSameAsCreator" @change="onOwnerCheckboxChange" class="owner-checkbox">
                Same as Creator
              </el-checkbox>
              <el-select
                v-if="!ownerSameAsCreator"
                v-model="formData.owner"
                style="width: 100%; margin-top: 4px;"
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
        <el-col :span="12">
          <el-form-item label="Add to Forecast By" prop="addToForecastByPeriod">
            <div class="period-pair">
              <div class="combo-wrap period-select">
                <el-input
                  v-model="atfbPeriodSearch"
                  :placeholder="formData.addToForecastByPeriod || 'Select period'"
                  @focus="atfbPeriodOpen = true"
                  @blur="onAtfbPeriodBlur"
                  @input="atfbPeriodOpen = true"
                  clearable
                  @clear="formData.addToForecastByPeriod = ''; atfbPeriodSearch = ''"
                >
                  <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                </el-input>
                <div v-if="atfbPeriodOpen" class="combo-dropdown">
                  <div v-for="p in filteredAtfbPeriods" :key="p" class="combo-item" @mousedown.prevent="formData.addToForecastByPeriod = p; atfbPeriodSearch = ''; atfbPeriodOpen = false">{{ p }}</div>
                  <div v-if="filteredAtfbPeriods.length === 0 && atfbPeriodSearch" class="combo-custom" @mousedown.prevent="formData.addToForecastByPeriod = atfbPeriodSearch; atfbPeriodOpen = false">Use custom value: "{{ atfbPeriodSearch }}"</div>
                </div>
              </div>

              <div class="combo-wrap year-select">
                <el-input
                  v-model="atfbYearSearch"
                  :placeholder="formData.addToForecastByYear || 'Select year'"
                  @focus="atfbYearOpen = true"
                  @blur="onAtfbYearBlur"
                  @input="atfbYearOpen = true"
                  clearable
                  @clear="formData.addToForecastByYear = ''; atfbYearSearch = ''"
                >
                  <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                </el-input>
                <div v-if="atfbYearOpen" class="combo-dropdown">
                  <div v-for="y in filteredAtfbYears" :key="y" class="combo-item" @mousedown.prevent="formData.addToForecastByYear = y; atfbYearSearch = ''; atfbYearOpen = false">{{ y }}</div>
                  <div v-if="filteredAtfbYears.length === 0 && atfbYearSearch" class="combo-custom" @mousedown.prevent="formData.addToForecastByYear = atfbYearSearch; atfbYearOpen = false">Use custom value: "{{ atfbYearSearch }}"</div>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Department" prop="department">
            <div class="combo-wrap">
              <el-input
                v-model="deptSearch"
                :placeholder="formData.department || 'Select or enter department'"
                @focus="deptOpen = true"
                @blur="onDeptBlur"
                @input="deptOpen = true"
                clearable
                @clear="formData.department = ''; deptSearch = ''"
              >
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="deptOpen" class="combo-dropdown">
                <div v-for="d in filteredDepts" :key="d" class="combo-item" @mousedown.prevent="formData.department = d; deptSearch = ''; deptOpen = false">{{ d }}</div>
                <div v-if="filteredDepts.length === 0 && deptSearch" class="combo-custom" @mousedown.prevent="formData.department = deptSearch; deptOpen = false">Use custom value: "{{ deptSearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Division" prop="division">
            <div class="combo-wrap">
              <el-input
                v-model="divSearch"
                :placeholder="formData.division || 'Select or enter division'"
                @focus="divOpen = true"
                @blur="onDivBlur"
                @input="divOpen = true"
                clearable
                @clear="formData.division = ''; divSearch = ''"
              >
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="divOpen" class="combo-dropdown">
                <div v-for="d in filteredDivs" :key="d" class="combo-item" @mousedown.prevent="formData.division = d; divSearch = ''; divOpen = false">{{ d }}</div>
                <div v-if="filteredDivs.length === 0 && divSearch" class="combo-custom" @mousedown.prevent="formData.division = divSearch; divOpen = false">Use custom value: "{{ divSearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Country" prop="country">
            <div class="combo-wrap">
              <el-input
                v-model="countrySearch"
                :placeholder="formData.country || 'Select or enter country'"
                @focus="countryOpen = true"
                @blur="onCountryBlur"
                @input="countryOpen = true"
                clearable
                @clear="formData.country = ''; countrySearch = ''"
              >
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="countryOpen" class="combo-dropdown">
                <div v-for="c in filteredCountries" :key="c" class="combo-item" @mousedown.prevent="formData.country = c; countrySearch = ''; countryOpen = false">{{ c }}</div>
                <div v-if="filteredCountries.length === 0 && countrySearch" class="combo-custom" @mousedown.prevent="formData.country = countrySearch; countryOpen = false">Use custom value: "{{ countrySearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item
            label="Categorisation"
            prop="categorisation"
            :required="categActive"
          >
            <el-select
              v-model="formData.categorisation"
              style="width: 100%"
              :disabled="!categActive"
              :placeholder="categActive ? 'Select categorisation' : 'Only available for Marketing, Demand, Supply, or Overheads'"
            >
              <el-option v-for="c in categOptions" :key="c" :value="c" :label="c" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item prop="shortDescription">
            <template #label>
              Short Description <span class="char-count">({{ formData.shortDescription.length }}/100 characters)</span>
            </template>
            <el-input
              v-model="formData.shortDescription"
              placeholder="Enter a brief description (max 100 characters)..."
              maxlength="100"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="Detailed Description" prop="detailedDescription">
            <el-input
              v-model="formData.detailedDescription"
              type="textarea"
              :rows="3"
              placeholder="Enter a detailed description (optional)..."
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
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
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="channelOpen" class="combo-dropdown">
                <div v-for="c in filteredChannels" :key="c" class="combo-item" :class="{ 'is-disabled': isChannelDisabled(c) }" @mousedown.prevent="selectChannel(c)">{{ c }}</div>
                <div v-if="filteredChannels.length === 0 && channelSearch" class="combo-custom" @mousedown.prevent="formData.channel = channelSearch; channelOpen = false">Use custom value: "{{ channelSearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
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
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="brandOpen" class="combo-dropdown">
                <div v-for="b in filteredBrands" :key="b" class="combo-item" @mousedown.prevent="formData.brand = b; brandSearch = ''; brandOpen = false">{{ b }}</div>
                <div v-if="filteredBrands.length === 0 && brandSearch" class="combo-custom" @mousedown.prevent="formData.brand = brandSearch; brandOpen = false">Use custom value: "{{ brandSearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Sub Channel" prop="subChannel">
            <div class="combo-wrap">
              <el-input
                v-model="subChannelSearch"
                :placeholder="formData.subChannel || 'Select or enter subchannel'"
                @focus="subChannelOpen = true"
                @blur="onSubChannelBlur"
                @input="subChannelOpen = true"
                clearable
                @clear="formData.subChannel = ''; subChannelSearch = ''"
              >
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="subChannelOpen" class="combo-dropdown">
                <div v-for="s in filteredSubChannels" :key="s" class="combo-item" @mousedown.prevent="formData.subChannel = s; subChannelSearch = ''; subChannelOpen = false">{{ s }}</div>
                <div v-if="filteredSubChannels.length === 0 && subChannelSearch" class="combo-custom" @mousedown.prevent="formData.subChannel = subChannelSearch; subChannelOpen = false">Use custom value: "{{ subChannelSearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Brand Family" prop="brandFamily">
            <div class="combo-wrap" ref="brandFamilyRef">
              <div class="combo-trigger" @click="brandFamilyOpen = !brandFamilyOpen">
                <span :class="formData.brandFamily.length ? 'has-value' : 'placeholder'">
                  {{ formData.brandFamily.length ? formData.brandFamily.join(', ') : 'Select one or more brand families' }}
                </span>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </div>
              <div v-if="brandFamilyOpen" class="combo-dropdown brand-family-dropdown">
                <el-input v-model="brandFamilySearch" placeholder="Type to search or add custom..." class="bf-search" @keydown.enter.prevent="addCustomBrandFamily" />
                <div v-if="brandFamilySearch.trim() && !brandFamilyOptions.some(f => f.toLowerCase() === brandFamilySearch.toLowerCase())" class="combo-custom" @mousedown.prevent="addCustomBrandFamily">+ Add custom: "{{ brandFamilySearch }}"</div>
                <template v-if="formData.brandFamily.filter(f => !brandFamilyOptions.includes(f)).length">
                  <div class="bf-section-label">Custom Values</div>
                  <div v-for="f in formData.brandFamily.filter(fv => !brandFamilyOptions.includes(fv))" :key="f" class="combo-item combo-check-item" @mousedown.prevent="toggleBrandFamily(f)">
                    <el-checkbox :model-value="true" /><span>{{ f }}</span>
                  </div>
                  <div class="bf-divider" />
                </template>
                <div class="combo-item combo-check-item bf-select-all" @mousedown.prevent="toggleAllBrandFamilies">
                  <el-checkbox :model-value="allBrandFamiliesSelected" /><span class="bf-select-all-label">Select All Suggestions</span>
                </div>
                <div v-for="f in filteredBrandFamilies" :key="f" class="combo-item combo-check-item" @mousedown.prevent="toggleBrandFamily(f)">
                  <el-checkbox :model-value="formData.brandFamily.includes(f)" /><span>{{ f }}</span>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
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
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="accountOpen" class="combo-dropdown">
                <div v-for="a in filteredAccounts" :key="a" class="combo-item" @mousedown.prevent="formData.account = a; accountSearch = ''; accountOpen = false">{{ a }}</div>
                <div v-if="filteredAccounts.length === 0 && accountSearch" class="combo-custom" @mousedown.prevent="formData.account = accountSearch; accountOpen = false">Use custom value: "{{ accountSearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Risk vs. Opportunity" prop="rAndO">
            <div class="toggle-group">
              <button type="button" class="toggle-btn" :class="{ 'is-active': formData.rAndO === 'Risk' }" @click="formData.rAndO = 'Risk'">Risk</button>
              <button type="button" class="toggle-btn" :class="{ 'is-active': formData.rAndO === 'Opportunity' }" @click="formData.rAndO = 'Opportunity'">Opportunity</button>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Probability" prop="probability">
            <div class="toggle-group">
              <button v-for="p in probabilityOptions" :key="p" type="button" class="toggle-btn" :class="{ 'is-active': formData.probability === p }" @click="formData.probability = p">{{ p }}</button>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <div class="impact-section-header">
        <h4 class="section-title">Impact Details</h4>
      </div>

      <div v-if="!formData.country" class="impact-locked">
        <el-icon><InfoFilled /></el-icon>
        Please select a Country first to enable Impact Details.
      </div>

      <template v-else>
        <div class="impact-card" :class="{ 'has-children': hasChildImpacts }">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="Primary Impact Period">
                <el-input v-if="hasChildImpacts" :model-value="impactPeriodSummary || 'Add child impact periods'" disabled />
                
                <template v-else-if="usePeriodRange">
                  <div class="range-block">
                    <div class="period-range-check" style="margin-bottom: 12px;">
                      <el-checkbox v-model="usePeriodRange" @change="onCancelPeriodRange">Use Period Range</el-checkbox>
                    </div>

                    <div class="sub-label">Start Period</div>
                    <div class="period-pair mt-1">
                      <div class="combo-wrap period-select">
                        <el-input
                          v-model="prStartPeriodSearch"
                          :placeholder="periodRangeStart.period ? periodToMonth(periodRangeStart.period) : 'Select period'"
                          @focus="prStartPeriodOpen = true"
                          @blur="onPrStartPeriodBlur"
                          @input="prStartPeriodOpen = true"
                          clearable
                          @clear="periodRangeStart.period = ''; prStartPeriodSearch = ''"
                        >
                          <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                        </el-input>
                        <div v-if="prStartPeriodOpen" class="combo-dropdown">
                          <div v-for="p in filteredPrStartPeriods" :key="p" class="combo-item" @mousedown.prevent="periodRangeStart.period = p; prStartPeriodSearch = ''; prStartPeriodOpen = false">{{ periodToMonth(p) }}</div>
                        </div>
                      </div>

                      <div class="combo-wrap year-select">
                        <el-input
                          v-model="prStartYearSearch"
                          :placeholder="periodRangeStart.year || 'Select year'"
                          @focus="prStartYearOpen = true"
                          @blur="onPrStartYearBlur"
                          @input="prStartYearOpen = true"
                          clearable
                          @clear="periodRangeStart.year = ''; prStartYearSearch = ''"
                        >
                          <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                        </el-input>
                        <div v-if="prStartYearOpen" class="combo-dropdown">
                          <div v-for="y in filteredPrStartYears" :key="y" class="combo-item" @mousedown.prevent="periodRangeStart.year = y; prStartYearSearch = ''; prStartYearOpen = false">{{ y }}</div>
                        </div>
                      </div>
                    </div>
                    
                    <div class="sub-label mt-3">End Period</div>
                    <div class="period-pair mt-1">
                      <div class="combo-wrap period-select">
                        <el-input
                          v-model="prEndPeriodSearch"
                          :placeholder="periodRangeEnd.period ? periodToMonth(periodRangeEnd.period) : 'Select period'"
                          @focus="prEndPeriodOpen = true"
                          @blur="onPrEndPeriodBlur"
                          @input="prEndPeriodOpen = true"
                          clearable
                          @clear="periodRangeEnd.period = ''; prEndPeriodSearch = ''"
                        >
                          <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                        </el-input>
                        <div v-if="prEndPeriodOpen" class="combo-dropdown">
                          <div v-for="p in filteredPrEndPeriods" :key="p" class="combo-item" @mousedown.prevent="periodRangeEnd.period = p; prEndPeriodSearch = ''; prEndPeriodOpen = false">{{ periodToMonth(p) }}</div>
                        </div>
                      </div>

                      <div class="combo-wrap year-select">
                        <el-input
                          v-model="prEndYearSearch"
                          :placeholder="periodRangeEnd.year || 'Select year'"
                          @focus="prEndYearOpen = true"
                          @blur="onPrEndYearBlur"
                          @input="prEndYearOpen = true"
                          clearable
                          @clear="periodRangeEnd.year = ''; prEndYearSearch = ''"
                        >
                          <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                        </el-input>
                        <div v-if="prEndYearOpen" class="combo-dropdown">
                          <div v-for="y in filteredPrEndYears" :key="y" class="combo-item" @mousedown.prevent="periodRangeEnd.year = y; prEndYearSearch = ''; prEndYearOpen = false">{{ y }}</div>
                        </div>
                      </div>
                    </div>

                    <el-button
                      class="prorate-btn"
                      :disabled="!periodRangeStart.period || !periodRangeStart.year || !periodRangeEnd.period || !periodRangeEnd.year"
                      @click="createChildImpactsFromRange"
                    >Generate Prorated Impacts</el-button>
                  </div>
                </template>

                <template v-else>
                  <div class="period-pair">
                    <div class="combo-wrap period-select">
                      <el-input
                        v-model="impactPeriodSearch"
                        :placeholder="formData.impactPeriod ? periodToMonth(formData.impactPeriod) : 'Select period'"
                        :disabled="hasChildImpacts"
                        @focus="impactPeriodOpen = true"
                        @blur="onImpactPeriodBlur"
                        @input="impactPeriodOpen = true"
                        clearable
                        @clear="formData.impactPeriod = ''; impactPeriodSearch = ''"
                      >
                        <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                      </el-input>
                      <div v-if="impactPeriodOpen && !hasChildImpacts" class="combo-dropdown">
                        <div v-for="p in filteredImpactPeriods" :key="p" class="combo-item" @mousedown.prevent="formData.impactPeriod = p; impactPeriodSearch = ''; impactPeriodOpen = false">{{ periodToMonth(p) }}</div>
                      </div>
                    </div>

                    <div class="combo-wrap year-select">
                      <el-input
                        v-model="impactYearSearch"
                        :placeholder="formData.impactYear || 'Select year'"
                        :disabled="hasChildImpacts"
                        @focus="impactYearOpen = true"
                        @blur="onImpactYearBlur"
                        @input="impactYearOpen = true"
                        clearable
                        @clear="formData.impactYear = ''; impactYearSearch = ''"
                      >
                        <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                      </el-input>
                      <div v-if="impactYearOpen && !hasChildImpacts" class="combo-dropdown">
                        <div v-for="y in filteredImpactYears" :key="y" class="combo-item" @mousedown.prevent="formData.impactYear = y; impactYearSearch = ''; impactYearOpen = false">{{ y }}</div>
                      </div>
                    </div>
                  </div>
                  <div v-if="!hasChildImpacts" class="period-range-check mt-2">
                    <el-checkbox v-model="usePeriodRange">Use Period Range</el-checkbox>
                  </div>
                </template>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item label="Impact Type">
                <div class="toggle-group">
                  <button type="button" class="toggle-btn" :class="{ 'is-active': formData.primaryImpact !== 'Volume' && formData.impactType === 'NSV' }" @click="formData.impactType = 'NSV'">NSV</button>
                  <button type="button" class="toggle-btn" :class="{ 'is-active': formData.primaryImpact !== 'Volume' && formData.impactType === 'COGS' }" @click="formData.impactType = 'COGS'">COGS</button>
                  <button type="button" class="toggle-btn" :class="{ 'is-active': formData.primaryImpact !== 'Volume' && formData.impactType === 'LOGS' }" @click="formData.impactType = 'LOGS'">LOGS</button>
                  <button type="button" class="toggle-btn" :class="{ 'is-active': formData.impactType === 'OI' }" @click="formData.impactType = 'OI'">OI</button>
                </div>
              </el-form-item>

              <el-form-item class="mt-3">
                <template #label>{{ getImpactTypeLabel(formData.impactType) }}</template>
                <el-input
                  :model-value="formData.impactValue"
                  :disabled="hasChildImpacts"
                  placeholder="Enter impact value"
                  @input="formData.impactValue = cleanNumStr($event as string)"
                  @blur="formData.impactValue = formatNumStr(formData.impactValue)"
                  @focus="formData.impactValue = cleanNumStr(formData.impactValue)"
                />
              </el-form-item>

              <el-form-item v-if="['NSV', 'COGS'].includes(formData.impactType)" class="mt-3">
                <template #label>
                  Volume (Cases) <span v-if="formData.impactType === 'COGS'" class="optional-tag">(optional)</span>
                </template>
                <el-input
                  :model-value="formData.secondaryValue"
                  :disabled="hasChildImpacts"
                  placeholder="Enter volume in cases"
                  @input="formData.secondaryValue = cleanNumStr($event as string)"
                  @blur="formData.secondaryValue = formatNumStr(formData.secondaryValue)"
                  @focus="formData.secondaryValue = cleanNumStr(formData.secondaryValue)"
                />
              </el-form-item>
              
              <div class="add-impact-row">
                <el-button class="add-impact-btn" size="small" @click="addChild">
                  <el-icon><Plus /></el-icon> Add Impact
                </el-button>
              </div>
            </el-col>
          </el-row>
        </div>

        <div v-for="(child, idx) in formData.childImpacts" :key="idx" class="impact-child-card">
          <el-row :gutter="16" align="middle">
            <el-col :span="['NSV', 'COGS'].includes(formData.impactType) ? 6 : 8">
              <div class="sub-label">Period <span class="impact-required">*</span></div>
              <div class="combo-wrap" style="margin-top: 6px">
                <el-input
                  v-model="child._periodSearch"
                  :placeholder="child.impactPeriod ? periodToMonth(child.impactPeriod) : 'Select period'"
                  @focus="child._periodOpen = true"
                  @blur="onChildPeriodBlur(child)"
                  @input="child._periodOpen = true"
                  clearable
                  @clear="child.impactPeriod = ''; child._periodSearch = ''"
                >
                  <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                </el-input>
                <div v-if="child._periodOpen" class="combo-dropdown">
                  <div v-for="p in getFilteredChildPeriods(child._periodSearch)" :key="p" class="combo-item" @mousedown.prevent="child.impactPeriod = p; child._periodSearch = ''; child._periodOpen = false">{{ periodToMonth(p) }}</div>
                </div>
              </div>
            </el-col>
            <el-col :span="['NSV', 'COGS'].includes(formData.impactType) ? 6 : 8">
              <div class="sub-label">Year</div>
              <div class="combo-wrap" style="margin-top: 6px">
                <el-input
                  v-model="child._yearSearch"
                  :placeholder="child.impactYear || 'Select year'"
                  @focus="child._yearOpen = true"
                  @blur="onChildYearBlur(child)"
                  @input="child._yearOpen = true"
                  clearable
                  @clear="child.impactYear = ''; child._yearSearch = ''"
                >
                  <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                </el-input>
                <div v-if="child._yearOpen" class="combo-dropdown">
                  <div v-for="y in getFilteredChildYears(child._yearSearch)" :key="y" class="combo-item" @mousedown.prevent="child.impactYear = y; child._yearSearch = ''; child._yearOpen = false">{{ y }}</div>
                </div>
              </div>
            </el-col>
            <el-col :span="['NSV', 'COGS'].includes(formData.impactType) ? 6 : 8">
              <div class="sub-label">{{ getImpactTypeLabel(formData.impactType) }} <span class="impact-required">*</span></div>
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
              <div class="sub-label">
                Volume (Cases) <span v-if="formData.impactType === 'COGS'" class="optional-tag">(optional)</span>
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
            <el-button type="danger" link @click="removeChild(idx)"><el-icon><Delete /></el-icon> Remove</el-button>
          </div>
        </div>

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
const departmentOptions  = computed(() => lookupStore.getCached("department"));

const CATEG_ACTIVE_DEPTS = ["Portfolio Review", "Demand Review", "Supply Review", "Overheads (Pre-Exec)"];
const categActive = computed(() => CATEG_ACTIVE_DEPTS.includes(formData.value.department));

const supplyCategorisations    = ["Conversion (Wiri)", "Conversion (Swanbank)", "Co-Pack", "Agency", "Materials", "Stock", "Int/TT Freight", "Other"];
const overheadsCategorisations = ["People Costs", "Other People Costs", "Total People Costs", "Strategic Projects", "Vehicles", "Travel & Entertainment", "Communication", "Leases & Rentals", "Utilities", "Repairs & Maintenance", "Depreciation", "Printing & Stationery", "Administration", "Professional Fees", "IT Supplies", "Market Research", "3rd Party Merchandisers", "Insurance", "Group recharges / Sundry Income"];
const alcoholCategorisations   = ["Customer SOH", "Ranging", "Phasing", "Excise", "Rate", "Allocations"];
const baseCategorisations      = ["Baseline/Run Rates", "Brand Activations", "Deletions", "Long Term Forecast", "NPD", "New Business", "OOS", "Promotional Pricing", "Strategic/MTP/Trading Terms"];

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
// Combobox data (from lookupStore and static filters)
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
const brandOptions       = computed(() => lookupStore.getCached("brand"));
const brandFamilyOptions = computed(() =>
  formData.value.brand
    ? lookupStore.getCached("brand_family", formData.value.brand)
    : lookupStore.getCached("brand_family")
);

const channelOpen       = ref(false);
const channelSearch     = ref("");
const subChannelOpen    = ref(false);
const subChannelSearch  = ref("");
const brandOpen         = ref(false);
const brandSearch       = ref("");
const brandFamilyOpen   = ref(false);
const brandFamilySearch = ref("");
const accountOpen       = ref(false);
const accountSearch     = ref("");
const brandFamilyRef    = ref<HTMLElement | null>(null);

const deptOpen = ref(false);
const deptSearch = ref("");
const divOpen = ref(false);
const divSearch = ref("");
const countryOpen = ref(false);
const countrySearch = ref("");

const creationPeriodOpen = ref(false);
const creationPeriodSearch = ref("");
const creationYearOpen = ref(false);
const creationYearSearch = ref("");

const atfbPeriodOpen = ref(false);
const atfbPeriodSearch = ref("");
const atfbYearOpen = ref(false);
const atfbYearSearch = ref("");

// Range Start States
const prStartPeriodOpen = ref(false);
const prStartPeriodSearch = ref("");
const prStartYearOpen = ref(false);
const prStartYearSearch = ref("");

// Range End States
const prEndPeriodOpen = ref(false);
const prEndPeriodSearch = ref("");
const prEndYearOpen = ref(false);
const prEndYearSearch = ref("");

// Impact Single States
const impactPeriodOpen = ref(false);
const impactPeriodSearch = ref("");
const impactYearOpen = ref(false);
const impactYearSearch = ref("");

function handleBrandFamilyClickOutside(event: MouseEvent) {
  if (brandFamilyRef.value && !brandFamilyRef.value.contains(event.target as Node)) {
    brandFamilyOpen.value = false;
  }
}

const currentYear   = new Date().getFullYear();
const yearOptions   = Array.from({ length: 10 }, (_, i) => currentYear - 2 + i);

const filteredChannels      = computed(() => channelOptions.value.filter(c => c.toLowerCase().includes(channelSearch.value.toLowerCase())));
const filteredSubChannels   = computed(() => subChannelOptions.value.filter(s => s.toLowerCase().includes(subChannelSearch.value.toLowerCase())));
const filteredBrands        = computed(() => brandOptions.value.filter(b => b.toLowerCase().includes(brandSearch.value.toLowerCase())));
const filteredAccounts      = computed(() => accountOptions.value.filter(a => a.toLowerCase().includes(accountSearch.value.toLowerCase())));
const filteredBrandFamilies = computed(() => brandFamilyOptions.value.filter(f => f.toLowerCase().includes(brandFamilySearch.value.toLowerCase())));

const filteredDepts         = computed(() => departmentOptions.value.filter(d => d.toLowerCase().includes(deptSearch.value.toLowerCase())));
const filteredDivs          = computed(() => divisionOptions.value.filter(d => d.toLowerCase().includes(divSearch.value.toLowerCase())));
const filteredCountries     = computed(() => countryOptions.value.filter(c => c.toLowerCase().includes(countrySearch.value.toLowerCase())));
const filteredCreationPeriods = computed(() => PERIODS.filter(p => periodToMonth(p).toLowerCase().includes(creationPeriodSearch.value.toLowerCase()) || p.toLowerCase().includes(creationPeriodSearch.value.toLowerCase())));
const filteredCreationYears = computed(() => yearOptions.map(String).filter(y => y.includes(creationYearSearch.value)));
const filteredAtfbPeriods   = computed(() => PERIODS.filter(p => p.toLowerCase().includes(atfbPeriodSearch.value.toLowerCase())));
const filteredAtfbYears     = computed(() => yearOptions.map(String).filter(y => y.includes(atfbYearSearch.value)));

const filteredPrStartPeriods = computed(() => PERIODS.filter(p => periodToMonth(p).toLowerCase().includes(prStartPeriodSearch.value.toLowerCase()) || p.toLowerCase().includes(prStartPeriodSearch.value.toLowerCase())));
const filteredPrStartYears = computed(() => yearOptions.map(String).filter(y => y.includes(prStartYearSearch.value)));
const filteredPrEndPeriods = computed(() => PERIODS.filter(p => periodToMonth(p).toLowerCase().includes(prEndPeriodSearch.value.toLowerCase()) || p.toLowerCase().includes(prEndPeriodSearch.value.toLowerCase())));
const filteredPrEndYears = computed(() => yearOptions.map(String).filter(y => y.includes(prEndYearSearch.value)));
const filteredImpactPeriods = computed(() => PERIODS.filter(p => periodToMonth(p).toLowerCase().includes(impactPeriodSearch.value.toLowerCase()) || p.toLowerCase().includes(impactPeriodSearch.value.toLowerCase())));
const filteredImpactYears = computed(() => yearOptions.map(String).filter(y => y.includes(impactYearSearch.value)));

const getFilteredChildPeriods = (search?: string) => PERIODS.filter(p => periodToMonth(p).toLowerCase().includes((search || '').toLowerCase()) || p.toLowerCase().includes((search || '').toLowerCase()));
const getFilteredChildYears = (search?: string) => yearOptions.map(String).filter(y => y.includes(search || ''));

const allBrandFamiliesSelected = computed(() => brandFamilyOptions.value.length > 0 && brandFamilyOptions.value.every(f => formData.value.brandFamily.includes(f)));

function isChannelDisabled(ch: string) {
  if (formData.value.division === "Non-Alcohol") return ch === "Licensed" || ch === "Route";
  if (formData.value.division === "Alcohol")     return ch === "Convenience" || ch === "Grocery";
  return false;
}
function selectChannel(ch: string) {
  if (!isChannelDisabled(ch)) {
    formData.value.channel = ch; channelSearch.value = ""; channelOpen.value = false;
  }
}

function onChannelBlur()    { setTimeout(() => { channelOpen.value = false; }, 120); }
function onSubChannelBlur() { setTimeout(() => { subChannelOpen.value = false; }, 120); }
function onBrandBlur()      { setTimeout(() => { brandOpen.value = false; }, 120); }
function onAccountBlur()    { setTimeout(() => { accountOpen.value = false; }, 120); }
function onDeptBlur()       { setTimeout(() => { deptOpen.value = false; }, 120); }
function onDivBlur()        { setTimeout(() => { divOpen.value = false; }, 120); }
function onCountryBlur()    { setTimeout(() => { countryOpen.value = false; }, 120); }
function onCreationPeriodBlur() { setTimeout(() => { creationPeriodOpen.value = false; }, 120); }
function onCreationYearBlur()   { setTimeout(() => { creationYearOpen.value = false; }, 120); }
function onAtfbPeriodBlur()     { setTimeout(() => { atfbPeriodOpen.value = false; }, 120); }
function onAtfbYearBlur()       { setTimeout(() => { atfbYearOpen.value = false; }, 120); }

function onPrStartPeriodBlur() { setTimeout(() => { prStartPeriodOpen.value = false; }, 120); }
function onPrStartYearBlur()   { setTimeout(() => { prStartYearOpen.value = false; }, 120); }
function onPrEndPeriodBlur()   { setTimeout(() => { prEndPeriodOpen.value = false; }, 120); }
function onPrEndYearBlur()     { setTimeout(() => { prEndYearOpen.value = false; }, 120); }
function onImpactPeriodBlur()  { setTimeout(() => { impactPeriodOpen.value = false; }, 120); }
function onImpactYearBlur()    { setTimeout(() => { impactYearOpen.value = false; }, 120); }
function onChildPeriodBlur(child: ChildImpactForm) { setTimeout(() => { child._periodOpen = false; }, 120); }
function onChildYearBlur(child: ChildImpactForm)   { setTimeout(() => { child._yearOpen = false; }, 120); }

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
  _periodOpen?:   boolean;
  _periodSearch?: string;
  _yearOpen?:     boolean;
  _yearSearch?:   string;
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

const ownerSameAsCreator = ref(true);
const isInitialLoadRef   = ref(true);

function onOwnerCheckboxChange(val: boolean) {
  if (val) formData.value.owner = formData.value.creator;
}

const usePeriodRange   = ref(false); // DEFAULT SET TO FALSE HERE
const periodRangeStart = ref({ period: "", year: "" });
const periodRangeEnd   = ref({ period: "", year: "" });

function onCancelPeriodRange(val: boolean) {
  if (!val) {
    periodRangeStart.value = { period: "", year: "" };
    periodRangeEnd.value   = { period: "", year: "" };
  }
}

const formRef       = ref<FormInstance>();
const currentMonth  = new Date().getMonth() + 1;
const currentPeriod = `F${String(currentMonth).padStart(2, "0")}`;
const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];

function periodToMonth(period: string): string {
  if (!period) return period;
  const n = parseInt(period.replace("F", ""), 10);
  if (isNaN(n) || n < 1 || n > 12) return period;
  return monthNames[n - 1];
}

function defaultForm(): FormData {
  const email = currentUserEmail.value;
  return {
    creationDatePeriod:    currentPeriod,
    creationDateYear:      String(currentYear),
    addToForecastByPeriod: currentPeriod,
    addToForecastByYear:   String(currentYear),
    division:        "", department:      "", country:         "",
    channel:         "", subChannel:      "", account:         "",
    brand:           "", brandFamily:     [], rAndO:           "Risk",
    probability:     "", categorisation:  "", impactPeriod:    currentPeriod,
    impactYear:      String(currentYear), impactValue:     "", primaryImpact:   "AUD",
    secondaryValue:  "", secondaryUnit:   "Volume", impactType:      "NSV",
    owner:           email, creator:         email, status:          "Open",
    shortDescription:    "", detailedDescription: "", childImpacts:    [],
  };
}

const formData = ref<FormData>(defaultForm());
const isLoadingEntry  = ref(false);
const hasChildImpacts = computed(() => formData.value.childImpacts.length > 0);

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

function getImpactTypeLabel(impactType: string): string {
  const currency = formData.value.primaryImpact === "NZD" ? "NZD" : "AUD";
  const labels: Record<string, string> = { NSV: `NSV (${currency})`, COGS: `COGS (${currency})`, LOGS: `LOGS (${currency})`, OI: `OI (${currency})` };
  return labels[impactType] || "Impact Value";
}
const currencyCode = computed(() => formData.value.primaryImpact === "NZD" ? "NZD" : formData.value.primaryImpact === "AUD" ? "AUD" : "");

const totalPrimaryImpact = computed(() => {
  return formData.value.childImpacts.reduce((acc, ci) => {
    const n = parseFloat(cleanNumStr(ci.impactValue)); return acc + (isNaN(n) ? 0 : n);
  }, 0).toString();
});
const totalSecondaryImpact = computed(() => {
  return formData.value.childImpacts.reduce((acc, ci) => {
    const n = parseFloat(cleanNumStr(ci.secondaryValue)); return acc + (isNaN(n) ? 0 : n);
  }, 0).toString();
});
const secondaryTotalVisible = computed(() => formData.value.childImpacts.some(ci => ci.secondaryValue.trim()));
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

watch(currentUserEmail, (email) => {
  if (email && !props.entry) {
    formData.value.creator = email;
    if (ownerSameAsCreator.value) formData.value.owner = email;
  }
});

watch(() => formData.value.country, (country) => {
  const opts = getUnitOptions(country);
  if (country === "New Zealand" && !opts.includes(formData.value.primaryImpact)) formData.value.primaryImpact = "NZD";
  else if (country === "Australia" && !opts.includes(formData.value.primaryImpact)) formData.value.primaryImpact = "AUD";
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
  const vals: Record<string, string> = { [oldUnit]: formData.value.impactValue, [formData.value.secondaryUnit]: formData.value.secondaryValue };
  formData.value.impactValue = vals[newUnit] ?? "";
  const secOpts = unitOptions.value.filter(u => u !== newUnit);
  const newSecUnit = secOpts.includes(oldUnit) ? oldUnit : (secOpts[0] ?? "");
  formData.value.secondaryUnit  = newSecUnit; formData.value.secondaryValue = vals[newSecUnit] ?? "";
  formData.value.childImpacts.forEach(ci => {
    const ciVals: Record<string, string> = { [ci.impactUnit]: ci.impactValue, [ci.secondaryUnit]: ci.secondaryValue };
    ci.impactUnit = newUnit; ci.impactValue = ciVals[newUnit] ?? "";
    ci.secondaryUnit = newSecUnit; ci.secondaryValue = ciVals[newSecUnit] ?? "";
  });
});
watch(() => formData.value.secondaryUnit, (val) => { if (isLoadingEntry.value) return; formData.value.childImpacts.forEach(ci => { ci.secondaryUnit = val; }); });
watch(() => formData.value.channel, (val) => { if (!isLoadingEntry.value) { formData.value.subChannel = ""; formData.value.account = ""; } if (val) lookupStore.loadChildren("sub_channel", val); });
watch(() => formData.value.subChannel, (val) => { if (!isLoadingEntry.value) formData.value.account = ""; if (val) lookupStore.loadChildren("account", val); });
watch(() => formData.value.brand, (val) => { if (!isLoadingEntry.value) formData.value.brandFamily = []; if (val) lookupStore.loadChildren("brand_family", val); });
watch(() => formData.value.department, (val) => {
  if (isInitialLoadRef.value) return;
  if (!CATEG_ACTIVE_DEPTS.includes(val)) formData.value.categorisation = "";
  if (val === "Demand Review") formData.value.impactType = "NSV";
  else if (formData.value.impactType === "NSV") formData.value.impactType = "OI";
});
watch(() => formData.value.rAndO, (val) => {
  if (isInitialLoadRef.value) return;
  function applySign(v: string, shouldBeNeg: boolean): string {
    const n = parseFloat(cleanNumStr(v));
    if (isNaN(n)) return v; return shouldBeNeg ? (n > 0 ? String(-n) : v) : (n < 0 ? String(Math.abs(n)) : v);
  }
  const neg = val === "Risk";
  formData.value.impactValue = applySign(formData.value.impactValue, neg);
  formData.value.childImpacts.forEach(ci => { ci.impactValue = applySign(ci.impactValue, neg); });
});

watch(() => props.entry, async (entry) => {
  isLoadingEntry.value = true;
  if (entry) {
    isInitialLoadRef.value = true;
    const _d = (entry.division || "").toLowerCase();
    const entryIsAlcohol = _d.includes("alcohol") && !_d.includes("non-alcohol");
    const fromStorage = (unit: string, val: string): string => {
      if (!val || unit !== "Volume" || !entryIsAlcohol) return val;
      const n = parseFloat(val); return isNaN(n) ? val : String(n / 9);
    };

    let brandFamilyArray: string[] = [];
    if (entry.brandFamily) {
      if (Array.isArray(entry.brandFamily)) brandFamilyArray = entry.brandFamily as unknown as string[];
      else {
        try {
          const parsed = JSON.parse(entry.brandFamily as unknown as string);
          brandFamilyArray = Array.isArray(parsed) ? parsed : [entry.brandFamily as unknown as string];
        } catch { brandFamilyArray = [entry.brandFamily as unknown as string]; }
      }
    }

    const creator = entry.creator || currentUserEmail.value;
    const owner   = entry.owner   || currentUserEmail.value;
    ownerSameAsCreator.value = owner === creator;

    formData.value = {
      creationDatePeriod:    entry.creationDatePeriod    || currentPeriod,
      creationDateYear:      entry.creationDateYear      || String(currentYear),
      addToForecastByPeriod: entry.addToForecastByPeriod || currentPeriod,
      addToForecastByYear:   entry.addToForecastByYear   || String(currentYear),
      division:       entry.division      || "", department:      entry.department    || "",
      country:        entry.country       || "", channel:         entry.channel       || "",
      subChannel:     entry.subChannel    || "", account:         entry.account       || "",
      brand:          entry.brand         || "", brandFamily:     brandFamilyArray,
      rAndO:          entry.rAndO         || "Risk", probability:     entry.probability   || "",
      categorisation: entry.categorisation|| "", impactPeriod:   entry.impactPeriod  || "",
      impactYear:     entry.impactYear    || (entry.childImpacts?.length ? "" : String(currentYear)),
      primaryImpact:  entry.primaryImpact || "AUD", impactType:     entry.impactType    || "OI",
      impactValue: formatNumStr(entry.primaryImpact === "NZD" ? (entry.nsvNzd || "") : entry.primaryImpact === "Volume" ? fromStorage("Volume", entry.volumeLitres || "") : (entry.nsvAud || "")),
      ...((): { secondaryUnit: string; secondaryValue: string } => {
        const pi = entry.primaryImpact || "AUD";
        const candidates = [
          { unit: "AUD", val: entry.nsvAud || "" }, { unit: "NZD", val: entry.nsvNzd || "" }, { unit: "Volume", val: fromStorage("Volume", entry.volumeLitres || "") },
        ].filter(c => c.unit !== pi);
        const found = candidates.find(c => c.val) ?? candidates[0];
        return { secondaryUnit: found.unit, secondaryValue: formatNumStr(found.val) };
      })(),
      owner:   owner, creator: entry.id === 0 ? (currentUserEmail.value || creator) : creator,
      status:  entry.status || "Open", shortDescription: entry.shortDescription || "", detailedDescription: entry.detailedDescription || "",
      childImpacts: (entry.childImpacts || []).map(ci => {
        const primary = entry.primaryImpact || "AUD";
        const secondaryCandidates = [
          { unit: "AUD", val: ci.nsvAud || "" }, { unit: "NZD", val: ci.nsvNzd || "" }, { unit: "Volume", val: fromStorage("Volume", ci.volumeLitres || "") },
        ].filter(c => c.unit !== primary);
        const sec = secondaryCandidates.find(c => c.val) ?? secondaryCandidates[0];
        return {
          impactYear: ci.impactYear || "", impactPeriod: ci.impactPeriod || "", impactUnit: primary,
          impactValue: formatNumStr(primary === "NZD" ? (ci.nsvNzd || "") : primary === "Volume" ? fromStorage("Volume", ci.volumeLitres || "") : (ci.nsvAud || "")),
          secondaryUnit:  sec.unit, secondaryValue: formatNumStr(sec.val),
          _periodOpen: false, _periodSearch: "", _yearOpen: false, _yearSearch: ""
        };
      }),
    };
    await nextTick();
    isInitialLoadRef.value = false;
  } else {
    formData.value = defaultForm();
    ownerSameAsCreator.value = true;
    usePeriodRange.value     = false; // CHANGED HERE TO DEFAULT FALSE
    periodRangeStart.value   = { period: "", year: "" };
    periodRangeEnd.value     = { period: "", year: "" };
  }
  isLoadingEntry.value = false;
}, { immediate: true });

const rules: FormRules = {
  creationDatePeriod: [{ required: true, message: "Required", trigger: "change" }], creationDateYear: [{ required: true, message: "Required", trigger: "change" }],
  division: [{ required: true, message: "Required", trigger: "change" }], department: [{ required: true, message: "Required", trigger: "change" }],
  country: [{ required: true, message: "Required", trigger: "change" }], channel: [{ required: true, message: "Required", trigger: "change" }],
  subChannel: [{ required: true, message: "Required", trigger: "change" }], account: [{ required: true, message: "Required", trigger: "blur" }],
  brand: [{ required: true, message: "Required", trigger: "change" }], brandFamily: [{ required: true, message: "Required", trigger: "change" }],
  rAndO: [{ required: true, message: "Required", trigger: "change" }], probability: [{ required: true, message: "Required", trigger: "change" }],
  categorisation: [{ validator: (_rule: unknown, value: string, callback: (e?: Error) => void) => { if (categActive.value && !value) callback(new Error("Required")); else callback(); }, trigger: "change", }],
  owner: [{ required: true, message: "Required", trigger: "change" }], creator: [{ required: true, message: "Required", trigger: "blur" }],
  shortDescription: [{ required: true, message: "Required", trigger: "blur" }],
};

function addChild() {
  const isFirst = formData.value.childImpacts.length === 0;
  if (isFirst) {
    const count = 2;
    for (let i = 0; i < count; i++) {
      formData.value.childImpacts.push({
        impactYear: String(currentYear), impactPeriod: i === 0 ? (formData.value.impactPeriod || "") : "",
        impactValue: i === 0 ? formData.value.impactValue : "", impactUnit: formData.value.primaryImpact,
        secondaryValue: i === 0 ? formData.value.secondaryValue : "", secondaryUnit: formData.value.secondaryUnit,
        _periodOpen: false, _periodSearch: "", _yearOpen: false, _yearSearch: ""
      });
    }
    formData.value.impactPeriod = ""; formData.value.impactYear = ""; formData.value.impactValue = ""; formData.value.secondaryValue = "";
  } else {
    formData.value.childImpacts.push({
      impactYear: String(currentYear), impactPeriod: "", impactValue: "", impactUnit: formData.value.primaryImpact,
      secondaryValue: "", secondaryUnit: formData.value.secondaryUnit,
      _periodOpen: false, _periodSearch: "", _yearOpen: false, _yearSearch: ""
    });
  }
}

function removeChild(idx: number) {
  formData.value.childImpacts.splice(idx, 1);
  if (formData.value.childImpacts.length === 1) {
    const last = formData.value.childImpacts[0];
    formData.value.impactPeriod = last.impactPeriod || currentPeriod; formData.value.impactYear = last.impactYear || String(currentYear);
    formData.value.impactValue = last.impactValue; formData.value.secondaryValue = last.secondaryValue;
    formData.value.childImpacts = [];
  } else if (formData.value.childImpacts.length === 0) {
    formData.value.impactPeriod = currentPeriod; formData.value.impactYear = String(currentYear);
  }
}

function isPeriodAfter(p1: string, y1: string, p2: string, y2: string): boolean {
  const Y1 = parseInt(y1), Y2 = parseInt(y2);
  if (Y1 > Y2) return true; if (Y1 < Y2) return false;
  return parseInt(p1.replace("F","")) > parseInt(p2.replace("F",""));
}
function isPeriodAfterOrEqual(p1: string, y1: string, p2: string, y2: string): boolean {
  const Y1 = parseInt(y1), Y2 = parseInt(y2);
  if (Y1 > Y2) return true; if (Y1 < Y2) return false;
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
  const { period: sp, year: sy } = periodRangeStart.value; const { period: ep, year: ey } = periodRangeEnd.value;
  if (!sp || !sy || !ep || !ey) { ElMessage.error("Please select both start and end periods for the range"); return; }
  if (!isPeriodAfterOrEqual(ep, ey, sp, sy)) { ElMessage.error("End period must be after or equal to start period"); return; }
  if (!isPeriodAfter(sp, sy, formData.value.addToForecastByPeriod, formData.value.addToForecastByYear)) { ElMessage.error("Start period must be after Add to Forecast By period"); return; }
  const periods = generatePeriodRange(sp, sy, ep, ey);
  if (!periods.length) { ElMessage.error("No periods in range"); return; }
  const totalPrimary = parseFloat(cleanNumStr(formData.value.impactValue)) || 0; const totalSecondary = parseFloat(cleanNumStr(formData.value.secondaryValue)) || 0;
  formData.value.childImpacts = periods.map(({ period, year }) => ({
    impactYear: year, impactPeriod: period, impactValue: String(totalPrimary / periods.length), impactUnit: formData.value.primaryImpact,
    secondaryValue: String(totalSecondary / periods.length), secondaryUnit: formData.value.secondaryUnit,
    _periodOpen: false, _periodSearch: "", _yearOpen: false, _yearSearch: ""
  }));
  formData.value.impactPeriod = ""; formData.value.impactValue = ""; formData.value.secondaryValue = "";
  usePeriodRange.value = false; periodRangeStart.value = { period: "", year: "" }; periodRangeEnd.value = { period: "", year: "" };
  ElMessage.success(`Created ${periods.length} child impacts with prorated values`);
}

function cleanNumStr(val: string): string {
  let s = val.replace(/,/g, "").replace(/[^\d.]/g, ""); const d = s.indexOf(".");
  if (d !== -1) s = s.slice(0, d + 1) + s.slice(d + 1).replace(/\./g, ""); return s;
}
function formatNumStr(val: string): string {
  const s = cleanNumStr(val); if (!s) return ""; const parts = s.split(".");
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ","); return parts.join(".");
}
function isValidNum(val: string): boolean {
  const s = cleanNumStr(val).trim(); return s !== "" && !isNaN(Number(s));
}

function toStorage(unit: string, val: string): string {
  if (!val || unit !== "Volume" || !isAlcohol.value) return val;
  const n = parseFloat(val); return isNaN(n) ? val : String(n * 9);
}
function mapToFields(primaryUnit: string, primaryVal: string, secUnit: string, secVal: string) {
  const set = (unit: string) => unit === primaryUnit ? toStorage(unit, primaryVal) : unit === secUnit ? toStorage(unit, secVal) : "";
  return { nsvAud: set("AUD"), nsvNzd: set("NZD"), volumeLitres: set("Volume") };
}

async function validate() {
  try {
    await formRef.value!.validate();
    if (hasChildImpacts.value) {
      for (let i = 0; i < formData.value.childImpacts.length; i++) {
        const ci = formData.value.childImpacts[i];
        if (!ci.impactPeriod) { ElMessage.error(`Row ${i+1}: Impact Period is required.`); return null; }
        if (!ci.impactYear) { ElMessage.error(`Row ${i+1}: Impact Year is required.`); return null; }
        if (!ci.impactValue.trim()) { ElMessage.error(`Row ${i+1}: Primary Impact value is required.`); return null; }
        if (!isValidNum(ci.impactValue)) { ElMessage.error(`Row ${i+1}: Primary Impact must be a valid number.`); return null; }
        if (ci.secondaryValue.trim() && !isValidNum(ci.secondaryValue)) { ElMessage.error(`Row ${i+1}: Secondary Impact must be a valid number.`); return null; }
        if (!isPeriodAfter(ci.impactPeriod, ci.impactYear, formData.value.addToForecastByPeriod, formData.value.addToForecastByYear)) { ElMessage.error(`Row ${i+1}: Impact Period must be after Add to Forecast By period`); return null; }
        ci.impactValue = cleanNumStr(ci.impactValue); ci.secondaryValue = cleanNumStr(ci.secondaryValue);
      }
    } else {
      if (!formData.value.impactPeriod && !usePeriodRange.value) { ElMessage.error("Impact Period is required."); return null; }
      if (!formData.value.impactYear && !usePeriodRange.value) { ElMessage.error("Impact Year is required."); return null; }
      if (!formData.value.impactValue.trim()) { ElMessage.error("Primary Impact value is required."); return null; }
      if (!isValidNum(formData.value.impactValue)) { ElMessage.error("Primary Impact must be a valid number."); return null; }
      if (formData.value.secondaryValue.trim() && !isValidNum(formData.value.secondaryValue)) { ElMessage.error("Secondary Impact must be a valid number."); return null; }
      if (!usePeriodRange.value && !isPeriodAfter(formData.value.impactPeriod, formData.value.impactYear, formData.value.addToForecastByPeriod, formData.value.addToForecastByYear)) { ElMessage.error("Primary Impact Period must be after Add to Forecast By period"); return null; }
      formData.value.impactValue = cleanNumStr(formData.value.impactValue); formData.value.secondaryValue = cleanNumStr(formData.value.secondaryValue);
    }
    const { nsvAud, nsvNzd, volumeLitres } = mapToFields(formData.value.primaryImpact, formData.value.impactValue, formData.value.secondaryUnit, formData.value.secondaryValue);
    return {
      ...formData.value, nsvAud, nsvNzd, volumeLitres,
      childImpacts: formData.value.childImpacts.map(ci => {
        const m = mapToFields(ci.impactUnit, ci.impactValue, ci.secondaryUnit, ci.secondaryValue); return { impactYear: ci.impactYear, impactPeriod: ci.impactPeriod, ...m };
      }),
    };
  } catch { return null; }
}

function reset() {
  formData.value = defaultForm(); ownerSameAsCreator.value = true;
  usePeriodRange.value = false; // CHANGED HERE TO DEFAULT FALSE
  periodRangeStart.value = { period: "", year: "" }; periodRangeEnd.value = { period: "", year: "" };
  formRef.value?.clearValidate();
}

defineExpose({ validate, reset });
</script>

<style scoped>
/* ── Typography & Header ────────────────────────────────────────────────────────── */
.entry-form-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
  background-color: #fff;
}

.form-header {
  padding-bottom: 24px;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  margin: 0;
  color: #1a1a1a;
}

.section-title {
  font-size: 15px;
  font-weight: 700;
  color: #1a1a1a;
  margin: 16px 0;
}

/* ── Custom Form Styles (Flat UI Look) ─────────────────────────────────────────────────────── */
:deep(.el-form-item__label) {
  font-weight: 600;
  font-size: 13px;
  color: #1a1a1a;
  padding-bottom: 4px;
  line-height: 1.2;
}

/* Input Fields overrides */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select .el-input__wrapper) {
  background-color: #f4f5f7;
  border: 1px solid transparent;
  box-shadow: none !important;
  border-radius: 6px;
  transition: all 0.2s ease;
}
:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover),
:deep(.el-select .el-input__wrapper:hover) {
  background-color: #ededf0;
}
:deep(.el-input__wrapper.is-focus),
:deep(.el-textarea__inner:focus),
:deep(.el-select .el-input__wrapper.is-focus) {
  background-color: #fff;
  border: 1px solid #1a1a1a;
}
:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f9f9f9;
  color: #a8a8a8;
}

.char-count {
  font-weight: 400;
  color: #8c8c8c;
  font-size: 12px;
  margin-left: 6px;
}
.optional-tag {
  color: #8c8c8c;
  font-weight: 400;
  font-size: 12px;
  margin-left: 4px;
}
.impact-required {
  color: #d4183d;
}

/* ── Layout Helpers ─────────────────────────────────────────────────────── */
.period-pair {
  display: flex;
  gap: 12px;
  width: 100%;
}
.period-select { flex: 1; }
.year-select   { width: 120px; flex-shrink: 0; flex: 1;}
.owner-wrap { display: flex; flex-direction: column; }
.owner-checkbox { margin-top: -8px; margin-bottom: 4px; }
.sub-label {
  font-size: 12px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

/* ── Toggles (Segmented Control style) ─────────────────────── */
.toggle-group {
  display: flex;
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  background-color: #fff;
}
.toggle-btn {
  flex: 1;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  border-right: 1px solid #e0e0e0;
  background: transparent;
  color: #555;
  cursor: pointer;
  transition: all 0.2s;
}
.toggle-btn:last-child {
  border-right: none;
}
.toggle-btn:hover {
  background: #f4f5f7;
}
.toggle-btn.is-active {
  background: #0e1015; /* Dark almost black color */
  color: #fff;
}

/* ── Custom Combobox UI ────────────────────────────────────────────────────────────── */
.combo-wrap { position: relative; width: 100%; }
.combo-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 9999;
  max-height: 240px;
  overflow-y: auto;
  padding: 8px 0;
}
.combo-item {
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
  color: #333;
}
.combo-item:hover { background: #f4f5f7; }
.combo-item.is-disabled { opacity: 0.4; cursor: not-allowed; }
.combo-custom {
  padding: 8px 14px;
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
}
.combo-custom:hover { background: #f4f5f7; }
.combo-arrow { color: #8c8c8c; font-size: 12px; }

/* Brand Family Multi Select */
.combo-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* width: 100%; */
  min-height: 36px;
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: #f4f5f7;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}
.combo-trigger:hover { background: #ededf0; }
.combo-trigger .has-value { color: #1a1a1a; }
.combo-trigger .placeholder { color: #a8a8a8; }
.brand-family-dropdown { padding: 12px 0; }
.bf-search { padding: 0 12px; margin-bottom: 8px; }
.combo-check-item { display: flex; align-items: center; gap: 10px; }
.bf-section-label { padding: 6px 14px 4px; font-size: 11px; font-weight: 700; color: #8c8c8c; text-transform: uppercase; letter-spacing: 0.05em; }
.bf-divider { height: 1px; background: #e0e0e0; margin: 6px 0; }
.bf-select-all { border-bottom: 1px solid #e0e0e0; margin-bottom: 4px; padding-bottom: 10px; }
.bf-select-all-label { font-weight: 700; }

/* ── Impact Section ─────────────────────────────────────────────────────────── */
.impact-locked {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px;
  border: 1px dashed #dcdfe6;
  border-radius: 8px;
  color: #8c8c8c;
  font-size: 13px;
  margin-bottom: 16px;
}
.impact-card {
  margin-bottom: 16px;
}

.range-block { display: flex; flex-direction: column; }
.prorate-btn {
  width: 100%;
  background-color: #727285; /* Soft grey/purple like image */
  border-color: #727285;
  color: #fff;
  height: 40px;
  font-weight: 600;
  margin-top: 24px;
  border-radius: 6px;
}
.prorate-btn:hover:not(:disabled) {
  background-color: #5c5c6d;
  border-color: #5c5c6d;
}

.add-impact-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.add-impact-btn {
  border-radius: 6px;
  font-weight: 600;
}

.impact-child-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 12px;
  background: #f9f9fb;
}
.child-remove-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
}

.totals-bar {
  display: flex;
  justify-content: flex-end;
  gap: 32px;
  padding: 16px 0;
  border-top: 1px solid #e0e0e0;
  margin-top: 8px;
}
.totals-item { display: flex; align-items: center; gap: 8px; }
.totals-label { font-size: 13px; font-weight: 600; color: #555; }
.totals-value { font-size: 18px; font-weight: 700; color: #1a1a1a; }

/* ── Submit Action Button ─────────────────────────────────────────────────── */
.submit-action-btn {
  width: 100%;
  height: 52px;
  background-color: #0e1015; /* Pure black block matching the screenshot */
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  border: none;
  border-radius: 6px;
  margin-top: 32px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.submit-action-btn:hover {
  background-color: #2a2d35;
}

/* Spacing Utils */
.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
</style>