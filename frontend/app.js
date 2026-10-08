const API_URL = "/api/yoshis";
const yoshiList = document.getElementById("yoshi-list");
const form = document.getElementById("yoshi-form");
const formTitle = document.getElementById("form-title");
const nameInput = document.getElementById("yoshi-name");
const colorInput = document.getElementById("yoshi-color");
const cancelButton = document.getElementById("cancel-button");
const descriptionInput = document.getElementById("yoshi-description");
const imageInput = document.getElementById("yoshi-image");
let editingYoshiId = null;


// -------------------------
// API
// -------------------------

async function getYoshis() {
    const response = await fetch(API_URL);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}


async function createYoshi(name, color, description, image) {
    const response = await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            color,
            description,
            image
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}

async function updateYoshi(id, name, color, description, image) {
    const response = await fetch(`${API_URL}/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            name,
            color,
            description,
            image
        })
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}

async function deleteYoshi(id) {
    const response = await fetch(`${API_URL}/${id}`, {
        method: "DELETE"
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
}


// -------------------------
// Display incredible Yoshis
// -------------------------

function getYoshiIcon(color) {
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
function renderYoshis(yoshis) {
    yoshiList.innerHTML = "";

    if (yoshis.length === 0) {
        yoshiList.innerHTML = `<p class="empty-message">No Yoshi here.</p>`;
        return;
    }

    yoshis.forEach((yoshi) => {
        const card = document.createElement("article");
        card.className = "yoshi-card";

        let imageHtml = "";

        if (yoshi.image && yoshi.image.includes("yoshi_colors_asset_face")) {
            const colorClass = yoshi.color.toLowerCase();
            imageHtml = `
                <div class="yoshi-sprite-wrapper">
                    <div class="yoshi-sprite yoshi-sprite-${escapeHtml(colorClass)}"></div>
                </div>
            `;
        } else if (yoshi.image) {
            imageHtml = `
                <img class="yoshi-image" src="${escapeHtml(yoshi.image)}" alt="${escapeHtml(yoshi.name)}"
                     onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\"yoshi-icon\">${getYoshiIcon(yoshi.color)}</div>';">
            `;
        } else {
            // Émoji par défaut
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

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


// -------------------------
// Loading 
// -------------------------

async function loadYoshis() {
    try {
        yoshiList.innerHTML = `
            <p>Chargement des Yoshis...</p>
        `;
        const yoshis = await getYoshis();
        renderYoshis(yoshis);
    } catch (error) {
        console.error(error);
        yoshiList.innerHTML = `
            <p class="error-message">
                Impossible to load the Yoshis.
            </p>
        `;
    }
}


// -------------------------
// Form
// -------------------------

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = nameInput.value.trim();
    const color = colorInput.value.trim();
    const description = descriptionInput.value.trim();
    const image = imageInput.value.trim();
    if (!name || !color) {
        return;
    }

    try {
       if (editingYoshiId === null) {
        await createYoshi(
            name,
            color,
            description,
            image
        );
    } else {
        await updateYoshi(
            editingYoshiId,
            name,
            color,
            description,
            image
        );
    }
    resetForm();
    await loadYoshis();
    } catch (error) {
        console.error(error);
        alert("Yoshi just ate the server. Sorry about that...");
    }
});


// -------------------------
// Modifier
// -------------------------

async function startEditYoshi(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const yoshi = await response.json();
        editingYoshiId = yoshi.id;
        nameInput.value = yoshi.name;
        colorInput.value = yoshi.color;
        descriptionInput.value = yoshi.description || "";
        imageInput.value = yoshi.image || "";
        formTitle.textContent = "Modify a Yoshi";
        cancelButton.hidden = false;
        nameInput.focus();
    } catch (error) {
        console.error(error);
        alert("Impossible to load this Yoshi.");
    }
}


// -------------------------
// Delete poor Yoshis
// -------------------------

async function removeYoshi(id) {
    const confirmed = confirm(
        "Are you sure to kill this lovely Yoshi ?"
    );

    if (!confirmed) {
        return;
    }

    try {
        await deleteYoshi(id);
        await loadYoshis();

    } catch (error) {
        console.error(error);
        alert("Impossible to delete this Yoshi. He's too strong");
    }
}


// -------------------------
// Cards actions
// -------------------------

yoshiList.addEventListener("click", (event) => {
    const editButton = event.target.closest(".edit-button");
    const deleteButton = event.target.closest(".delete-button");

    if (editButton) {
        startEditYoshi(Number(editButton.dataset.id));
    }

    if (deleteButton) {
        removeYoshi(Number(deleteButton.dataset.id));
    }
});


// -------------------------
// Cancel editing
// -------------------------

cancelButton.addEventListener("click", () => {
    resetForm();
});


function resetForm() {
    editingYoshiId = null;
    form.reset();
    formTitle.textContent = "Add a Yoshi";
    cancelButton.hidden = true;
}


// -------------------------
// Start
// -------------------------

loadYoshis();
