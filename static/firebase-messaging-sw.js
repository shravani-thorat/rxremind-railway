importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyC5xLeT44La7Cfz5w2l5NgF5MWVzh_gtyY",
  authDomain: "rxremind-bb83e.firebaseapp.com",
  projectId: "rxremind-bb83e",
  messagingSenderId: "1098454881651",
  appId: "1:1098454881651:web:fe4cf0689ab90bf10f6106"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body,
    icon: "/static/icons/MediPingLogo.png"
  });
});