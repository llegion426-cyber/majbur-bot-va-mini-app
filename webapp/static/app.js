const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand();

const initData = tg?.initData || "";

const state = {
  regions: [],
  currentRegion: null,
  listings: [],
  isAdmin: false,
  editingId: null,
};

const el = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Telegram-Init-Data": initData,
      ...(options.headers || {}),
    },
  });
  if (!res.ok) throw new Error(await res.text());
  return res.status === 204 ? null : res.json();
}

async function init() {
  try {
    const me = await api("/me");
    state.isAdmin = !!me.is_admin;
  } catch (e) {
    state.isAdmin = false;
  }

  state.regions = await api("/regions");
  renderRegions();

  el("addBtn").hidden = !state.isAdmin;
  el("addBtn").onclick = () => openForm();

  el("backBtn").onclick = showRegions;
  document.querySelectorAll("[data-close]").forEach((b) => (b.onclick = closeModals));

  el("listingForm").onsubmit = onSubmitForm;
  el("fPhoto").onchange = onPhotoChange;
  el("editListingBtn").onclick = () => openForm(state.currentListing);
  el("deleteListingBtn").onclick = onDeleteListing;
}

function renderRegions() {
  const grid = el("regionsGrid");
  grid.innerHTML = "";
  state.regions.forEach((r) => {
    const card = document.createElement("div");
    card.className = "region-card";
    card.innerHTML = `<div class="region-name">${r.name}</div><div class="region-count">E'lonlarni ko'rish</div>`;
    card.onclick = () => openRegion(r);
    grid.appendChild(card);
  });
}

async function openRegion(region) {
  state.currentRegion = region;
  el("pageTitle").textContent = region.name;
  el("pageSubtitle").textContent = "Arenda e'lonlari";
  el("backBtn").hidden = false;
  el("regionsView").hidden = true;
  el("listingsView").hidden = false;

  state.listings = await api(`/listings?region_id=${region.id}`);
  renderListings();
}

function renderListings() {
  const grid = el("listingsGrid");
  const empty = el("emptyState");
  grid.innerHTML = "";
  if (state.listings.length === 0) {
    empty.hidden = false;
    return;
  }
  empty.hidden = true;
  state.listings.forEach((l) => {
    const card = document.createElement("div");
    card.className = "listing-card";
    const thumbStyle = l.photo_base64 ? `style="background-image:url('${l.photo_base64}')"` : "";
    card.innerHTML = `
      <div class="listing-thumb" ${thumbStyle}>${l.photo_base64 ? "" : "🏠"}</div>
      <div class="listing-info">
        <div class="listing-title">${l.title}</div>
        <div class="listing-address">${l.address || ""}</div>
        <div class="listing-price">${formatPrice(l.price)} so'm</div>
      </div>
    `;
    card.onclick = () => openDetail(l);
    grid.appendChild(card);
  });
}

function showRegions() {
  el("pageTitle").textContent = "Hududni tanlang";
  el("pageSubtitle").textContent = "Arenda uy-joy e'lonlari";
  el("backBtn").hidden = true;
  el("regionsView").hidden = false;
  el("listingsView").hidden = true;
}

function openDetail(listing) {
  state.currentListing = listing;
  el("detailPhoto").style.backgroundImage = listing.photo_base64 ? `url('${listing.photo_base64}')` : "none";
  el("detailPhoto").textContent = listing.photo_base64 ? "" : "🏠";
  el("detailStatus").textContent = listing.status === "band" ? "🔴 Band" : "🟢 Bo'sh";
  el("detailStatus").className = `status-seal ${listing.status}`;
  el("detailTitle").textContent = listing.title;
  el("detailAddress").textContent = listing.address || "";
  el("detailPrice").textContent = `${formatPrice(listing.price)} so'm`;
  el("detailDescription").textContent = listing.description || "";
  el("adminActions").hidden = !state.isAdmin;
  el("detailModal").hidden = false;
}

function closeModals() {
  el("detailModal").hidden = true;
  el("formModal").hidden = true;
  state.editingId = null;
}

function openForm(listing = null) {
  closeModals();
  state.editingId = listing ? listing.id : null;
  el("formTitle").textContent = listing ? "E'lonni tahrirlash" : "Yangi e'lon";

  const regionSelect = el("fRegion");
  regionSelect.innerHTML = state.regions.map((r) => `<option value="${r.id}">${r.name}</option>`).join("");
  regionSelect.value = listing ? listing.region_id : state.currentRegion?.id || state.regions[0]?.id;
