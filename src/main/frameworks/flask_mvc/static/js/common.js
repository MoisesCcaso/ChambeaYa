(function () {
    "use strict";

    const escapeMap = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
    };
    const iconSprite = "/static/icons.svg";

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (char) => escapeMap[char]);
    }

    function icon(name, className = "") {
        const safeName = String(name || "activity").replace(/[^a-z0-9-]/gi, "");
        const safeClass = String(className).replace(/[^a-z0-9 _-]/gi, "");
        return `<svg class="icon ${safeClass}" aria-hidden="true"><use href="${iconSprite}#icon-${safeName}"></use></svg>`;
    }

    async function api(path, options = {}) {
        const config = {
            credentials: "same-origin",
            headers: {},
            ...options,
        };

        if (config.body && !(config.body instanceof FormData) && typeof config.body !== "string") {
            config.headers["Content-Type"] = "application/json";
            config.body = JSON.stringify(config.body);
        }

        const response = await fetch(path, config);
        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json")
            ? await response.json()
            : await response.text();

        if (!response.ok) {
            const error = new Error(data?.error || "No se pudo completar la operación.");
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return data;
    }

    function toast(message, type = "success", timeout = 4200) {
        const region = document.getElementById("toast-region");
        if (!region) return;
        const element = document.createElement("div");
        element.className = `toast ${type}`;
        element.innerHTML = `
            <span aria-hidden="true">${icon(type === "error" ? "alert" : "check")}</span>
            <span>${escapeHTML(message)}</span>
            <button type="button" aria-label="Cerrar">${icon("x")}</button>
        `;
        element.querySelector("button").addEventListener("click", () => element.remove());
        region.appendChild(element);
        window.setTimeout(() => element.remove(), timeout);
    }

    function setButtonLoading(button, loading, label = "Procesando…") {
        if (!button) return;
        if (loading) {
            button.dataset.originalHtml = button.innerHTML;
            button.textContent = label;
            button.disabled = true;
        } else {
            if (button.dataset.originalHtml) {
                button.innerHTML = button.dataset.originalHtml;
                delete button.dataset.originalHtml;
            }
            button.disabled = false;
        }
    }

    function parseDate(value) {
        if (!value) return null;
        const text = String(value);
        const hasTimezone = /(?:Z|[+-]\d{2}:\d{2})$/i.test(text);
        const date = new Date(hasTimezone ? text : `${text}Z`);
        return Number.isNaN(date.getTime()) ? null : date;
    }

    function formatDate(value, includeTime = false) {
        if (!value) return "—";
        const date = parseDate(value);
        if (!date) return "—";
        return new Intl.DateTimeFormat("es-PE", {
            day: "2-digit",
            month: "short",
            year: "numeric",
            ...(includeTime ? { hour: "2-digit", minute: "2-digit" } : {}),
        }).format(date);
    }

    function relativeTime(value) {
        if (!value) return "";
        const date = parseDate(value);
        if (!date) return "";
        const seconds = Math.round((date.getTime() - Date.now()) / 1000);
        const abs = Math.abs(seconds);
        const formatter = new Intl.RelativeTimeFormat("es", { numeric: "auto" });
        if (abs < 60) return formatter.format(seconds, "second");
        if (abs < 3600) return formatter.format(Math.round(seconds / 60), "minute");
        if (abs < 86400) return formatter.format(Math.round(seconds / 3600), "hour");
        if (abs < 2592000) return formatter.format(Math.round(seconds / 86400), "day");
        return formatDate(value);
    }

    function initials(...parts) {
        return parts
            .filter(Boolean)
            .map((part) => String(part).trim()[0])
            .join("")
            .slice(0, 2)
            .toUpperCase() || "U";
    }

    function statusLabel(status) {
        const labels = {
            borrador: "Borrador",
            publicada: "Publicada",
            cerrada: "Cerrada",
            pendiente: "Pendiente",
            seleccionada: "Seleccionada",
            rechazada: "No seleccionada",
            cancelada: "Retirada",
            EN_CURSO: "En curso",
            FINALIZADA: "Finalizada",
        };
        return labels[status] || status || "—";
    }

    function statusBadge(status) {
        const key = String(status || "").toLowerCase();
        return `<span class="status-badge status-${escapeHTML(key)}">${escapeHTML(statusLabel(status))}</span>`;
    }

    function emptyState(title, description, iconName = "activity") {
        return `
            <div class="empty-state">
                <span class="empty-state-icon" aria-hidden="true">${icon(iconName)}</span>
                <h3>${escapeHTML(title)}</h3>
                <p>${escapeHTML(description)}</p>
            </div>
        `;
    }

    function splitComma(value) {
        return String(value || "")
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean);
    }

    window.Chambea = {
        api,
        emptyState,
        escapeHTML,
        formatDate,
        icon,
        initials,
        relativeTime,
        setButtonLoading,
        splitComma,
        statusBadge,
        statusLabel,
        toast,
    };
})();
