function addMedicine() {
    const div = document.createElement("div");

    div.innerHTML = `
        <br>
        <label>Medicine</label>
        <input type="text" name="medicine[]" required>

        <label>Quantity</label>
        <input type="number" name="quantity[]" required>

        <label>Days</label>
        <input type="number" name="days[]" placeholder="e.g. 30" min="1" required>
    `;

    document.getElementById("medicines").appendChild(div);
}

document.addEventListener("DOMContentLoaded",() => {
    if("notification" in window) {
        Notification.requestPermission();
    }
});

function ShowReminderNotification(title, message) {
    if (Notification.permission === "granted") {
        new Notification(title, {
            body: message,
            icon: "/static/icon.png"
        });
    }
}

function checkReminders() {
    fetch("/api/reminders")
    .then(res => res.json())
    .then(data => {
        if(data.length > 0){
            let r = data[0];
            ShowReminderNotification(
                "Medicine Refill Reminder",
                `${r.name} - ${r.medicine} - Call customer`
            );
        }
    });
}

setInterval(checkReminders, 60*60*1000);

if("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/sw.js");
}

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getMessaging, getToken } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging.js";

const firebaseConfig = {
    apiKey: "AIzaSyC5xLeT44La7Cfz5w2l5NgF5MWVzh_gtyY",
    authDomain: "rxremind-bb83e.firebaseapp.com",
    projectId: "rxremind-bb83e",
    messagingSenderId: "1098454881651",
    appId: "1:1098454881651:web:fe4cf0689ab90bf10f6106"
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

Notification.requestPermission().then((permission) => {
  if (permission === "granted") {
    getToken(messaging, {
      vapidKey: "YOUR_PUBLIC_VAPID_KEY"
    }).then((currentToken) => {
      if (currentToken) {
        fetch("/save-token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token: currentToken })
        });
      }
    });
  }
});