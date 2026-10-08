const API_URL = "/api/yoshis";

// DOM elements
const yoshiList = document.getElementById("yoshi-list");
const form = document.getElementById("yoshi-form");
const formTitle = document.getElementById("form-title");
const nameInput = document.getElementById("yoshi-name");
const colorInput = document.getElementById("yoshi-color");
const descriptionInput = document.getElementById("yoshi-description");
const imageInput = document.getElementById("yoshi-image");
const cancelButton = document.getElementById("cancel-button");

let editingYoshiId = null;

// -------------------------
// Helpers & API Wrapper
// -------------------------

async function requestApi(endpoint = "", options = {}) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    if (response.status !== 204) {
        return response.json();
    }
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getYoshiIcon(color = "") {
    const icons = {
        green: "🟢",
        red: "🔴",
        blue: "🔵",
        yellow: "🟡",
        gold: "🟡",
        pink: "🩷",
        purple: "🟣",
        orange: "🟠",
        black: "⚫",
        white: "⚪"
    };

    return icons[color.toLowerCase()] || "🥚";
}

// -------------------------
// IHM
// -------------------------

function renderYoshis(yoshis) {
    yoshiList.innerHTML = "";

    if (!yoshis || yoshis.length === 0) {
        yoshiList.innerHTML = `<p class="empty-message">No Yoshi here.</p>`;
        return;
    }

    yoshis.forEach((yoshi) => {
        const card = document.createElement("article");
        card.className = "yoshi-card";

        let imageHtml = "";
        const colorClass = yoshi.color ? yoshi.color.toLowerCase() : "";

        if (yoshi.image && yoshi.image.includes("yoshi_colors_asset_face")) {
            imageHtml = `
                <div class="yoshi-sprite-wrapper">
                    <div class="yoshi-sprite yoshi-sprite-${escapeHtml(colorClass)}"></div>
                </div>
            `;
        } else if (yoshi.image) {
            imageHtml = `
                <img class="yoshi-image" 
                     src="${escapeHtml(yoshi.image)}" 
                     alt="${escapeHtml(yoshi.name)}"
                     onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'yoshi-icon\\'>${getYoshiIcon(yoshi.color)}</div>';">
            `;
        } else {
            imageHtml = `<div class="yoshi-icon">${getYoshiIcon(yoshi.color)}</div>`;
        }

        card.innerHTML = `
            ${imageHtml}
            <h3>${escapeHtml(yoshi.name)}</h3>
            <p class="yoshi-color">Color: <strong>${escapeHtml(yoshi.color)}</strong></p>
            ${yoshi.description ? `<p class="yoshi-description">${escapeHtml(yoshi.description)}</p>` : ""}
            <div class="yoshi-actions">
                <button class="edit-button" data-id="${yoshi.id}">Edit</button>
                <button class="delete-button" data-id="${yoshi.id}">Kill</button>
            </div>
        `;

        yoshiList.appendChild(card);
    });
}

async function loadYoshis() {
    try {
        yoshiList.innerHTML = `<p class="empty-message">Loading Yoshis...</p>`;
        const yoshis = await requestApi();
        renderYoshis(yoshis);
    } catch (error) {
        console.error("Error loading :", error);
        yoshiList.innerHTML = `<p class="error-message">Impossible to load the Yoshis.</p>`;
    }
}

async function startEditYoshi(id) {
    try {
        const yoshi = await requestApi(`/${id}`);
        editingYoshiId = yoshi.id;

        nameInput.value = yoshi.name || "";
        colorInput.value = yoshi.color || "";
        descriptionInput.value = yoshi.description || "";
        imageInput.value = yoshi.image || "";

        formTitle.textContent = "Modify a Yoshi";
        cancelButton.hidden = false;
        nameInput.focus();
    } catch (error) {
        console.error("Error editing Yoshi :", error);
        alert("Impossible to load this Yoshi.");
    }
}

async function removeYoshi(id) {
    const confirmed = confirm("Are you sure to kill this lovely Yoshi ?");
    if (!confirmed) return;

    try {
        await requestApi(`/${id}`, { method: "DELETE" });
        await loadYoshis();
    } catch (error) {
        console.error("Error killing Yoshi :", error);
        alert("Impossible to delete this Yoshi. He's too strong");
    }
}

function resetForm() {
    editingYoshiId = null;
    form.reset();
    formTitle.textContent = "Add a Yoshi";
    cancelButton.hidden = true;
}

// -------------------------
// Events
// -------------------------

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        name: nameInput.value.trim(),
        color: colorInput.value.trim(),
        description: descriptionInput.value.trim(),
        image: imageInput.value.trim()
    };

    if (!payload.name || !payload.color) return;

    try {
        if (editingYoshiId === null) {
            await requestApi("", {
                method: "POST",
                body: JSON.stringify(payload)
            });
        } else {
            await requestApi(`/${editingYoshiId}`, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
        }

        resetForm();
        await loadYoshis();
    } catch (error) {
        console.error("Error saving Yoshi :", error);
        alert("Yoshi just ate the server. Sorry about that...");
    }
});

yoshiList.addEventListener("click", (event) => {
    const editBtn = event.target.closest(".edit-button");
    const deleteBtn = event.target.closest(".delete-button");

    if (editBtn) startEditYoshi(Number(editBtn.dataset.id));
    if (deleteBtn) removeYoshi(Number(deleteBtn.dataset.id));
});

cancelButton.addEventListener("click", resetForm);

loadYoshis();