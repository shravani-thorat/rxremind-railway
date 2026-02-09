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

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/firebase-messaging-sw.js")
    .then((registration) => {

      const app = initializeApp(firebaseConfig);
      const messaging = getMessaging(app);

      Notification.requestPermission().then((permission) => {
        if (permission === "granted") {

          getToken(messaging, {
            vapidKey: "BG0KjYPTQWnUHl5ozG4xntepXG_53yc0RCVYLvEN_9_OuWotIUBoUcgBY7mgnLeZEA8oDorgrrDTRrehvBknu2A",
            serviceWorkerRegistration: registration
          }).then((currentToken) => {

            if (currentToken) {
              console.log("Token:", currentToken);

              fetch("/save-token", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: currentToken })
              });

            } else {
              console.log("No token received.");
            }

          }).catch((err) => {
            console.error("Error getting token:", err);
          });
        }
      });

    });
}