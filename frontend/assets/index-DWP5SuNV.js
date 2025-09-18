async function loadDashboard() {
  try {
    let res = await fetch("/api/dashboard");
    let data = await res.json();

    // Stats
    let statsEl = document.getElementById("stats");
    statsEl.innerHTML = "";
    for (let [key, val] of Object.entries(data.stats)) {
      let div = document.createElement("div");
      div.className = "card";
      div.innerHTML = `<h3>${key}</h3><p>${val}</p>`;
      statsEl.appendChild(div);
    }

    // Alerts
    let alertsEl = document.getElementById("alerts");
    alertsEl.innerHTML = "";
    data.alerts.forEach(a => {
      let div = document.createElement("div");
      div.className = "alert";
      div.innerHTML = `<b>${a.user_id}</b>: ${a.activity}`;
      alertsEl.appendChild(div);
    });

    // High-risk users
    let usersEl = document.getElementById("highRiskUsers");
    usersEl.innerHTML = "";
    data.high_risk_users.forEach(u => {
      let div = document.createElement("div");
      div.className = "user-card";
      div.innerHTML = `<b>${u.name}</b> (${u.department})<br>Risk Score: ${u.score}/100`;
      usersEl.appendChild(div);
    });

  } catch (err) {
    console.error("Dashboard load failed", err);
  }
}

loadDashboard();
setInterval(loadDashboard, 10000);