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
      vapidKey: "BG0KjYPTQWnUHl5ozG4xntepXG_53yc0RCVYLvEN_9_OuWotIUBoUcgBY7mgnLeZEA8oDorgrrDTRrehvBknu2A"
    }).then((currentToken) => {

      if (currentToken) {

        fetch("/save-token", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ token: currentToken }),
        });

        console.log("Token sent to backend");

      } else {
        console.log("No registration token available.");
      }

    }).catch((err) => {
      console.log("Error getting token:", err);
    });

  } else {
    console.log("Notification permission denied.");
  }
});
