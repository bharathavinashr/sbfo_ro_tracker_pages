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
                  :class="{ 'has-selected-value': !!formData.creationDatePeriod && !creationPeriodSearch }"
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
                  :class="{ 'has-selected-value': !!formData.creationDateYear && !creationYearSearch }"
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
              <div v-if="!ownerSameAsCreator" class="combo-wrap" style="margin-top: 4px;">
                <el-input
                  v-model="ownerSearch"
                  :placeholder="formData.owner || 'Select owner'"
                  :class="{ 'has-selected-value': !!formData.owner && !ownerSearch }"
                  @focus="ownerOpen = true"
                  @blur="onOwnerBlur"
                  @input="ownerOpen = true"
                  clearable
                  @clear="formData.owner = ''; ownerSearch = ''"
                >
                  <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
                </el-input>
                <div v-if="ownerOpen" class="combo-dropdown">
                  <div v-for="u in filteredOwners" :key="u.email" class="combo-item" @mousedown.prevent="formData.owner = u.email; ownerSearch = ''; ownerOpen = false">
                    {{ u.display_name ? `${u.display_name} (${u.email})` : u.email }}
                  </div>
                </div>
              </div>
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
                  :class="{ 'has-selected-value': !!formData.addToForecastByPeriod && !atfbPeriodSearch }"
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
                  :class="{ 'has-selected-value': !!formData.addToForecastByYear && !atfbYearSearch }"
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
          <el-form-item label="IBP Step" prop="ibpStep">
            <div class="combo-wrap">
              <el-input
                v-model="ibpStepSearch"
                :placeholder="formData.ibpStep || 'Select IBP Step'"
                :class="{ 'has-selected-value': !!formData.ibpStep && !ibpStepSearch }"
                @focus="deptOpen = true"
                @blur="onDeptBlur"
                @input="deptOpen = true"
                clearable
                @clear="formData.ibpStep = ''; ibpStepSearch = ''"
              >
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="deptOpen" class="combo-dropdown">
                <div v-for="d in filteredIbpSteps" :key="d" class="combo-item" @mousedown.prevent="formData.ibpStep = d; ibpStepSearch = ''; deptOpen = false">{{ d }}</div>
                <div v-if="filteredIbpSteps.length === 0 && ibpStepSearch" class="combo-custom" @mousedown.prevent="formData.ibpStep = ibpStepSearch; deptOpen = false">Use custom value: "{{ ibpStepSearch }}"</div>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Division" prop="division">
            <div class="combo-wrap">
              <el-input
                v-model="divSearch"
                :placeholder="formData.division || 'Select division'"
                :class="{ 'has-selected-value': !!formData.division && !divSearch }"
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
                :placeholder="Object.keys(formData.country).length ? Object.values(formData.country)[0] : 'Select country'"
                :class="{ 'has-selected-value': Object.keys(formData.country).length > 0 && !countrySearch }"
                @focus="countryOpen = true"
                @blur="onCountryBlur"
                @input="countryOpen = true"
                clearable
                @clear="formData.country = {}; countrySearch = ''"
              >
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="countryOpen" class="combo-dropdown">
                <div v-for="c in filteredCountries" :key="c.value" class="combo-item" @mousedown.prevent="formData.country = { [c.value]: c.label }; countrySearch = ''; countryOpen = false">{{ c.label }}</div>
                <div v-if="filteredCountries.length === 0 && countrySearch" class="combo-custom" @mousedown.prevent="formData.country = { [countrySearch]: countrySearch }; countryOpen = false">Use custom value: "{{ countrySearch }}"</div>
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
            <div class="combo-wrap" :title="!categActive ? categDisabledMessage : ''">
              <el-input
                v-model="categSearch"
                :placeholder="formData.categorisation || (categActive ? 'Select categorisation' : 'Select categorisation')"
                :disabled="!categActive"
                :class="{ 'has-selected-value': !!formData.categorisation && !categSearch }"
                @focus="categOpen = true"
                @blur="onCategBlur"
                @input="categOpen = true"
                clearable
                @clear="formData.categorisation = ''; categSearch = ''"
              >
                <template #suffix><el-icon class="combo-arrow"><ArrowDown /></el-icon></template>
              </el-input>
              <div v-if="categOpen && categActive" class="combo-dropdown">
                <div v-for="c in filteredCategs" :key="c" class="combo-item" @mousedown.prevent="formData.categorisation = c; categSearch = ''; categOpen = false">{{ c }}</div>
                <div v-if="filteredCategs.length === 0 && categSearch" class="combo-custom" @mousedown.prevent="formData.categorisation = categSearch; categOpen = false">Use custom value: "{{ categSearch }}"</div>
              </div>
            </div>
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
          <el-form-item label="Channel" prop="channel" ref="channelRef">
            <div class="combo-wrap" ref="channelRef" v-click-outside="handleChannelClickOutside" :class="{ 'is-disabled': !countryDivisionActive }" :title="!countryDivisionActive ? channelDisabledMessage : ''" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
              <div class="combo-trigger" @click="countryDivisionActive && (channelOpen = !channelOpen)" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
                <span :class="Object.keys(formData.channel).length ? 'has-value' : 'placeholder'">
                  {{ Object.keys(formData.channel).length ? Object.values(formData.channel).join(', ') : 'Select one or more channels' }}
                </span>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </div>
              <div v-if="channelOpen && countryDivisionActive" class="combo-dropdown brand-family-dropdown">
                <el-input v-model="channelSearch" placeholder="Type to search..." class="bf-search" />
                <div class="combo-item combo-check-item bf-select-all" @mousedown.prevent="toggleAllChannels">
                  <el-checkbox :model-value="allChannelsSelected" />
                  <span class="bf-select-all-label">Select All Suggestions</span>
                </div>
                <div v-for="c in filteredChannels" :key="c.value" class="combo-item combo-check-item" :class="{ 'is-disabled': isChannelDisabled(c.label) }" @mousedown.prevent="toggleChannel(c.value, c.label)">
                  <el-checkbox :model-value="!!formData.channel[c.value]" /><span>{{ c.label }}</span>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Brand" prop="brand" ref="brandRef">
            <div class="combo-wrap" ref="brandRef" v-click-outside="handleBrandClickOutside" :class="{ 'is-disabled': !countryDivisionActive }" :title="!countryDivisionActive ? channelSubChannelAccountBrandMessage : ''">
              <div class="combo-trigger" @click="countryDivisionActive && (brandOpen = !brandOpen)" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
                <span :class="Object.keys(formData.brand).length ? 'has-value' : 'placeholder'">
                  {{ Object.keys(formData.brand).length ? Object.values(formData.brand).join(', ') : 'Select one or more brands' }}
                </span>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </div>
              <div v-if="brandOpen && countryDivisionActive" class="combo-dropdown brand-family-dropdown">
                <el-input v-model="brandSearch" placeholder="Type to search..." class="bf-search" />
                <div class="combo-item combo-check-item bf-select-all" @mousedown.prevent="toggleAllBrands">
                  <el-checkbox :model-value="allBrandsSelected" /><span class="bf-select-all-label">Select All Suggestions</span>
                </div>
                <div v-for="b in filteredBrands" :key="b.value" class="combo-item combo-check-item" @mousedown.prevent="toggleBrand(b.value, b.label)">
                  <el-checkbox :model-value="!!formData.brand[b.value]" /><span>{{ b.label }}</span>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Sub Channel" prop="subChannel" ref="subChannelRef">
            <div class="combo-wrap" ref="subChannelRef" v-click-outside="handleSubChannelClickOutside" :class="{ 'is-disabled': !countryDivisionActive }" :title="!countryDivisionActive ? channelSubChannelAccountBrandMessage : ''" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
              <div class="combo-trigger" @click="countryDivisionActive && (subChannelOpen = !subChannelOpen)" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
                <span :class="Object.keys(formData.subChannel).length ? 'has-value' : 'placeholder'">
                  {{ Object.keys(formData.subChannel).length ? Object.values(formData.subChannel).join(', ') : 'Select one or more sub-channels' }}
                </span>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </div>
              <div v-if="subChannelOpen && countryDivisionActive" class="combo-dropdown brand-family-dropdown">
                <el-input v-model="subChannelSearch" placeholder="Type to search..." class="bf-search" />
                <div class="combo-item combo-check-item bf-select-all" @mousedown.prevent="toggleAllSubChannels">
                  <el-checkbox :model-value="allSubChannelsSelected" />
                  <span class="bf-select-all-label">Select All Suggestions</span>
                </div>
                <div v-for="s in filteredSubChannels" :key="s.value" class="combo-item combo-check-item" @mousedown.prevent="toggleSubChannel(s.value, s.label)">
                  <el-checkbox :model-value="!!formData.subChannel[s.value]" /><span>{{ s.label }}</span>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Brand Family" prop="brandFamily" ref="brandFamilyRef">
            <div class="combo-wrap" ref="brandFamilyRef" v-click-outside="handleBrandFamilyClickOutside" :class="{ 'is-disabled': !countryDivisionActive }" :title="!countryDivisionActive ? channelSubChannelAccountBrandMessage : ''">
              <div class="combo-trigger" @click="countryDivisionActive && (brandFamilyOpen = !brandFamilyOpen)" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
                <span :class="Object.keys(formData.brandFamily).length ? 'has-value' : 'placeholder'">
                  {{ Object.keys(formData.brandFamily).length ? Object.values(formData.brandFamily).join(', ') : 'Select one or more brand families' }}
                </span>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </div>
              <div v-if="brandFamilyOpen && countryDivisionActive" class="combo-dropdown brand-family-dropdown">
                <el-input v-model="brandFamilySearch" placeholder="Type to search or add custom..." class="bf-search" @keydown.enter.prevent="addCustomBrandFamily" />
                <div v-if="brandFamilySearch.trim() && !brandFamilyOptions.some(f => f.label.toLowerCase() === brandFamilySearch.toLowerCase())" class="combo-custom" @mousedown.prevent="addCustomBrandFamily">+ Add custom: "{{ brandFamilySearch }}"</div>
                <template v-if="Object.keys(formData.brandFamily).filter(k => !brandFamilyOptions.some(opt => opt.value === k)).length">
                  <div class="bf-section-label">Custom Values</div>
                  <template v-for="(name, code) in formData.brandFamily" :key="code">
                    <div v-if="!brandFamilyOptions.some(opt => opt.value === code)" class="combo-item combo-check-item" @mousedown.prevent="toggleBrandFamily(code, name)">
                      <el-checkbox :model-value="true" /><span>{{ name }}</span>
                    </div>
                  </template>
                  <div class="bf-divider" />
                </template>
                <div class="combo-item combo-check-item bf-select-all" @mousedown.prevent="toggleAllBrandFamilies">
                  <el-checkbox :model-value="allBrandFamiliesSelected" /><span class="bf-select-all-label">Select All Suggestions</span>
                </div>
                <div v-for="f in filteredBrandFamilies" :key="f.value" class="combo-item combo-check-item" @mousedown.prevent="toggleBrandFamily(f.value, f.label)">
                  <el-checkbox :model-value="!!formData.brandFamily[f.value]" /><span>{{ f.label }}</span>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="Account" prop="account" ref="accountRef">
            <div class="combo-wrap" ref="accountRef" v-click-outside="handleAccountClickOutside" :class="{ 'is-disabled': !countryDivisionActive }" :title="!countryDivisionActive ? channelSubChannelAccountBrandMessage : ''" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
              <div class="combo-trigger" @click="countryDivisionActive && (accountOpen = !accountOpen)" :style="{ opacity: countryDivisionActive ? 1 : 0.6, cursor: countryDivisionActive ? 'pointer' : 'not-allowed' }">
                <span :class="Object.keys(formData.account).length ? 'has-value' : 'placeholder'">
                  {{ Object.keys(formData.account).length ? Object.values(formData.account).join(', ') : 'Select one or more accounts' }}
                </span>
                <el-icon class="combo-arrow"><ArrowDown /></el-icon>
              </div>
              <div v-if="accountOpen && countryDivisionActive" class="combo-dropdown brand-family-dropdown">
                <el-input v-model="accountSearch" placeholder="Type to search..." class="bf-search" />
                <div class="combo-item combo-check-item bf-select-all" @mousedown.prevent="toggleAllAccounts">
                  <el-checkbox :model-value="allAccountsSelected" />
                  <span class="bf-select-all-label">Select All Suggestions</span>
                </div>
                <div v-for="a in filteredAccounts" :key="a.value" class="combo-item combo-check-item" @mousedown.prevent="handleAccountToggle(a.value, a.label)">
                  <el-checkbox :model-value="!!formData.account[a.value]" /><span>{{ a.label }}</span>
                </div>
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

      <div v-if="Object.keys(formData.country).length === 0" class="impact-locked">
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
                          :class="{ 'has-selected-value': !!periodRangeStart.period && !prStartPeriodSearch }"
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
                          :class="{ 'has-selected-value': !!periodRangeStart.year && !prStartYearSearch }"
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
                          :class="{ 'has-selected-value': !!periodRangeEnd.period && !prEndPeriodSearch }"
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
                          :class="{ 'has-selected-value': !!periodRangeEnd.year && !prEndYearSearch }"
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
                    >Generate Monthly Impacts</el-button>
                  </div>
                </template>

                <template v-else>
                  <div class="period-pair">
                    <div class="combo-wrap period-select">
                      <el-input
                        v-model="impactPeriodSearch"
                        :placeholder="formData.impactPeriod ? periodToMonth(formData.impactPeriod) : 'Select period'"
                        :class="{ 'has-selected-value': !!formData.impactPeriod && !impactPeriodSearch }"
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
                        :class="{ 'has-selected-value': !!formData.impactYear && !impactYearSearch }"
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
              
              <div class="impact-section-subtitle">Financial Impact</div>
              <el-form-item class="mt-2">
                <template #label>{{ getfinancialImpactTypeLabel(formData.financialImpactType) }}</template>
                <div class="input-with-dropdown">
                  <el-input
                    :model-value="formData.impactValue"
                    :disabled="hasChildImpacts"
                    placeholder="Enter financial impact value"
                    @input="formData.impactValue = cleanNumStr($event as string)"
                    @blur="formData.impactValue = formatNumStr(formData.impactValue)"
                    @focus="formData.impactValue = cleanNumStr(formData.impactValue)"
                  />
                  <el-dropdown trigger="click" @command="formData.financialImpactType = $event">
                    <el-button type="primary" class="black-dropdown-btn">
                      {{ formData.financialImpactType }}
                      <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="NSV">NSV</el-dropdown-item>
                        <el-dropdown-item command="COGS">COGS</el-dropdown-item>
                        <el-dropdown-item command="LOGS">LOGS</el-dropdown-item>
                        <el-dropdown-item command="GP">GP</el-dropdown-item>
                        <el-dropdown-item command="OI">OI</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </el-form-item>

              <div class="impact-section-subtitle mt-4">Volume Impact</div>
              <el-form-item class="mt-2">
                <template #label>Volume ({{ formData.volumeImpactType }})</template>
                <div class="input-with-dropdown">
                  <el-input
                    :model-value="formData.secondaryValue"
                    :disabled="hasChildImpacts"
                    placeholder="Enter volume"
                    @input="formData.secondaryValue = cleanNumStr($event as string)"
                    @blur="formData.secondaryValue = formatNumStr(formData.secondaryValue)"
                    @focus="formData.secondaryValue = cleanNumStr(formData.secondaryValue)"
                  />
                  <el-dropdown trigger="click" @command="formData.volumeImpactType = $event">
                    <el-button type="primary" class="black-dropdown-btn">
                      {{ formData.volumeImpactType }}
                      <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="Cases">Cases</el-dropdown-item>
                        <el-dropdown-item command="9LE">9LE</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
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
            <el-col :span="6">
              <div class="sub-label">Period <span class="impact-required">*</span></div>
              <div class="combo-wrap" style="margin-top: 6px">
                <el-input
                  v-model="child._periodSearch"
                  :placeholder="child.impactPeriod ? periodToMonth(child.impactPeriod) : 'Select period'"
                  :class="{ 'has-selected-value': !!child.impactPeriod && !child._periodSearch }"
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
            <el-col :span="6">
              <div class="sub-label">Year</div>
              <div class="combo-wrap" style="margin-top: 6px">
                <el-input
                  v-model="child._yearSearch"
                  :placeholder="child.impactYear || 'Select year'"
                  :class="{ 'has-selected-value': !!child.impactYear && !child._yearSearch }"
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
            <el-col :span="6">
              <div class="sub-label">{{ getfinancialImpactTypeLabel(formData.financialImpactType) }} <span class="impact-required">*</span></div>
              <el-input
                :model-value="child.impactValue"
                placeholder="Enter value"
                style="margin-top: 6px"
                @input="child.impactValue = cleanNumStr($event as string)"
                @blur="child.impactValue = formatNumStr(child.impactValue)"
                @focus="child.impactValue = cleanNumStr(child.impactValue)"
              />
            </el-col>
            <el-col :span="6">
              <div class="sub-label">
                Volume ({{ formData.volumeImpactType }})
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
            <span class="totals-label">Total {{ getfinancialImpactTypeLabel(formData.financialImpactType) }}</span>
            <span class="totals-value">{{ formatNumStr(totalPrimaryImpact) }} {{ currencyCode }}</span>
          </div>
          <div v-if="secondaryTotalVisible" class="totals-item">
            <span class="totals-label">Total Volume ({{ formData.volumeImpactType }})</span>
            <span class="totals-value">{{ formatNumStr(totalSecondaryImpact) }}</span>
          </div>
        </div>
      </template>

      </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted, nextTick } from "vue";
import { Delete, InfoFilled, ArrowDown, Plus } from "@element-plus/icons-vue";
import { ElMessage, ClickOutside as vClickOutside } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import type { Entry } from "@/types";
import { PERIODS } from "@/types";
import { useLookupStore } from "@/stores/lookupStore";
import { useEntryStore } from "@/stores/entryStore";
import { lookupApi } from "@/services/api";

// ─────────────────────────────────────────────────────────────────────────────
// Stores & user info
// ─────────────────────────────────────────────────────────────────────────────
const lookupStore = useLookupStore();
const entryStore  = useEntryStore();

const currentUserEmail = computed(() => entryStore.currentUser?.email ?? "");
const ownerOptions = computed(() =>
  entryStore.users.filter((u) => u.role === 0 || u.role === 1)
);

// Product-based lookup data (from API)
const divisionOptions = ref<string[]>([]);
const countryOptions  = ref<{value: string, label: string}[]>([]);
const brandOptions = ref<{value: string, label: string}[]>([]);
const brandFamilyOptions = ref<{value: string, label: string}[]>([]);

// ─── Data Parsing Helpers ──────────────────────────────────────────────────
function ensureObject(v: any): Record<string, string> {
  if (!v) return {};
  if (typeof v === 'object' && !Array.isArray(v)) return v;
  try {
    const p = JSON.parse(v);
    return (p && typeof p === 'object' && !Array.isArray(p)) ? p : {};
  } catch { return {}; }
}

function ensureValues(v: any): string[] {
  if (!v) return [];
  if (Array.isArray(v)) return v;
  if (typeof v === 'object') return Object.values(v);
  try {
    const p = JSON.parse(v);
    if (Array.isArray(p)) return p;
    if (p && typeof p === 'object') return Object.values(p);
  } catch {}
  return [String(v)];
}
// ─────────────────────────────────────────────────────────────────────────────

onMounted(async () => {
  await lookupStore.preload();
  if (entryStore.users.length === 0) await entryStore.fetchUsers();

  // Load divisions
  try {
    const data = await lookupApi.getDivisions();
    divisionOptions.value = data.options.map(o => o.value);
  } catch (error) {
    console.error("Error loading divisions:", error);
  }

  const rawCountryData = (entryStore.currentUser as any)?.country;
  const userCountryData = ensureObject(rawCountryData); 

  if (Object.keys(userCountryData).length > 0) {
    countryOptions.value = Object.entries(userCountryData).map(([value, label]) => ({ value, label: label as string }));
  } else {
    const accessibleDivs = userDivisions.value;
    if (accessibleDivs.length > 0) {
      try {
        const allResults = await Promise.all(accessibleDivs.map(d => lookupApi.getCountries(d)));
        const merged = new Map<string, string>();
        allResults.forEach(res => {
          res.options.forEach(o => merged.set(String(o.value), o.label));
        });
        countryOptions.value = Array.from(merged.entries()).map(([value, label]) => ({ value, label }));
      } catch (e) {
        console.error("Error pre-fetching all countries:", e);
      }
    }
  }

  if (!props.entry) {
    if (userIbpSteps.value.length === 1) {
      formData.value.ibpStep = userIbpSteps.value[0];
    }
    if (userDivisions.value.length === 1) {
      formData.value.division = userDivisions.value[0];
    }
    const availableCountries = availableCountryOptions.value;
    if (availableCountries.length === 1) {
      formData.value.country = { [availableCountries[0].value]: availableCountries[0].label };
    }
  }
});

// ─────────────────────────────────────────────────────────────────────────────
// Lookup options (from store)
// ─────────────────────────────────────────────────────────────────────────────
const ibpStepOptions     = computed(() => lookupStore.getCached("ibp_step"));
const probabilityOptions = computed(() => lookupStore.getCached("probability"));

const CATEG_ACTIVE_IBP_STEPS = ["Portfolio Review", "Demand Review", "Supply Review", "Overheads (Pre-Exec)"];
const categActive = computed(() => CATEG_ACTIVE_IBP_STEPS.includes(formData.value.ibpStep));

const countryDivisionActive = computed(() => Object.keys(formData.value.country).length > 0 && !!formData.value.division);
const channelDisabledMessage = computed(() => {
  if (Object.keys(formData.value.country).length > 0 && !formData.value.division) {
    return "Please select Division";
  }
  return "Please select Country and Division";
});
const channelSubChannelAccountBrandMessage = "Please select Country and Division";
const categDisabledMessage = "Please select IBP Step";

const supplyCategorisations    = ["Conversion (Wiri)", "Conversion (Swanbank)", "Co-Pack", "Agency", "Materials", "Stock", "Int/TT Freight", "Other"];
const overheadsCategorisations = ["People Costs", "Other People Costs", "Total People Costs", "Strategic Projects", "Vehicles", "Travel & Entertainment", "Communication", "Leases & Rentals", "Utilities", "Repairs & Maintenance", "Depreciation", "Printing & Stationery", "Administration", "Professional Fees", "IT Supplies", "Market Research", "3rd Party Merchandisers", "Insurance", "Group recharges / Sundry Income"];
const alcoholCategorisations   = ["Customer SOH", "Ranging", "Phasing", "Excise", "Rate", "Allocations"];
const baseCategorisations      = ["Baseline/Run Rates", "Brand Activations", "Deletions", "Long Term Forecast", "NPD", "New Business", "OOS", "Promotional Pricing", "Strategic/MTP/Trading Terms"];

const categOptions = computed(() => {
  if (formData.value.ibpStep === "Supply Review") return supplyCategorisations;
  if (formData.value.ibpStep === "Overheads (Pre-Exec)") return overheadsCategorisations;
  if (
    formData.value.division === "Alcohol" &&
    (formData.value.ibpStep === "Portfolio Review" || formData.value.ibpStep === "Demand Review")
  ) return [...baseCategorisations, ...alcoholCategorisations];
  return baseCategorisations;
});

// ─────────────────────────────────────────────────────────────────────────────
// Combobox data (from lookupStore and API)
// ─────────────────────────────────────────────────────────────────────────────
const channelOptions    = ref<{value: string, label: string}[]>([]);
const subChannelOptions = ref<{value: string, label: string}[]>([]);
const accountOptions    = ref<{value: string, label: string}[]>([]);

const channelRef        = ref<HTMLElement | null>(null);
const subChannelRef     = ref<HTMLElement | null>(null);
const accountRef        = ref<HTMLElement | null>(null);
const brandSearch       = ref("");
const brandFamilyOpen   = ref(false);
const brandFamilySearch = ref("");
const accountOpen       = ref(false);
const channelOpen       = ref(false);
const channelSearch     = ref("");
const subChannelOpen    = ref(false);
const subChannelSearch  = ref("");
const brandOpen         = ref(false);
const accountSearch     = ref("");
const brandFamilyRef    = ref<HTMLElement | null>(null);
const brandRef          = ref<HTMLElement | null>(null);

const deptOpen = ref(false);
const selectionPriority = ref<'channel' | 'account' | null>(null);
const brandSelectionPriority = ref<'brand' | 'brandFamily' | null>(null);
const isReverseAction = ref(false);
const ownerOpen = ref(false);
const ownerSearch = ref("");
function onOwnerBlur() { setTimeout(() => { ownerOpen.value = false; }, 120); }
const filteredOwners = computed(() => {
  const s = ownerSearch.value.toLowerCase();
  return ownerOptions.value.filter(u => {
    const label = u.display_name ? `${u.display_name} (${u.email})` : u.email;
    return label.toLowerCase().includes(s);
  });
});

const ibpStepSearch = ref("");
const divOpen = ref(false);
const divSearch = ref("");

const categOpen = ref(false);
const categSearch = ref("");
function onCategBlur() { setTimeout(() => { categOpen.value = false; }, 120); }
const filteredCategs = computed(() => categOptions.value.filter(c => c.toLowerCase().includes(categSearch.value.toLowerCase())));
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
const prStartPeriodOpen = ref(false);
const prStartPeriodSearch = ref("");
const prStartYearOpen = ref(false);
const prStartYearSearch = ref("");
const prEndPeriodOpen = ref(false);
const prEndPeriodSearch = ref("");
const prEndYearOpen = ref(false);
const prEndYearSearch = ref("");
const impactPeriodOpen = ref(false);
const impactPeriodSearch = ref("");
const impactYearOpen = ref(false);
const impactYearSearch = ref("");

function handleBrandFamilyClickOutside() { brandFamilyOpen.value = false; }
function handleBrandClickOutside()       { brandOpen.value = false; }
function handleChannelClickOutside()     { channelOpen.value = false; }
function handleSubChannelClickOutside()  { subChannelOpen.value = false; }
function handleAccountClickOutside()     { accountOpen.value = false; }

const currentYear   = new Date().getFullYear();
const yearOptions   = Array.from({ length: 10 }, (_, i) => currentYear - 2 + i);
const filteredChannels      = computed(() => channelOptions.value.filter(c => c.label.toLowerCase().includes(channelSearch.value.toLowerCase())));
const filteredSubChannels   = computed(() => subChannelOptions.value.filter(s => s.label.toLowerCase().includes(subChannelSearch.value.toLowerCase())));
const filteredBrands        = computed(() => brandOptions.value.filter(b => b.label.toLowerCase().includes(brandSearch.value.toLowerCase())));
const filteredAccounts      = computed(() => accountOptions.value.filter(a => a.label.toLowerCase().includes(accountSearch.value.toLowerCase())));
const filteredBrandFamilies = computed(() => brandFamilyOptions.value.filter(f => f.label.toLowerCase().includes(brandFamilySearch.value.toLowerCase())));

const userIbpSteps = computed(() => {
  const steps = (entryStore.currentUser as any)?.ibp_steps;
  if (steps) {
    return Array.isArray(steps) ? steps : String(steps).split(',').map(s => s.trim());
  }
  return ibpStepOptions.value;
});

const userDivisions = computed(() => {
  const divs = (entryStore.currentUser as any)?.division;
  if (divs) {
    return Array.isArray(divs) ? divs : String(divs).split(',').map(s => s.trim());
  }
  return divisionOptions.value;
});

const userCountries = computed(() => {
  const cnts = ensureObject((entryStore.currentUser as any)?.country);
  return Object.values(cnts);
});

const availableCountryOptions = computed(() => {
  const allowed = userCountries.value;
  if (!allowed.length) return countryOptions.value;
  return countryOptions.value.filter(opt => allowed.includes(opt.label));
});

const filteredIbpSteps = computed(() => userIbpSteps.value.filter(d => d.toLowerCase().includes(ibpStepSearch.value.toLowerCase())));
const filteredDivs = computed(() => userDivisions.value.filter(d => d.toLowerCase().includes(divSearch.value.toLowerCase())));
const filteredCountries = computed(() => availableCountryOptions.value.filter(c => c.label.toLowerCase().includes(countrySearch.value.toLowerCase())));

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

const allBrandFamiliesSelected = computed(() => brandFamilyOptions.value.length > 0 && brandFamilyOptions.value.every(f => !!formData.value.brandFamily[f.value]));
const allBrandsSelected = computed(() => filteredBrands.value.length > 0 && filteredBrands.value.every(b => !!formData.value.brand[b.value]));
const allChannelsSelected = computed(() => {
  const suggestions = filteredChannels.value.filter(c => !isChannelDisabled(c.label));
  return suggestions.length > 0 && suggestions.every(c => !!formData.value.channel[c.value]);
});
const allSubChannelsSelected = computed(() => 
  filteredSubChannels.value.length > 0 && filteredSubChannels.value.every(s => !!formData.value.subChannel[s.value])
);
const allAccountsSelected = computed(() => filteredAccounts.value.length > 0 && filteredAccounts.value.every(a => !!formData.value.account[a.value]));

function isChannelDisabled(ch: string) {
  if (formData.value.division === "Non-Alcohol") return ch === "Licensed" || ch === "Route";
  if (formData.value.division === "Alcohol")     return ch === "Convenience" || ch === "Grocery";
  return false;
}
async function toggleChannel(code: string, name: string) {
  if (isChannelDisabled(name)) return;
  
  if (formData.value.channel[code]) {
    delete formData.value.channel[code];

    if (selectionPriority.value === 'account') {
      const countryName = Object.values(formData.value.country)[0];
      const division = formData.value.division;
      
      const subCodes = Object.keys(formData.value.subChannel);
      for (const scCode of subCodes) {
        const details = await lookupApi.getSubchannelDetails(division, scCode, countryName);
        if (details?.channel?.code === code) {
          delete formData.value.subChannel[scCode];
        }
      }

      const accCodes = Object.keys(formData.value.account);
      for (const accCode of accCodes) {
        const details = await lookupApi.getAccountDetails(division, accCode, countryName);
        if (details?.channel?.code === code) {
          delete formData.value.account[accCode];
        }
      }

      if (Object.keys(formData.value.account).length === 0) {
        selectionPriority.value = null;
        formData.value.channel = {};
        formData.value.subChannel = {};
      } else {
        await syncParentsFromAccounts();
      }
    }
  } else {
    if (!selectionPriority.value) selectionPriority.value = 'channel';
    formData.value.channel[code] = name;
  }
  
  if (Object.keys(formData.value.channel).length === 0 && selectionPriority.value === 'channel') {
    selectionPriority.value = null;
  }
}

async function syncChannelFromSubChannels() {
  const subCodes = Object.keys(formData.value.subChannel);
  const countryName = Object.values(formData.value.country)[0];
  if (!formData.value.division || !countryName) return;

  const newChannels: Record<string, string> = {};
  isReverseAction.value = true;
  
  try {
    const results = await Promise.all(
      subCodes.map(code => lookupApi.getSubchannelDetails(formData.value.division, code, countryName))
    );

    results.forEach(details => {
      if (details && details.channel) {
        newChannels[details.channel.code] = details.channel.name;
      }
    });
    formData.value.channel = newChannels;
  } catch (e) {
    console.error("Error syncing channels from subchannels:", e);
  } finally {
    await nextTick();
    isReverseAction.value = false;
  }
}

async function toggleSubChannel(code: string, name: string) {
  if (formData.value.subChannel[code]) {
    delete formData.value.subChannel[code];

    if (selectionPriority.value === 'account') {
      const countryName = Object.values(formData.value.country)[0];
      const division = formData.value.division;

      const accCodes = Object.keys(formData.value.account);
      for (const accCode of accCodes) {
        const details = await lookupApi.getAccountDetails(division, accCode, countryName);
        if (details?.subchannel?.code === code) {
          delete formData.value.account[accCode];
        }
      }

      if (Object.keys(formData.value.account).length === 0) {
        selectionPriority.value = null;
        formData.value.channel = {};
        formData.value.subChannel = {};
      } else {
        await syncParentsFromAccounts();
      }
    }
  } else {
    if (!selectionPriority.value) selectionPriority.value = 'channel';
    formData.value.subChannel[code] = name;
  }
  
  if (selectionPriority.value === 'channel') {
    formData.value.account = {};
  } else if (selectionPriority.value === 'account') {
    await syncChannelFromSubChannels();
  }
}

async function syncParentsFromAccounts() {
  const accountCodes = Object.keys(formData.value.account);
  const countryName = Object.values(formData.value.country)[0];
  if (!formData.value.division || !countryName) return;

  const newChannels: Record<string, string> = {};
  const newSubChannels: Record<string, string> = {};
  isReverseAction.value = true;

  try {
    const results = await Promise.all(
      accountCodes.map(code => lookupApi.getAccountDetails(formData.value.division, code, countryName))
    );

    results.forEach(details => {
      if (details && details.channel && details.subchannel) {
        newChannels[details.channel.code] = details.channel.name;
        newSubChannels[details.subchannel.code] = details.subchannel.name;
      }
    });

    formData.value.channel = newChannels;
    formData.value.subChannel = newSubChannels;
  } catch (e) {
    console.error("Error syncing parents from accounts:", e);
  } finally {
    await nextTick();
    isReverseAction.value = false;
  }
}

async function handleAccountToggle(code: string, name: string) {
  if (formData.value.account[code]) {
    delete formData.value.account[code];
    if (selectionPriority.value === 'account') {
      if (Object.keys(formData.value.account).length === 0) {
        selectionPriority.value = null;
        formData.value.channel = {};
        formData.value.subChannel = {};
      } else {
        await syncParentsFromAccounts();
      }
    }
  } else {
    if (!selectionPriority.value) selectionPriority.value = 'account';
    formData.value.account[code] = name;
    
    if (selectionPriority.value === 'account') {
      await syncParentsFromAccounts();
    }
  }
}

async function syncBrandFromBrandFamilies() {
  const brandFamilyCodes = Object.keys(formData.value.brandFamily);
  const countryName = Object.values(formData.value.country)[0];
  if (!formData.value.division || !countryName) return;

  const newBrands: Record<string, string> = {};
  isReverseAction.value = true;

  try {
    const results = await Promise.all(
      brandFamilyCodes.map(code => lookupApi.getBrandFamilyDetails(formData.value.division, code, countryName))
    );

    results.forEach(details => {
      if (details && details.brand) {
        newBrands[details.brand.code] = details.brand.name;
      }
    });

    formData.value.brand = newBrands;
  } catch (e) {
    console.error("Error syncing brands from brand families:", e);
  } finally {
    await nextTick();
    isReverseAction.value = false;
  }
}

async function syncBrandFamiliesFromBrand() {
  const brandCodes = Object.keys(formData.value.brand);
  const countryName = Object.values(formData.value.country)[0];
  if (!formData.value.division || !countryName) return;

  const newBrandFamilies: Record<string, string> = {};
  isReverseAction.value = true;

  try {
    const results = await Promise.all(
      brandCodes.map(code => lookupApi.getBrandFamiliesByBrand(formData.value.division, code, countryName))
    );

    results.forEach(data => {
      data.options.forEach(option => {
        newBrandFamilies[option.value] = option.label;
      });
    });

    formData.value.brandFamily = newBrandFamilies;
  } catch (e) {
    console.error("Error syncing brand families from brands:", e);
  } finally {
    await nextTick();
    isReverseAction.value = false;
  }
}

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

async function toggleBrand(code: string, name: string) {
  if (formData.value.brand[code]) {
    delete formData.value.brand[code];

    if (brandSelectionPriority.value === 'brandFamily') {
      const countryName = Object.values(formData.value.country)[0];
      const division = formData.value.division;
      
      const bfCodes = Object.keys(formData.value.brandFamily);
      for (const bfCode of bfCodes) {
        const details = await lookupApi.getBrandFamilyDetails(division, bfCode, countryName);
        if (details?.brand?.code === code) {
          delete formData.value.brandFamily[bfCode];
        }
      }

      if (Object.keys(formData.value.brandFamily).length === 0) {
        brandSelectionPriority.value = null;
        formData.value.brand = {};
        formData.value.brandFamily = {};
      } else {
        await syncBrandFromBrandFamilies();
      }
    }
  } else {
    if (!brandSelectionPriority.value) brandSelectionPriority.value = 'brand';
    formData.value.brand[code] = name;
  }
  
  if (Object.keys(formData.value.brand).length === 0 && brandSelectionPriority.value === 'brand') {
    brandSelectionPriority.value = null;
  }
}

async function toggleAllBrands() {
  const suggestions = filteredBrands.value;
  
  if (allBrandsSelected.value) {
    if (brandSelectionPriority.value === 'brandFamily') {
      const countryName = Object.values(formData.value.country)[0];
      const division = formData.value.division;
      const codesToRemove = suggestions.map(b => b.value);

      const bfCodes = Object.keys(formData.value.brandFamily);
      for (const bfCode of bfCodes) {
        const details = await lookupApi.getBrandFamilyDetails(division, bfCode, countryName);
        if (details?.brand?.code && codesToRemove.includes(details.brand.code)) {
          delete formData.value.brandFamily[bfCode];
        }
      }

      if (Object.keys(formData.value.brandFamily).length === 0) {
        brandSelectionPriority.value = null;
        formData.value.brand = {};
        formData.value.brandFamily = {};
      } else {
        await syncBrandFromBrandFamilies();
      }
    } else {
      suggestions.forEach(b => delete formData.value.brand[b.value]);
    }
  } else {
    if (!brandSelectionPriority.value) brandSelectionPriority.value = 'brand';
    suggestions.forEach(b => formData.value.brand[b.value] = b.label);
  }
  if (brandSelectionPriority.value === 'brand' && Object.keys(formData.value.brand).length === 0) {
    brandSelectionPriority.value = null;
  }
}

async function toggleAllChannels() {
  const suggestions = filteredChannels.value.filter(c => !isChannelDisabled(c.label));
  
  if (allChannelsSelected.value) {
    if (selectionPriority.value === 'account') {
      const countryName = Object.values(formData.value.country)[0];
      const division = formData.value.division;
      const codesToRemove = suggestions.map(c => c.value);

      const subCodes = Object.keys(formData.value.subChannel);
      for (const scCode of subCodes) {
        const details = await lookupApi.getSubchannelDetails(division, scCode, countryName);
        if (details?.channel?.code && codesToRemove.includes(details.channel.code)) {
          delete formData.value.subChannel[scCode];
        }
      }

      const accCodes = Object.keys(formData.value.account);
      for (const accCode of accCodes) {
        const details = await lookupApi.getAccountDetails(division, accCode, countryName);
        if (details?.channel?.code && codesToRemove.includes(details.channel.code)) {
          delete formData.value.account[accCode];
        }
      }

      if (Object.keys(formData.value.account).length === 0) {
        selectionPriority.value = null;
        formData.value.channel = {};
        formData.value.subChannel = {};
      } else {
        await syncParentsFromAccounts();
      }
    } else {
      suggestions.forEach(c => delete formData.value.channel[c.value]);
    }
  } else {
    if (!selectionPriority.value) selectionPriority.value = 'channel';
    suggestions.forEach(c => formData.value.channel[c.value] = c.label);
  }
  if (selectionPriority.value === 'channel' && Object.keys(formData.value.channel).length === 0) {
    selectionPriority.value = null;
  }
}

async function toggleAllSubChannels() {
  const suggestions = filteredSubChannels.value;

  if (allSubChannelsSelected.value) {
    if (selectionPriority.value === 'account') {
      const countryName = Object.values(formData.value.country)[0];
      const division = formData.value.division;
      const codesToRemove = suggestions.map(s => s.value);

      const accCodes = Object.keys(formData.value.account);
      for (const accCode of accCodes) {
        const details = await lookupApi.getAccountDetails(division, accCode, countryName);
        if (details?.subchannel?.code && codesToRemove.includes(details.subchannel.code)) {
          delete formData.value.account[accCode];
        }
      }

      if (Object.keys(formData.value.account).length === 0) {
        selectionPriority.value = null;
        formData.value.channel = {};
        formData.value.subChannel = {};
      } else {
        await syncParentsFromAccounts();
      }
    } else {
      suggestions.forEach(s => delete formData.value.subChannel[s.value]);
    }
  } else {
    if (!selectionPriority.value) selectionPriority.value = 'channel';
    suggestions.forEach(s => formData.value.subChannel[s.value] = s.label);
  }

  if (selectionPriority.value === 'channel') {
    formData.value.account = {};
  } else if (selectionPriority.value === 'account') {
    await syncChannelFromSubChannels();
  }
}

async function toggleAllAccounts() {
  if (allAccountsSelected.value) {
    filteredAccounts.value.forEach(a => delete formData.value.account[a.value]);
  } else {
    if (!selectionPriority.value) selectionPriority.value = 'account';
    filteredAccounts.value.forEach(a => formData.value.account[a.value] = a.label);
  }

  if (selectionPriority.value === 'account') {
    if (Object.keys(formData.value.account).length === 0) {
      selectionPriority.value = null;
      formData.value.channel = {};
      formData.value.subChannel = {};
    } else {
      await syncParentsFromAccounts();
    }
  }
}

async function toggleBrandFamily(code: string, name: string) {
  if (formData.value.brandFamily[code]) {
    delete formData.value.brandFamily[code];

    if (brandSelectionPriority.value === 'brandFamily') {
      if (Object.keys(formData.value.brandFamily).length === 0) {
        brandSelectionPriority.value = null;
        formData.value.brand = {};
        formData.value.brandFamily = {};
      } else {
        await syncBrandFromBrandFamilies();
      }
    }
  } else {
    if (!brandSelectionPriority.value) brandSelectionPriority.value = 'brandFamily';
    formData.value.brandFamily[code] = name;
  }
  
  if (brandSelectionPriority.value === 'brand') {
  } else if (brandSelectionPriority.value === 'brandFamily') {
    await syncBrandFromBrandFamilies();
  }
}

function addCustomBrandFamily() {
  const val = brandFamilySearch.value.trim();
  if (val && !Object.values(formData.value.brandFamily).includes(val)) {
    formData.value.brandFamily[val] = val;
  }
  brandFamilySearch.value = "";
}
async function toggleAllBrandFamilies() {
  const suggestions = filteredBrandFamilies.value;

  if (allBrandFamiliesSelected.value) {
    if (brandSelectionPriority.value === 'brandFamily') {
      const codesToRemove = suggestions.map(f => f.value);

      const bfCodes = Object.keys(formData.value.brandFamily);
      for (const bfCode of bfCodes) {
        if (codesToRemove.includes(bfCode)) {
          delete formData.value.brandFamily[bfCode];
        }
      }

      if (Object.keys(formData.value.brandFamily).length === 0) {
        brandSelectionPriority.value = null;
        formData.value.brand = {};
        formData.value.brandFamily = {};
      } else {
        await syncBrandFromBrandFamilies();
      }
    } else {
      suggestions.forEach(f => delete formData.value.brandFamily[f.value]);
    }
  } else {
    if (!brandSelectionPriority.value) brandSelectionPriority.value = 'brandFamily';
    suggestions.forEach(f => formData.value.brandFamily[f.value] = f.label);
  }

  if (brandSelectionPriority.value === 'brandFamily') {
    if (Object.keys(formData.value.brandFamily).length > 0) {
      await syncBrandFromBrandFamilies();
    }
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
  volumeImpactValue?: string; // Added for child impacts
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
  ibpStep:               string;
  country:               Record<string, string>;
  channel:               Record<string, string>;
  subChannel:            Record<string, string>;
  account:               Record<string, string>;
  brand:                 Record<string, string>;
  brandFamily:           Record<string, string>;
  rAndO:                 string;
  probability:           string;
  categorisation:        string;
  impactPeriod:          string;
  impactYear:            string;
  impactValue:           string;
  primaryImpact:         string;
  secondaryValue:        string;
  secondaryUnit:         string;
  financialImpactType:   string;
  volumeImpactType:      string;
  volumeImpactValue:     string;
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

const currentMonth  = new Date().getMonth() + 1;
const currentPeriod = `F${String(currentMonth).padStart(2, "0")}`;
const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];

const usePeriodRange   = ref(false);
const periodRangeStart = ref({ period: currentPeriod, year: String(currentYear) });
const periodRangeEnd   = ref({ period: currentPeriod, year: String(currentYear) });

function onCancelPeriodRange(val: boolean) {
  if (!val) {
    periodRangeStart.value = { period: currentPeriod, year: String(currentYear) };
    periodRangeEnd.value   = { period: currentPeriod, year: String(currentYear) };
  }
}

const formRef       = ref<FormInstance>();
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
    division:        "", ibpStep:         "", country:         {},
    channel:         {}, subChannel:      {}, account:         {},
    brand:           {}, brandFamily:     {}, rAndO:           "Risk",
    probability:     "", categorisation:  "", impactPeriod:    currentPeriod,
    impactYear:      String(currentYear), impactValue:     "", primaryImpact:   "AUD",
    secondaryValue:  "", secondaryUnit:   "Volume", financialImpactType:      "NSV",
    volumeImpactType: "Cases",
    volumeImpactValue: "",
    owner:           email, creator:         email, status:          "Open",
    shortDescription:    "", detailedDescription: "", childImpacts:    [],
  };
}

const formData = ref<FormData>(defaultForm());
const isLoadingEntry  = ref(false);
const hasChildImpacts = computed(() => formData.value.childImpacts.length > 0);

function getUnitOptions(countryDict: Record<string, string>): string[] {
  const countryName = Object.values(countryDict)[0];
  if (countryName === "Australia")   return ["AUD", "Volume"];
  if (countryName === "New Zealand") return ["NZD", "Volume"];
  return ["AUD", "NZD", "Volume"];
}
const unitOptions = computed(() => getUnitOptions(formData.value.country));

const isAlcohol = computed(() => {
  const d = formData.value.division.toLowerCase();
  return d.includes("alcohol") && !d.includes("non-alcohol");
});

function getfinancialImpactTypeLabel(financialImpactType: string): string {
  const currency = formData.value.primaryImpact === "NZD" ? "NZD" : "AUD";
  const labels: Record<string, string> = { NSV: `NSV (${currency})`, COGS: `COGS (${currency})`, LOGS: `LOGS (${currency})`, GP: `GP (${currency})`, OI: `OI (${currency})` };
  return labels[financialImpactType] || "Financial Impact Value";
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
  const countryName = Object.values(country)[0];
  if (countryName === "New Zealand" && !opts.includes(formData.value.primaryImpact)) formData.value.primaryImpact = "NZD";
  else if (countryName === "Australia" && !opts.includes(formData.value.primaryImpact)) formData.value.primaryImpact = "AUD";
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

watch(() => formData.value.division, async (division) => {
  if (!isLoadingEntry.value) {
    formData.value.brand = {};
    formData.value.brandFamily = {};
    formData.value.channel = {};
    formData.value.subChannel = {};
    formData.value.account = {};
    selectionPriority.value = null;
    brandSelectionPriority.value = null;
  }

  if (division && Object.keys(formData.value.country).length > 0) {
    await loadCountryBasedLookups(formData.value.country, division);
  }
}, { immediate: true });

watch(() => formData.value.country, async (country) => {
  if (!isLoadingEntry.value) {
    formData.value.brand = {};
    formData.value.brandFamily = {};
    formData.value.channel = {};
    formData.value.subChannel = {};
    formData.value.account = {};
    selectionPriority.value = null;
    brandSelectionPriority.value = null;
  }

  await loadCountryBasedLookups(country, formData.value.division);
});

async function loadCountryBasedLookups(country: Record<string, string>, division: string) {
  if (Object.keys(country).length > 0 && division) {
    try {
      const countryName = Object.values(country)[0];
      
      const brandData = await lookupApi.getBrands(division, countryName);
      brandOptions.value = brandData.options;

      const brandNames = brandData.options.map(b => b.label);
      if (brandNames.length > 0) {
        const brandFamilyData = await lookupApi.getBrandFamilies(brandNames, countryName, division);
        brandFamilyOptions.value = brandFamilyData.options;
      } else {
        brandFamilyOptions.value = [];
      }

      const data = await lookupApi.getChannels(division, countryName);
      channelOptions.value = data.options;

      const accData = await lookupApi.getAccounts(division, "", countryName);
      accountOptions.value = accData.options;
    } catch (error) {
      console.error("Error loading country-based lookups:", error);
      brandOptions.value = [];
      brandFamilyOptions.value = [];
      channelOptions.value = [];
      accountOptions.value = [];
    }
  } else {
    brandOptions.value = [];
    brandFamilyOptions.value = [];
    channelOptions.value = [];
    accountOptions.value = [];
  }
}

watch(() => formData.value.channel, async (channelsMap) => {
  if (!isLoadingEntry.value && !isReverseAction.value) {
    if (selectionPriority.value !== 'account') {
      formData.value.subChannel = {};
      formData.value.account = {};
    }
  }
  
  const countryName = Object.values(formData.value.country)[0];
  if (!formData.value.division || !countryName) {
    subChannelOptions.value = [];
    return;
  }

  if (selectionPriority.value === 'account') {
    try {
      const data = await lookupApi.getSubchannels(formData.value.division, "", countryName);
      subChannelOptions.value = data.options;
    } catch (error) {
      subChannelOptions.value = [];
    }
  } else {
    const channelCodes = Object.keys(channelsMap);
    if (channelCodes.length > 0) {
      const subchannelsMap = new Map<string, {value: string, label: string}>();
      for (const channelCode of channelCodes) {
        if (channelCode) {
          const data = await lookupApi.getSubchannels(formData.value.division, channelCode, countryName);
          data.options.forEach(opt => subchannelsMap.set(opt.value, opt));
        }
      }
      subChannelOptions.value = Array.from(subchannelsMap.values());
    } else {
      subChannelOptions.value = [];
    }
  }
}, { deep: true });

watch(() => formData.value.subChannel, async (subChannelsMap) => {
  if (!isLoadingEntry.value && !isReverseAction.value) {
    if (selectionPriority.value !== 'account') {
      formData.value.account = {};
    }
  }
  
  const countryName = Object.values(formData.value.country)[0];
  if (!formData.value.division || !countryName) {
    accountOptions.value = [];
    return;
  }

  if (selectionPriority.value === 'account') {
    try {
      const data = await lookupApi.getAccounts(formData.value.division, "", countryName);
      accountOptions.value = data.options;
    } catch (error) {
      accountOptions.value = [];
    }
  } else {
    const subchannelCodes = Object.keys(subChannelsMap);
    if (subchannelCodes.length > 0) {
      const accountsMap = new Map<string, {value: string, label: string}>();
      for (const subchannelCode of subchannelCodes) {
        if (subchannelCode) {
          const data = await lookupApi.getAccounts(formData.value.division, subchannelCode, countryName);
          data.options.forEach(opt => accountsMap.set(opt.value, opt));
        }
      }
      accountOptions.value = Array.from(accountsMap.values());
    } else {
      try {
        const data = await lookupApi.getAccounts(formData.value.division, "", countryName);
        accountOptions.value = data.options;
      } catch (e) {
        accountOptions.value = [];
      }
    }
  }
}, { deep: true });

watch(() => formData.value.brand, async (brandMap) => {
  if (!isLoadingEntry.value && !isReverseAction.value) {
    if (brandSelectionPriority.value !== 'brandFamily') {
      formData.value.brandFamily = {};
    }
  }

  const countryName = Object.values(formData.value.country)[0];
  if (!formData.value.division || !countryName) {
    brandFamilyOptions.value = [];
    return;
  }

  if (brandSelectionPriority.value === 'brandFamily') {
    try {
      const allBrands = brandOptions.value.map(b => b.label);
      if (allBrands.length > 0) {
        const data = await lookupApi.getBrandFamilies(allBrands, countryName, formData.value.division);
        brandFamilyOptions.value = data.options;
      } else {
        brandFamilyOptions.value = [];
      }
    } catch (error) {
      console.error("Error loading brand families:", error);
      brandFamilyOptions.value = [];
    }
  } else {
    const brandCodes = Object.keys(brandMap);
    if (brandCodes.length > 0) {
      const brandFamiliesMap = new Map<string, {value: string, label: string}>();
      for (const brandCode of brandCodes) {
        if (brandCode) {
          const data = await lookupApi.getBrandFamiliesByBrand(formData.value.division, brandCode, countryName);
          data.options.forEach(opt => brandFamiliesMap.set(opt.value, opt));
        }
      }
      brandFamilyOptions.value = Array.from(brandFamiliesMap.values());
    } else {
      try {
        const allBrands = brandOptions.value.map(b => b.label);
        if (allBrands.length > 0) {
          const data = await lookupApi.getBrandFamilies(allBrands, countryName, formData.value.division);
          brandFamilyOptions.value = data.options;
        } else {
          brandFamilyOptions.value = [];
        }
      } catch (error) {
        console.error("Error loading all brand families:", error);
        brandFamilyOptions.value = [];
      }
    }
  }
}, { deep: true });

watch(() => formData.value.brandFamily, async (brandFamilyMap) => {
  if (brandSelectionPriority.value === 'brandFamily') {
    if (Object.keys(brandFamilyMap).length > 0) {
      await syncBrandFromBrandFamilies();
    }
  }
}, { deep: true });

watch(brandFamilyOpen, async (isOpen) => {
  if (isOpen) {
    if (!brandSelectionPriority.value) brandSelectionPriority.value = 'brandFamily';
    
    if (brandFamilyOptions.value.length === 0) {
      const countryName = Object.values(formData.value.country)[0];
      if (formData.value.division && countryName) {
        try {
          const allBrands = brandOptions.value.map(b => b.label);
          if (allBrands.length > 0) {
            const data = await lookupApi.getBrandFamilies(allBrands, countryName, formData.value.division);
            brandFamilyOptions.value = data.options;
          }
        } catch (e) {
          console.error("Error loading brand families on open:", e);
        }
      }
    }
  }
});

watch(accountOpen, async (isOpen) => {
  if (isOpen) {
    if (!selectionPriority.value) selectionPriority.value = 'account';
    
    if (accountOptions.value.length === 0) {
      const countryName = Object.values(formData.value.country)[0];
      if (formData.value.division && countryName) {
        try {
          const data = await lookupApi.getAccounts(formData.value.division, "", countryName);
          accountOptions.value = data.options;
        } catch (e) {
          console.error("Error loading accounts on open:", e);
        }
      }
    }
  } else if (Object.keys(formData.value.account).length > 0) {
    await syncParentsFromAccounts();
  }
});

watch(brandOpen, (isOpen) => {
  if (isOpen && !brandSelectionPriority.value) {
    brandSelectionPriority.value = 'brand';
  }
});

watch(channelOpen, (isOpen) => {
  if (isOpen && !selectionPriority.value) {
    selectionPriority.value = 'channel';
  }
});

watch(subChannelOpen, (isOpen) => {
  if (isOpen && !selectionPriority.value) {
    selectionPriority.value = 'channel';
  }
});

watch(() => formData.value.ibpStep, (val) => {
  if (isInitialLoadRef.value) return;
  if (!CATEG_ACTIVE_IBP_STEPS.includes(val)) formData.value.categorisation = "";
  if (val === "Demand Review") formData.value.financialImpactType = "NSV";
  else if (formData.value.financialImpactType === "NSV") formData.value.financialImpactType = "OI";
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
  selectionPriority.value = null;
  brandSelectionPriority.value = null;
  if (entry) {
    isInitialLoadRef.value = true;
    const _d = (entry.division || "").toLowerCase();
    const entryIsAlcohol = _d.includes("alcohol") && !_d.includes("non-alcohol");
    const fromStorage = (unit: string, val: string): string => {
      if (!val || unit !== "Volume" || !entryIsAlcohol) return val;
      const n = parseFloat(val); return isNaN(n) ? val : String(n / 9);
    };
    
    const creator = entry.creator || currentUserEmail.value;
    const owner   = entry.owner  || currentUserEmail.value;
    ownerSameAsCreator.value = owner === creator;

    formData.value = {
      creationDatePeriod:    entry.creationDatePeriod  || currentPeriod,
      creationDateYear:      entry.creationDateYear    || String(currentYear),
      addToForecastByPeriod: entry.addToForecastByPeriod || currentPeriod,
      addToForecastByYear:   entry.addToForecastByYear   || String(currentYear),
      division:       entry.division      || "", ibpStep:         entry.ibpStep       || "",
      country:        ensureObject(entry.country),
      channel:        ensureObject(entry.channel),
      subChannel:     ensureObject(entry.subChannel),
      account:        ensureObject(entry.account),
      brand:          ensureObject(entry.brand),
      brandFamily:    ensureObject(entry.brandFamily),
      rAndO:          entry.rAndO         || "Risk", probability:     entry.probability   || "",
      categorisation: entry.categorisation|| "", impactPeriod:   entry.impactPeriod  || "",
      impactYear:     entry.impactYear    || (entry.childImpacts?.length ? "" : String(currentYear)),
      primaryImpact:  entry.primaryImpact || "AUD", financialImpactType:     entry.financialImpactType    || "OI",
      volumeImpactType: (entry as any).volumeImpactType || "Cases",
      volumeImpactValue: (entry as any).volumeImpactValue || "",
      impactValue: formatNumStr(entry.primaryImpact === "NZD" ? (entry.nsvNzd || "") : entry.primaryImpact === "Volume" ? ((entry as any).volumeImpactValue || fromStorage("Volume", entry.volumeLitres || "")) : (entry.nsvAud || "")),
      ...((): { secondaryUnit: string; secondaryValue: string } => {
        const pi = entry.primaryImpact || "AUD";
        const candidates = [
          { unit: "AUD", val: entry.nsvAud || "" }, { unit: "NZD", val: entry.nsvNzd || "" }, { unit: "Volume", val: (entry as any).volumeImpactValue || fromStorage("Volume", entry.volumeLitres || "") },
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
          impactValue: formatNumStr(primary === "NZD" ? (ci.nsvNzd || "") : primary === "Volume" ? (ci.volumeImpactValue || fromStorage("Volume", ci.volumeLitres || "")) : (ci.nsvAud || "")),
          secondaryUnit:  sec.unit, secondaryValue: formatNumStr(sec.val),
          _periodOpen: false, _periodSearch: "", _yearOpen: false, _yearSearch: ""
        };
      }),
    };
    
    await nextTick();
    setTimeout(() => {
      isInitialLoadRef.value = false;
      isLoadingEntry.value = false;
    }, 300);
  } else {
    formData.value = defaultForm();
    ownerSameAsCreator.value = true;
    usePeriodRange.value     = false;
    periodRangeStart.value   = { period: currentPeriod, year: String(currentYear) };
    periodRangeEnd.value     = { period: currentPeriod, year: String(currentYear) };
    isLoadingEntry.value = false;
  }
}, { immediate: true });

const rules: FormRules = {
  creationDatePeriod: [{ required: true, message: "Please fill out this field.", trigger: "change" }],
  creationDateYear: [{ required: true, message: "Please fill out this field.", trigger: "change" }],
  division: [{ required: true, message: "Please fill out this field.", trigger: "change" }],
  ibpStep: [{ required: true, message: "Please fill out this field.", trigger: "change" }],
  country: [{ validator: (_rule: any, value: any, callback: any) => { if (!Object.keys(value || {}).length) callback(new Error("Please fill out this field.")); else callback(); }, trigger: "change" }],
  channel: [{ validator: (_rule: any, value: any, callback: any) => { if (!Object.keys(value || {}).length) callback(new Error("Please fill out this field.")); else callback(); }, trigger: "change" }],
  subChannel: [{ validator: (_rule: any, value: any, callback: any) => { if (!Object.keys(value || {}).length) callback(new Error("Please fill out this field.")); else callback(); }, trigger: "change" }],
  account: [{ validator: (_rule: any, value: any, callback: any) => { if (!Object.keys(value || {}).length) callback(new Error("Please fill out this field.")); else callback(); }, trigger: "change" }],
  brand: [{ validator: (_rule: any, value: any, callback: any) => { if (!Object.keys(value || {}).length) callback(new Error("Please fill out this field.")); else callback(); }, trigger: "change" }],
  brandFamily: [{ validator: (_rule: any, value: any, callback: any) => { if (!Object.keys(value || {}).length) callback(new Error("Please fill out this field.")); else callback(); }, trigger: "change" }],
  rAndO: [{ required: true, message: "Please fill out this field.", trigger: "change" }],
  probability: [{ required: true, message: "Please fill out this field.", trigger: "change" }],
  categorisation: [{ validator: (_rule: unknown, value: string, callback: (e?: Error) => void) => { if (categActive.value && !value) callback(new Error("Please fill out this field.")); else callback(); }, trigger: "change" }],
  owner: [{ required: true, message: "Please fill out this field.", trigger: "change" }],
  creator: [{ required: true, message: "Please fill out this field.", trigger: "blur" }],
  shortDescription: [{ required: true, message: "Please fill out this field.", trigger: "blur" }],
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
  usePeriodRange.value = false; periodRangeStart.value = { period: currentPeriod, year: String(currentYear) }; periodRangeEnd.value = { period: currentPeriod, year: String(currentYear) };
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
function mapToFields(primaryUnit: string, primaryVal: string, secUnit: string, secVal: string): { nsvAud: string; nsvNzd: string; volumeLitres: string; volumeImpactValue: string } {
  const set = (unit: string) => unit === primaryUnit ? toStorage(unit, primaryVal) : unit === secUnit ? toStorage(unit, secVal) : "";
  const getRaw = (unit: string) => unit === primaryUnit ? primaryVal : unit === secUnit ? secVal : "";
  return {
    nsvAud: set("AUD"),
    nsvNzd: set("NZD"),
    volumeLitres: set("Volume"),
    volumeImpactValue: getRaw("Volume"),
  };
}

async function validate() {
  try {
    await formRef.value!.validate().catch(err => {
      const firstField = Object.keys(err)[0];
      if (firstField) formRef.value!.scrollToField(firstField);
      throw err;
    });
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

    const { nsvAud, nsvNzd, volumeLitres, volumeImpactValue } = mapToFields(formData.value.primaryImpact, formData.value.impactValue, formData.value.secondaryUnit, formData.value.secondaryValue);

    return {
      ...formData.value,
      // Ensure volumeImpactValue is correctly set for the parent entry
      volumeImpactValue: cleanNumStr(volumeImpactValue),
      channel: formData.value.channel,
      subChannel: formData.value.subChannel,
      account: formData.value.account,
      nsvAud, nsvNzd, volumeLitres,
      childImpacts: formData.value.childImpacts.map(ci => {
        const m = mapToFields(ci.impactUnit, ci.impactValue, ci.secondaryUnit, ci.secondaryValue);
        return {
          impactYear: ci.impactYear,
          impactPeriod: ci.impactPeriod,
          ...m,
          volumeImpactValue: cleanNumStr(m.volumeImpactValue),
        };
      }),
    };
  } catch { return null; }
}

function reset() {
  formData.value = defaultForm(); ownerSameAsCreator.value = true;
  selectionPriority.value = null;
  brandSelectionPriority.value = null;
  usePeriodRange.value = false;
  periodRangeStart.value = { period: currentPeriod, year: String(currentYear) };
  periodRangeEnd.value   = { period: currentPeriod, year: String(currentYear) };
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
  max-height: 70vh;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 16px;
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
  font-size: 14px;
  color: #1a1a1a;
  padding-bottom: 4px;
  line-height: 1.2;
}

/* Input Fields overrides */
:deep(.el-input__wrapper),
:deep(.el-textarea__inner),
:deep(.el-select .el-input__wrapper) {
  font-size: 14px;
  background-color: #f4f5f7;
  border: 1px solid transparent;
  box-shadow: 0 0 0 1px transparent inset !important;
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

:deep(.el-form-item.is-error .el-input__wrapper),
:deep(.el-form-item.is-error .el-textarea__inner),
:deep(.el-form-item.is-error .combo-trigger) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
  background-color: #fff !important;
}

:deep(.el-form-item__error) {
  position: relative;
  display: inline-block;
  background: #fef2f2;
  color: #dc2626;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  border: 1px solid #fee2e2;
  margin-top: 6px;
  box-shadow: 0 2px 5px rgba(220, 38, 38, 0.1);
}

:deep(.el-input__inner),
:deep(.el-textarea__inner) {
  color: #000 !important;
}

/* Exception for Creator (keep it muted since it's disabled) */
:deep(.el-form-item[prop="creator"] .el-input.is-disabled .el-input__inner) {
  color: #a8a8a8 !important;
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
.owner-wrap { display: flex; flex-direction: column; width: 100%;}
.owner-checkbox {
  margin-top: -8px;
  margin-bottom: 4px;
}
:deep(.owner-checkbox .el-checkbox__label) {
  color: #000 !important;
  font-weight: 500;
}
:deep(.owner-checkbox .el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #000 !important;
  border-color: #000 !important;
}
:deep(.owner-checkbox .el-checkbox__input .el-checkbox__inner) {
  border-color: #000;
}

:deep(.period-range-check .el-checkbox__label) {
  color: #000 !important;
}
:deep(.period-range-check .el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #000 !important;
  border-color: #000 !important;
}
:deep(.period-range-check .el-checkbox__input .el-checkbox__inner) {
  border-color: #000;
}

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
  background: #0e1015;
  color: #fff;
}

/* ── Input + Dropdown Styling ───────────────────────────────────────── */
.impact-section-subtitle {
  font-size: 14px;
  font-weight: 700;
  /* font-style: italic; */
  color: #1a1a1a;
  margin-top: 8px;
  margin-bottom: 4px;
}
.input-with-dropdown {
  display: flex;
  align-items: stretch;
  gap: 12px;
  width: 100%;
}
.black-dropdown-btn {
  background-color: #0e1015 !important;
  border-color: #0e1015 !important;
  color: #fff !important;
  font-weight: 600;
  width: 110px;
  height: 100%;
  border-radius: 4px;
}
.black-dropdown-btn:hover, .black-dropdown-btn:focus {
  background-color: #2a2d35 !important;
  border-color: #2a2d35 !important;
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
.combo-trigger .has-value { color: #000; font-weight: 500; }
.combo-trigger .placeholder { color: #a8a8a8; }

.has-selected-value :deep(input::placeholder) {
  color: #000 !important;
  opacity: 1;
}

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

.range-block { display: flex; flex-direction: column; width: 100%;}
.prorate-btn {
  width: 100%;
  background-color: #000;
  border-color: #000;
  color: #fff;
  height: 30px;
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

/* Spacing Utils */
.mt-1 { margin-top: 4px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 24px; }
</style>