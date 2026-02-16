// --- State ---
let apiToken = sessionStorage.getItem('ddc_api_token') || '';
const API_BASE = '/api';
const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#a855f7', '#ef4444', '#06b6d4', '#ec4899', '#14b8a6', '#f97316', '#8b5cf6'];

// Chart instances (for cleanup on re-render)
let charts = {};
let worldMap = null;

// --- Auth ---
function login() {
  const input = document.getElementById('tokenInput');
  apiToken = input.value.trim();
  if (!apiToken) return;

  // Test the token with a summary request
  apiFetch('/summary')
    .then(() => {
      sessionStorage.setItem('ddc_api_token', apiToken);
      document.getElementById('loginScreen').style.display = 'none';
      document.getElementById('dashboard').classList.add('active');
      document.getElementById('loginError').style.display = 'none';
      loadDashboard();
    })
    .catch(() => {
      document.getElementById('loginError').style.display = 'block';
      apiToken = '';
    });
}

function logout() {
  sessionStorage.removeItem('ddc_api_token');
  apiToken = '';
  document.getElementById('loginScreen').style.display = 'flex';
  document.getElementById('dashboard').classList.remove('active');
  document.getElementById('tokenInput').value = '';
}

// Auto-login if token exists
if (apiToken) {
  apiFetch('/summary')
    .then(() => {
      document.getElementById('loginScreen').style.display = 'none';
      document.getElementById('dashboard').classList.add('active');
      loadDashboard();
    })
    .catch(() => {
      sessionStorage.removeItem('ddc_api_token');
      apiToken = '';
    });
}

// Enter key on login
document.getElementById('tokenInput').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') login();
});

// --- API ---
async function apiFetch(endpoint, options = {}) {
  const res = await fetch(API_BASE + endpoint, {
    ...options,
    headers: {
      'Authorization': 'Bearer ' + apiToken,
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

// --- Navigation ---
function switchTab(tab) {
  document.querySelectorAll('.nav-tab').forEach((el) => el.classList.remove('active'));
  document.querySelectorAll('.page').forEach((el) => el.classList.remove('active'));

  document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');
  document.getElementById('page-' + tab).classList.add('active');

  // Load data for the tab
  switch (tab) {
    case 'overview': loadOverview(); break;
    case 'packages': loadPackages(); break;
    case 'geography': loadGeography(); break;
    case 'timeseries': loadTimeseries(); break;
  }
}

// --- Dashboard Load ---
function loadDashboard() {
  loadOverview();
  loadPackageFilter();
}

// --- Overview ---
async function loadOverview() {
  try {
    const [summary, trend] = await Promise.all([
      apiFetch('/summary'),
      apiFetch('/timeseries?granularity=day&days=30'),
    ]);

    // Stat cards
    document.getElementById('statTotal').textContent = formatNumber(summary.total_downloads);
    document.getElementById('statToday').textContent = formatNumber(summary.downloads_today);
    document.getElementById('statWeek').textContent = formatNumber(summary.downloads_this_week);
    document.getElementById('statMonth').textContent = formatNumber(summary.downloads_this_month);
    document.getElementById('statUniqueIPs').textContent = formatNumber(summary.unique_ips_today);

    // Update timestamp
    document.getElementById('lastUpdated').textContent =
      'Updated: ' + new Date().toLocaleTimeString();

    // Package bar chart (horizontal)
    renderChart('chartPackages', 'bar', {
      labels: summary.per_package.map((p) => p.package),
      datasets: [{
        label: 'Downloads',
        data: summary.per_package.map((p) => p.count),
        backgroundColor: COLORS.slice(0, summary.per_package.length),
        borderRadius: 6,
      }],
    }, {
      indexAxis: 'y',
      plugins: { legend: { display: false } },
    });

    // Package share doughnut
    renderChart('chartShare', 'doughnut', {
      labels: summary.per_package.map((p) => p.package),
      datasets: [{
        data: summary.per_package.map((p) => p.count),
        backgroundColor: COLORS.slice(0, summary.per_package.length),
        borderWidth: 2,
        borderColor: '#ffffff',
      }],
    }, {
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12, padding: 12 } },
      },
    });

    // 30-day trend line chart
    const trendByPkg = groupByPackage(trend.data);
    const allPeriods = [...new Set(trend.data.map((d) => d.period))].sort();

    renderChart('chartTrend', 'line', {
      labels: allPeriods.map((p) => p.slice(5)), // MM-DD
      datasets: Object.entries(trendByPkg).map(([pkg, points], i) => ({
        label: pkg,
        data: allPeriods.map((period) => {
          const pt = points.find((p) => p.period === period);
          return pt ? pt.count : 0;
        }),
        borderColor: COLORS[i % COLORS.length],
        backgroundColor: COLORS[i % COLORS.length] + '15',
        fill: true,
        tension: 0.3,
        pointRadius: 2,
      })),
    });

    // Cumulative downloads line chart
    const totalByPeriod = {};
    trend.data.forEach((d) => {
      totalByPeriod[d.period] = (totalByPeriod[d.period] || 0) + d.count;
    });
    let cumulative = 0;
    const cumulativeData = allPeriods.map((p) => {
      cumulative += (totalByPeriod[p] || 0);
      return cumulative;
    });

    renderChart('chartCumulative', 'line', {
      labels: allPeriods.map((p) => p.slice(5)),
      datasets: [{
        label: 'Cumulative Downloads',
        data: cumulativeData,
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.08)',
        fill: true,
        tension: 0.3,
        pointRadius: 1,
        borderWidth: 2,
      }],
    }, {
      plugins: { legend: { display: false } },
    });
  } catch (err) {
    console.error('Failed to load overview:', err);
  }
}

// --- Packages ---
async function loadPackages() {
  try {
    const data = await apiFetch('/packages');
    const tbody = document.getElementById('packagesTable');
    tbody.innerHTML = data.packages
      .map((p) => `
        <tr>
          <td><strong>${esc(p.package)}</strong></td>
          <td>${esc(p.version)}</td>
          <td>${esc(p.arch)}</td>
          <td>${formatNumber(p.total_downloads)}</td>
          <td>${formatNumber(p.unique_downloaders)}</td>
          <td>${p.last_downloaded ? new Date(p.last_downloaded).toLocaleString() : '-'}</td>
        </tr>
      `)
      .join('');
  } catch (err) {
    console.error('Failed to load packages:', err);
  }
}

// --- Geography ---
async function loadGeography() {
  try {
    const days = document.getElementById('geoDays').value;
    const data = await apiFetch(`/geography?days=${days}`);

    // World map
    renderWorldMap(data.data);

    // Doughnut chart (top 10)
    const top10 = data.data.slice(0, 10);
    renderChart('chartGeo', 'doughnut', {
      labels: top10.map((d) => countryName(d.country) || 'Unknown'),
      datasets: [{
        data: top10.map((d) => d.count),
        backgroundColor: COLORS,
        borderWidth: 2,
        borderColor: '#ffffff',
      }],
    }, {
      plugins: {
        legend: { position: 'right', labels: { boxWidth: 12, padding: 10 } },
      },
    });

    // Table
    const tbody = document.getElementById('geoTable');
    tbody.innerHTML = data.data
      .map((d) => `
        <tr>
          <td>${countryFlag(d.country)} ${esc(countryName(d.country) || d.country || 'Unknown')}</td>
          <td>${formatNumber(d.count)}</td>
          <td>${formatNumber(d.unique_ips)}</td>
        </tr>
      `)
      .join('');

    // Cities
    loadCities(days);
  } catch (err) {
    console.error('Failed to load geography:', err);
  }
}

// --- Cities ---
async function loadCities(days) {
  try {
    const data = await apiFetch(`/cities?days=${days}`);
    const tbody = document.getElementById('citiesTable');
    tbody.innerHTML = data.data
      .map((d) => `
        <tr>
          <td><strong>${esc(d.city)}</strong></td>
          <td>${esc(d.region || '-')}</td>
          <td>${countryFlag(d.country)} ${esc(countryName(d.country) || d.country || '-')}</td>
          <td>${formatNumber(d.count)}</td>
          <td>${formatNumber(d.unique_ips)}</td>
        </tr>
      `)
      .join('');
  } catch (err) {
    console.error('Failed to load cities:', err);
  }
}

// --- World Map ---
function renderWorldMap(geoData) {
  if (typeof jsVectorMap === 'undefined') {
    document.getElementById('mapContainer').innerHTML =
      '<p style="text-align:center;color:#6b7280;padding:60px;">Map library not available</p>';
    return;
  }

  if (worldMap) {
    worldMap.destroy();
    worldMap = null;
  }
  document.getElementById('mapContainer').innerHTML = '';

  const values = {};
  geoData.forEach((d) => {
    if (d.country && d.country.length === 2) {
      values[d.country.toUpperCase()] = d.count;
    }
  });

  try {
    worldMap = new jsVectorMap({
      selector: '#mapContainer',
      map: 'world',
      backgroundColor: 'transparent',
      regionStyle: {
        initial: {
          fill: '#e5e7eb',
          stroke: '#ffffff',
          strokeWidth: 0.5,
        },
        hover: {
          fillOpacity: 0.8,
          cursor: 'pointer',
        },
      },
      series: {
        regions: [{
          attribute: 'fill',
          scale: ['#dbeafe', '#1d4ed8'],
          values: values,
          min: 0,
        }],
      },
      onRegionTooltipShow(event, tooltip, code) {
        try {
          const count = values[code] || 0;
          tooltip.text(
            tooltip.text() + ': ' + count.toLocaleString() + ' downloads'
          );
        } catch (e) { /* ignore tooltip errors */ }
      },
    });
  } catch (err) {
    console.error('Failed to render map:', err);
    document.getElementById('mapContainer').innerHTML =
      '<p style="text-align:center;color:#6b7280;padding:60px;">Failed to load map</p>';
  }
}

// --- Time Series ---
async function loadTimeseries() {
  try {
    const granularity = document.getElementById('tsGranularity').value;
    const days = document.getElementById('tsDays').value;
    const pkg = document.getElementById('tsPackage').value;

    let url = `/timeseries?granularity=${granularity}&days=${days}`;
    if (pkg) url += `&package=${encodeURIComponent(pkg)}`;

    const data = await apiFetch(url);
    const byPkg = groupByPackage(data.data);
    const allPeriods = [...new Set(data.data.map((d) => d.period))].sort();

    renderChart('chartTimeseries', 'bar', {
      labels: allPeriods.map((p) => formatPeriodLabel(p, granularity)),
      datasets: Object.entries(byPkg).map(([pkgName, points], i) => ({
        label: pkgName,
        data: allPeriods.map((period) => {
          const pt = points.find((p) => p.period === period);
          return pt ? pt.count : 0;
        }),
        backgroundColor: COLORS[i % COLORS.length],
        borderRadius: 4,
      })),
    }, {
      scales: { x: { stacked: true }, y: { stacked: true } },
    });
  } catch (err) {
    console.error('Failed to load timeseries:', err);
  }
}

async function loadPackageFilter() {
  try {
    const data = await apiFetch('/packages');
    const select = document.getElementById('tsPackage');
    const pkgNames = [...new Set(data.packages.map((p) => p.package))];
    pkgNames.forEach((name) => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error('Failed to load package filter:', err);
  }
}

// --- Chart Helpers ---
function renderChart(canvasId, type, data, extraOptions = {}) {
  if (charts[canvasId]) {
    charts[canvasId].destroy();
  }

  const ctx = document.getElementById(canvasId).getContext('2d');
  charts[canvasId] = new Chart(ctx, {
    type,
    data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: '#4b5563', font: { size: 12 } },
        },
      },
      scales: type === 'doughnut' || type === 'pie' ? {} : {
        x: {
          ticks: { color: '#6b7280' },
          grid: { color: '#f3f4f6' },
          ...(extraOptions.scales?.x || {}),
        },
        y: {
          ticks: { color: '#6b7280' },
          grid: { color: '#f3f4f6' },
          ...(extraOptions.scales?.y || {}),
        },
      },
      ...extraOptions,
    },
  });
}

// --- Utilities ---
function formatNumber(n) {
  if (n == null) return '0';
  return Number(n).toLocaleString();
}

function esc(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function groupByPackage(data) {
  const groups = {};
  data.forEach((d) => {
    if (!groups[d.package]) groups[d.package] = [];
    groups[d.package].push(d);
  });
  return groups;
}

function formatPeriodLabel(period, granularity) {
  if (granularity === 'month') return period; // YYYY-MM
  if (granularity === 'week') return period;   // YYYY-Www
  return period.slice(5); // MM-DD
}

function countryFlag(code) {
  if (!code || code.length !== 2) return '';
  const offset = 127397;
  const flag = String.fromCodePoint(
    ...code.toUpperCase().split('').map((c) => c.charCodeAt(0) + offset)
  );
  return `<span class="country-flag">${flag}</span>`;
}

// Country code to name mapping
const COUNTRY_NAMES = {
  US: 'United States', GB: 'United Kingdom', DE: 'Germany', FR: 'France',
  IT: 'Italy', ES: 'Spain', NL: 'Netherlands', BE: 'Belgium', AT: 'Austria',
  CH: 'Switzerland', SE: 'Sweden', NO: 'Norway', DK: 'Denmark', FI: 'Finland',
  PL: 'Poland', CZ: 'Czech Republic', RO: 'Romania', HU: 'Hungary',
  PT: 'Portugal', IE: 'Ireland', GR: 'Greece', BG: 'Bulgaria', HR: 'Croatia',
  SK: 'Slovakia', SI: 'Slovenia', LT: 'Lithuania', LV: 'Latvia', EE: 'Estonia',
  CA: 'Canada', MX: 'Mexico', BR: 'Brazil', AR: 'Argentina', CL: 'Chile',
  CO: 'Colombia', PE: 'Peru', VE: 'Venezuela', EC: 'Ecuador', UY: 'Uruguay',
  CN: 'China', JP: 'Japan', KR: 'South Korea', IN: 'India', ID: 'Indonesia',
  TH: 'Thailand', VN: 'Vietnam', PH: 'Philippines', MY: 'Malaysia', SG: 'Singapore',
  TW: 'Taiwan', HK: 'Hong Kong', AU: 'Australia', NZ: 'New Zealand',
  RU: 'Russia', UA: 'Ukraine', BY: 'Belarus', KZ: 'Kazakhstan',
  TR: 'Turkey', IL: 'Israel', AE: 'UAE', SA: 'Saudi Arabia', QA: 'Qatar',
  EG: 'Egypt', ZA: 'South Africa', NG: 'Nigeria', KE: 'Kenya', GH: 'Ghana',
  LU: 'Luxembourg', CY: 'Cyprus', MT: 'Malta', IS: 'Iceland',
  RS: 'Serbia', BA: 'Bosnia', ME: 'Montenegro', MK: 'North Macedonia', AL: 'Albania',
  GE: 'Georgia', AM: 'Armenia', AZ: 'Azerbaijan', UZ: 'Uzbekistan',
  PK: 'Pakistan', BD: 'Bangladesh', LK: 'Sri Lanka', MM: 'Myanmar', NP: 'Nepal',
  KH: 'Cambodia', LA: 'Laos', MN: 'Mongolia',
  MA: 'Morocco', TN: 'Tunisia', DZ: 'Algeria', LY: 'Libya',
  JO: 'Jordan', LB: 'Lebanon', IQ: 'Iraq', KW: 'Kuwait', BH: 'Bahrain', OM: 'Oman',
  CR: 'Costa Rica', PA: 'Panama', DO: 'Dominican Republic', PR: 'Puerto Rico',
  GT: 'Guatemala', HN: 'Honduras', SV: 'El Salvador', NI: 'Nicaragua',
  BO: 'Bolivia', PY: 'Paraguay', TT: 'Trinidad and Tobago', JM: 'Jamaica',
  ET: 'Ethiopia', TZ: 'Tanzania', UG: 'Uganda', RW: 'Rwanda', SN: 'Senegal',
  CI: 'Ivory Coast', CM: 'Cameroon', AO: 'Angola', MZ: 'Mozambique',
};

function countryName(code) {
  if (!code) return null;
  return COUNTRY_NAMES[code.toUpperCase()] || code;
}
