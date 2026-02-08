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