async function startScan() {
  const email = document.getElementById("emailInput").value;
  const grid = document.getElementById("resultsGrid");

  if (!email) return alert("Please enter an email");

  // Hide category sections from previous scan
  document.getElementById("profilesSection").classList.add("hidden");
  document.getElementById("accountsSection").classList.add("hidden");
  document.getElementById("securitySection").classList.add("hidden");

  grid.innerHTML =
    '<div class="col-span-full text-center py-10"><i class="fas fa-circle-notch animate-spin text-3xl text-blue-500"></i><p class="mt-4">Extracting digital evidence...</p></div>';

  try {
    const response = await fetch(`http://localhost:8000/scan/${email}`);
    const data = await response.json();
    scanResults = data.results;
    grid.innerHTML = "";

    const profiles = [];
    const accounts = [];
    const security = [];

    data.results.forEach((res) => {
      if (["GitHub", "Gravatar", "LinkedIn"].includes(res.site)) {
        profiles.push(res);
      } else if (["HaveIBeenPwned"].includes(res.site)) {
        security.push(res);
      } else {
        accounts.push(res);
      }
    });

    if (profiles.length > 0) {
      document.getElementById("profilesSection").classList.remove("hidden");
      const profilesGrid = document.getElementById("profilesGrid");
      profilesGrid.innerHTML = "";
      profiles.forEach((res) => renderCard(res, profilesGrid));
    }

    if (accounts.length > 0) {
      document.getElementById("accountsSection").classList.remove("hidden");
      const accountsGrid = document.getElementById("accountsGrid");
      accountsGrid.innerHTML = "";
      accounts.forEach((res) => renderCard(res, accountsGrid));
    }

    if (security.length > 0) {
      document.getElementById("securitySection").classList.remove("hidden");
      const securityGrid = document.getElementById("securityGrid");
      securityGrid.innerHTML = "";
      security.forEach((res) => renderCard(res, securityGrid));
    }
  } catch (err) {
    grid.innerHTML =
      '<p class="text-red-400 text-center col-span-full">Server connection failed. Check if main.py is running.</p>';
  }
}

function renderCard(res, container) {
  const found =
    res.status === "Found" ||
    res.status === "Registered" ||
    res.status === "Breached";

  const card = document.createElement("div");
  card.className = `bg-slate-800/40 border ${
    found ? "border-blue-500/50" : "border-slate-700"
  } p-5 rounded-xl`;
  card.innerHTML = `
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center">
          <i class="fab fa-${res.site.toLowerCase()} text-xl"></i>
        </div>
        <h3 class="font-bold text-lg">${res.site}</h3>
      </div>
      <span class="text-xs uppercase tracking-widest ${
        found ? "text-blue-400" : "text-slate-500"
      } font-bold">
        ${res.status}
      </span>
    </div>
    <p class="text-sm text-slate-400">${res.details || "No public data available"}</p>
    ${
      res.url
        ? `<a href="${res.url}" target="_blank" class="text-blue-500 text-xs mt-3 block">View Public Profile →</a>`
        : ""
    }
    ${
      res.avatar
        ? `<img src="${res.avatar}" class="w-12 h-12 rounded-full mt-2">`
        : ""
    }
  `;
  container.appendChild(card);
}

function exportCSV() {
  if (!scanResults || scanResults.length === 0) {
    alert("No results to export. Please perform a scan first.");
    return;
  }
  let csv = "Site,Status,Details,URL\n";
  scanResults.forEach((res) => {
    csv += `"${res.site}","${res.status}","${res.details || ""}","${
      res.url || ""
    }"\n`;
  });
  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "mailtrace_results.csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

async function uploadCSV() {
  const fileInput = document.getElementById("csvFile");
  const grid = document.getElementById("resultsGrid");

  if (fileInput.files.length === 0) return alert("Select a CSV file first");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  grid.innerHTML =
    '<div class="col-span-full text-center py-6">Processing Bulk List...</div>';

  try {
    const response = await fetch("http://localhost:8000/scan-bulk", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    grid.innerHTML = "";

    function getStatus(resultArray, siteName) {
      const entry = resultArray.find((r) => r.site === siteName);
      return entry ? entry.status : "N/A";
    }

    // Collect all unique site names from the first result to build dynamic columns
    const siteNames =
      data.results.length > 0 ? data.results[0].data.map((r) => r.site) : [];

    let tableHTML = `
      <div class="col-span-full overflow-x-auto bg-slate-800/50 rounded-xl p-4">
        <table class="w-full text-left text-sm">
          <thead>
            <tr class="border-b border-slate-700">
              <th class="py-2 pr-4">Email</th>
              ${siteNames.map((s) => `<th class="py-2 pr-4">${s}</th>`).join("")}
            </tr>
          </thead>
          <tbody>`;

    data.results.forEach((item) => {
      tableHTML += `<tr class="border-b border-slate-700/50">
        <td class="py-3 pr-4">${item.email}</td>
        ${siteNames
          .map((site) => {
            const status = getStatus(item.data, site);
            const isFound =
              status === "Found" ||
              status === "Registered" ||
              status === "Breached";
            return `<td class="py-3 pr-4 ${
              isFound ? "text-green-400" : "text-slate-500"
            }">${status}</td>`;
          })
          .join("")}
      </tr>`;
    });

    tableHTML += `</tbody></table></div>`;
    grid.innerHTML = tableHTML;
  } catch (err) {
    alert("Bulk scan failed. Ensure backend is running.");
  }
}

let scanResults = [];