import { createRouter, createWebHistory } from "vue-router";
import MainPage from "@/pages/MainPage.vue";
import EntryHistoryPage from "@/pages/EntryHistoryPage.vue";

const routes = [
  { path: "/", component: MainPage },
  { path: "/entry/:originalEntryId/history", component: EntryHistoryPage },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
