import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "@/views/LoginPage.vue";
import RegisterPage from "@/views/RegisterPage.vue";
import MainPage from "@/views/MainPage.vue";
import PersonalInformationPage from "@/views/PersonalInformationPage.vue";
import AdminPage from "@/views/AdminPage.vue";
import PlatformPage from "@/views/PlatformPage.vue";
import NovelDetailPage from "@/views/NovelDetailPage.vue";
import ModifyPasswordPage from "@/views/ChangePassword.vue";
import BindPhone from '@/views/BindPhonePage.vue';

const routes = [
    { path: "/", redirect: "/login" },
    { path: "/login", component: LoginPage },
    { path: "/register", component: RegisterPage },
    { path: "/main",component: MainPage },
    { path: "/main/:conversationID",name:"Main", component: MainPage,props: true },
    { path: "/personalinformation", component: PersonalInformationPage },
    { path: "/admin", component: AdminPage },
    { path: "/platform", component: PlatformPage },
    { path: "/bind-phone",component:BindPhone},
    { path: "/modify-password",component: ModifyPasswordPage},
    { path: '/novels/:id', name: 'NovelDetail', component: NovelDetailPage },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
