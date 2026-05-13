import { defineStore } from "pinia";
import { ref } from "vue";
import { lookupApi } from "@/services/api";

/** Cache key: "category" or "category:parentValue" */
function cacheKey(category: string, parentValue?: string | string[]): string {
  if (!parentValue) return category;
  const p = Array.isArray(parentValue) ? parentValue.join(",") : parentValue;
  return p ? `${category}:${p}` : category;
}

export const useLookupStore = defineStore("lookup", () => {
  // Reactive cache so computed properties in components update automatically
  const cache = ref<Record<string, string[]>>({});

  /** Synchronous read from cache (returns [] if not yet loaded) */
  function getCached(category: string, parentValue?: string | string[]): string[] {
    return cache.value[cacheKey(category, parentValue)] ?? [];
  }

  /** Async load — fetches from API if not cached, then stores reactively */
  async function getOptions(category: string, parentValue?: string | string[]): Promise<string[]> {
    const key = cacheKey(category, parentValue);
    if (!cache.value[key]) {
      // Flatten the array to a comma-separated string to avoid Axios '[]' serialization
      const p = Array.isArray(parentValue) ? parentValue.join(",") : parentValue;
      const values = await lookupApi.get(category, p);
      cache.value[key] = values;
    }
    return cache.value[key];
  }

  /**
   * Preload all top-level (no-parent) option categories.
   * Call this once on app startup (e.g. in App.vue onMounted).
   */
  async function preload(): Promise<void> {
    const topLevel = [
      "division", "categorisation", "probability",
      "status", "ibp_step"
    ];
    await Promise.all(topLevel.map((c) => getOptions(c)));
  }

  /** Pre-fetch child options for a given parent (call on parent selection) */
  async function loadChildren(
    childCategory: string,
    parentValue: string | string[]
  ): Promise<void> {
    await getOptions(childCategory, parentValue);
  }

  return { getCached, getOptions, preload, loadChildren };
});
