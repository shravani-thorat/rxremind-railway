self.addEventListener("install", event => {
    console.log("Service Worker Installed");
    self.skipWaiting();
});

self.addEventListener("activate", event => {
    console.log("Service Worker Activated");
    event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
    if (event.request.method !== "GET") return;

    
    if (event.request.url.includes("/api/") ||
        event.request.url.includes("/toggle/") ||
        event.request.url.includes("/delete/")) {
        return;
    }

    event.respondWith(fetch(event.request));
});

// Firebase Scripts
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js");

// Initialize Firebase
firebase.initializeApp({
  apiKey: "AIzaSyC5xLeT44La7Cfz5w2l5NgF5MWVzh_gtyY",
  authDomain: "rxremind-bb83e.firebaseapp.com",
  projectId: "rxremind-bb83e",
  messagingSenderId: "1098454881651",
  appId: "1:1098454881651:web:fe4cf0689ab90bf10f6106"
});

const messaging = firebase.messaging();

// Background Notification Handler
messaging.onBackgroundMessage(function(payload) {

    console.log("Push Received:", payload);

    const notificationTitle = payload.notification.title;

    const notificationOptions = {
        body: payload.notification.body,
        icon: "/static/icons/MediPingLogo.png",
        badge: "/static/icons/MediPingLogo.png",
        vibrate: [200, 100, 200],
        data: { url: "/reminders" }
    };

    self.registration.showNotification(notificationTitle, notificationOptions);
});

// When User Clicks Notification
self.addEventListener("notificationclick", function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow("/reminders")
    );
});