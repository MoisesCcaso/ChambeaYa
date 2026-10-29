(function () {
    "use strict";

    const C = window.Chambea;
    const $ = (selector, root = document) => root.querySelector(selector);
    const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

    const state = {
        user: null,
        profile: null,
        opportunities: [],
        matches: [],
        applications: [],
        openings: [],
        practices: [],
        notifications: [],
        certificates: [],
        studentSkills: [],
        studentEducation: [],
        applicationFilter: "todas",
        openingFilter: "todas",
        selectedOpeningId: null,
        currentPracticeId: null,
    };

    const pageMeta = {
        resumen: ["Resumen", "Panel personal"],
        perfil: ["Mi perfil", "Configuración"],
        oportunidades: ["Oportunidades", "Explorar"],
        sugerencias: ["Para ti", "Matching"],
        postulaciones: ["Mis postulaciones", "Seguimiento"],
        convocatorias: ["Convocatorias", "Selección"],
        practicas: ["Prácticas", "Seguimiento"],
        certificados: ["Certificados", "Documentos"],
        notificaciones: ["Notificaciones", "Actividad"],
    };

    async function safeApi(path, fallback = null) {
        try {
            return await C.api(path);
        } catch (error) {
            if (error.status === 404) return fallback;
            throw error;
        }
    }

    function confirmAction(title, message, confirmLabel = "Confirmar", danger = false) {
        const dialog = $("#confirmation-dialog");
        const accept = $("#confirmation-accept");
        $("#confirmation-title").textContent = title;
        $("#confirmation-message").textContent = message;
        accept.textContent = confirmLabel;
        accept.className = `button ${danger ? "button-danger" : "button-primary"}`;

        return new Promise((resolve) => {
            let confirmed = false;
            const acceptAction = () => {
                confirmed = true;
                dialog.close();
            };
            const finish = () => {
                accept.removeEventListener("click", acceptAction);
                resolve(confirmed);
            };
            accept.addEventListener("click", acceptAction);
            dialog.addEventListener("close", finish, { once: true });
            dialog.showModal();
        });
    }

    function role() {
        return state.user?.tipo;
    }

    function profileName() {
        if (role() === "empresa") {
            return state.profile?.razon_social || "Mi empresa";
        }
        const fullName = [state.profile?.nombres, state.profile?.apellidos]
            .filter(Boolean)
            .join(" ");
        return fullName || "Mi perfil";
    }

    function profileInitials() {
        if (role() === "empresa") return C.initials(state.profile?.razon_social);
        return C.initials(state.profile?.nombres, state.profile?.apellidos);
    }

    function configureRole() {
        $$("[data-role]").forEach((element) => {
            element.hidden = element.dataset.role !== role();
        });
        $("#sidebar-role").textContent = role() === "empresa" ? "Empresa" : "Practicante";
        $("#topbar-email").textContent = state.user.email;
        updateIdentity();
    }

    function updateIdentity() {
        const name = profileName();
        const initials = profileInitials();
        $("#sidebar-name").textContent = name;
        $("#sidebar-avatar").textContent = initials;
        $("#topbar-avatar").textContent = initials;
    }

    function openSidebar() {
        $("#sidebar").classList.add("open");
        $("#sidebar-overlay").classList.add("visible");
    }

    function closeSidebar() {
        $("#sidebar").classList.remove("open");
        $("#sidebar-overlay").classList.remove("visible");
    }

    function navigate(view, updateHash = true) {
        if (
            !state.profile &&
            !["resumen", "perfil", "notificaciones"].includes(view)
        ) {
            view = "perfil";
            C.toast(
                role() === "empresa"
                    ? "Completa los datos de tu empresa antes de crear convocatorias."
                    : "Completa tu perfil antes de continuar.",
                "error"
            );
        }
        const panel = $(`[data-view-panel="${view}"]`);
        if (!panel || panel.hidden) return;
        $$(".app-view").forEach((item) => item.classList.toggle("active", item === panel));
        $$(".nav-item").forEach((item) => {
            item.classList.toggle("active", item.dataset.view === view);
        });
        const [title, context] = pageMeta[view] || ["ChambeaYa", "Panel"];
        $("#page-title").textContent = title;
        $("#page-context").textContent = context;
        if (updateHash) history.replaceState(null, "", `#${view}`);
        closeSidebar();
        window.scrollTo({ top: 0, behavior: "smooth" });

        if (view === "notificaciones") renderNotifications();
        if (view === "certificados") renderCertificates();
    }

    function loadingMarkup() {
        return `<div class="loading-rows"><div class="loading-line"></div><div class="loading-line"></div><div class="loading-line"></div></div>`;
    }

    function displayFileName(fileName) {
        return String(fileName || "Archivo").replace(/^[a-f0-9]{32}_/i, "");
    }

    async function loadProfile() {
        state.profile = await safeApi("/perfil/me", null);
        state.studentSkills = [...(state.profile?.habilidades || [])];
        state.studentEducation = [...(state.profile?.formacion_educativa || [])];
        updateIdentity();
        renderProfile();
    }

    async function loadNotifications() {
        state.notifications = await C.api("/notificaciones");
        updateUnread();
        renderNotifications();
    }

    async function loadPractices() {
        state.practices = await C.api("/practicas");
        renderPractices();
    }

    async function loadOpportunities(query = "") {
        const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
        state.opportunities = await C.api(`/convocatorias${suffix}`);
        renderOpportunities();
    }

    async function loadApplications() {
        state.applications = await C.api("/postulaciones/me");
        renderApplications();
    }

    async function loadMatches() {
        state.matches = await C.api("/matching/sugerencias");
        renderMatches();
    }

    async function loadOpenings() {
        state.openings = await C.api("/convocatorias/mis");
        renderOpenings();
    }

    async function loadCertificates() {
        if (role() !== "practicante") return;
        const results = await Promise.all(
            state.practices.map(async (practice) => {
                try {
                    return await C.api(`/certificados/practica/${practice.id}`);
                } catch (error) {
                    if (error.status === 404) return null;
                    throw error;
                }
            })
        );
        state.certificates = results.filter(Boolean);
        renderCertificates();
    }

    function updateUnread() {
        const unread = state.notifications.filter((item) => !item.leida).length;
        const sidebarCount = $("#sidebar-unread");
        const topbarCount = $("#topbar-unread");
        sidebarCount.textContent = unread > 99 ? "99+" : unread;
        sidebarCount.hidden = unread === 0;
        topbarCount.hidden = unread === 0;
    }

    function renderDashboard() {
        const isCompany = role() === "empresa";
        const firstName = isCompany
            ? state.profile?.razon_social || "tu empresa"
            : state.profile?.nombres || "de nuevo";
        $("#welcome-title").textContent = `Hola, ${firstName}`;
        $("#welcome-description").textContent = isCompany
            ? "Revisa el avance de tus convocatorias y procesos de selección."
            : "Continúa construyendo tu experiencia profesional.";
        $("#welcome-eyebrow").textContent = isCompany
            ? "Gestión de talento"
            : "Tu espacio de trabajo";

        const primary = $("#primary-action");
        delete primary.dataset.action;
        delete primary.dataset.targetView;
        if (!state.profile) {
            primary.innerHTML = `${C.icon("user")} Completar perfil`;
            primary.dataset.targetView = "perfil";
        } else if (isCompany) {
            primary.innerHTML = `${C.icon("plus")} Nueva convocatoria`;
            primary.dataset.action = "new-opening";
        } else {
            primary.innerHTML = `${C.icon("search")} Explorar oportunidades`;
            primary.dataset.targetView = "oportunidades";
        }

        const metrics = isCompany
            ? [
                ["Convocatorias", state.openings.length, "Total registradas"],
                ["Publicadas", state.openings.filter((x) => x.estado === "publicada").length, "Recibiendo candidatos"],
                ["Prácticas", state.practices.length, "Procesos iniciados"],
                ["No leídas", state.notifications.filter((x) => !x.leida).length, "Notificaciones"],
            ]
            : [
                ["Reputación", `${Math.round(state.profile?.score_reputacion || 0)}%`, "Perfil profesional"],
                ["Postulaciones", state.applications.length, "Procesos registrados"],
                ["Prácticas", state.practices.length, "Seguimiento activo"],
                ["Certificados", state.certificates.length, "Documentos emitidos"],
            ];
        $("#dashboard-metrics").innerHTML = metrics
            .map(
                ([label, value, note]) => `
                <div class="metric">
                    <span>${C.escapeHTML(label)}</span>
                    <strong>${C.escapeHTML(value)}</strong>
                    <small>${C.escapeHTML(note)}</small>
                </div>`
            )
            .join("");

        renderDashboardActivity();
        renderDashboardProgress();
        renderDashboardList();
    }

    function renderDashboardActivity() {
        const container = $("#dashboard-activity");
        const recent = state.notifications.slice(0, 4);
        if (!recent.length) {
            container.innerHTML = C.emptyState(
                "Aún no hay actividad",
                "Las novedades de tus procesos aparecerán aquí.",
                "activity"
            );
            return;
        }
        container.innerHTML = recent
            .map(
                (item) => `
                <div class="list-row">
                    <span class="row-mark">${notificationSymbol(item.tipo)}</span>
                    <span><strong>${C.escapeHTML(item.mensaje)}</strong><small>${C.escapeHTML(notificationCategory(item.tipo))}</small></span>
                    <span class="row-time">${C.escapeHTML(C.relativeTime(item.created_at))}</span>
                </div>`
            )
            .join("");
    }

    function renderDashboardProgress() {
        const panel = $("#dashboard-progress");
        if (role() === "empresa") {
            const verified = Boolean(state.profile?.verificada);
            const hasOpenings = state.openings.length > 0;
            const hasPublished = state.openings.some((x) => x.estado === "publicada");
            const score = [verified, hasOpenings, hasPublished].filter(Boolean).length / 3 * 100;
            panel.innerHTML = `
                <h3>Preparación de la empresa</h3>
                <p>Completa estos pasos para gestionar candidatos.</p>
                <div class="score-value">${Math.round(score)}%</div>
                <div class="progress-line"><span style="width:${score}%"></span></div>
                <ul class="progress-checklist">
                    <li class="${verified ? "done" : ""}"><i>${verified ? C.icon("check") : ""}</i> Empresa verificada</li>
                    <li class="${hasOpenings ? "done" : ""}"><i>${hasOpenings ? C.icon("check") : ""}</i> Primera convocatoria creada</li>
                    <li class="${hasPublished ? "done" : ""}"><i>${hasPublished ? C.icon("check") : ""}</i> Convocatoria publicada</li>
                </ul>`;
            return;
        }
        const score = Math.round(state.profile?.score_reputacion || 0);
        const hasName = Boolean(state.profile?.nombres && state.profile?.apellidos);
        const hasSkills = Boolean(state.profile?.habilidades?.length);
        const verified = Boolean(state.profile?.identidad_verificada);
        panel.innerHTML = `
            <h3>Fortaleza del perfil</h3>
            <p>Un perfil completo mejora tus recomendaciones.</p>
            <div class="score-value">${score}%</div>
            <div class="progress-line"><span style="width:${score}%"></span></div>
            <ul class="progress-checklist">
                <li class="${hasName ? "done" : ""}"><i>${hasName ? C.icon("check") : ""}</i> Información personal</li>
                <li class="${hasSkills ? "done" : ""}"><i>${hasSkills ? C.icon("check") : ""}</i> Habilidades registradas</li>
                <li class="${verified ? "done" : ""}"><i>${verified ? C.icon("check") : ""}</i> Identidad verificada</li>
            </ul>`;
    }

    function renderDashboardList() {
        const isCompany = role() === "empresa";
        const items = isCompany ? state.openings.slice(0, 5) : state.opportunities.slice(0, 5);
        $("#dashboard-list-title").textContent = isCompany
            ? "Tus convocatorias"
            : "Oportunidades recientes";
        $("#dashboard-list-description").textContent = isCompany
            ? "Actividad actual de tus oportunidades."
            : "Convocatorias disponibles para postular.";
        $("#dashboard-list-action").textContent = isCompany ? "Administrar" : "Explorar";
        $("#dashboard-list-action").dataset.targetView = isCompany ? "convocatorias" : "oportunidades";
        $("#dashboard-list-head").innerHTML = isCompany
            ? "<tr><th>Convocatoria</th><th>Estado</th><th>Fecha</th></tr>"
            : "<tr><th>Convocatoria</th><th>Habilidades</th><th>Estado</th></tr>";
        $("#dashboard-list-body").innerHTML = items.length
            ? items
                  .map((item) =>
                      isCompany
                          ? `<tr><td><strong>${C.escapeHTML(item.titulo)}</strong><small>#${item.id}</small></td><td>${C.statusBadge(item.estado)}</td><td>${C.formatDate(item.fecha_publicacion)}</td></tr>`
                          : `<tr><td><strong>${C.escapeHTML(item.titulo)}</strong><small>${C.escapeHTML(item.descripcion || "Sin descripción")}</small></td><td>${C.escapeHTML((item.habilidades_requeridas || []).slice(0, 2).join(", ") || "—")}</td><td>${C.statusBadge(item.estado)}</td></tr>`
                  )
                  .join("")
            : `<tr><td colspan="3">${C.emptyState(
                  isCompany ? "Sin convocatorias" : "Sin oportunidades",
                  isCompany
                      ? "Crea tu primera convocatoria para comenzar."
                      : "No encontramos convocatorias publicadas.",
                  isCompany ? "briefcase" : "search"
              )}</td></tr>`;
    }

    function renderProfile() {
        const summary = $("#profile-summary");
        const isCompany = role() === "empresa";
        summary.innerHTML = `
            <span class="avatar">${C.escapeHTML(profileInitials())}</span>
            <h3>${C.escapeHTML(profileName())}</h3>
            <p>${C.escapeHTML(state.user?.email || "")}</p>
            <div class="profile-score">
                <span>${isCompany ? "Estado de verificación" : "Reputación del perfil"}</span>
                <strong>${isCompany ? (state.profile?.verificada ? "Verificada" : "Pendiente") : `${Math.round(state.profile?.score_reputacion || 0)}%`}</strong>
            </div>`;

        if (isCompany) {
            const form = $("#company-profile-form");
            form.elements.razon_social.value = state.profile?.razon_social || "";
            form.elements.ruc.value = state.profile?.ruc || "";
        } else {
            const form = $("#student-profile-form");
            form.elements.nombres.value = state.profile?.nombres || "";
            form.elements.apellidos.value = state.profile?.apellidos || "";
            form.elements.dni.value = state.profile?.dni || "";
            form.elements.carnet_universitario.value =
                state.profile?.carnet_universitario || "";
            renderTags();
        }
    }

    function renderTags() {
        $("#skills-list").innerHTML = state.studentSkills
            .map(
                (value, index) =>
                    `<span class="tag">${C.escapeHTML(value)}<button type="button" data-remove-skill="${index}" aria-label="Quitar">${C.icon("x")}</button></span>`
            )
            .join("");
        $("#education-list").innerHTML = state.studentEducation
            .map(
                (value, index) =>
                    `<span class="tag">${C.escapeHTML(value)}<button type="button" data-remove-education="${index}" aria-label="Quitar">${C.icon("x")}</button></span>`
            )
            .join("");
    }

    function renderOpportunities() {
        const list = $("#opportunity-list");
        if (!state.opportunities.length) {
            list.innerHTML = C.emptyState(
                "No encontramos resultados",
                "Prueba con otra palabra o vuelve más tarde.",
                "search"
            );
            $("#opportunity-detail").innerHTML = C.emptyState(
                "Sin convocatoria seleccionada",
                "Los detalles aparecerán aquí.",
                "briefcase"
            );
            return;
        }
        if (!state.selectedOpeningId || !state.opportunities.some((x) => x.id === state.selectedOpeningId)) {
            state.selectedOpeningId = state.opportunities[0].id;
        }
        list.innerHTML = state.opportunities
            .map(
                (item) => `
                <button class="result-item ${item.id === state.selectedOpeningId ? "active" : ""}" data-select-opening="${item.id}">
                    <h3>${C.escapeHTML(item.titulo)}</h3>
                    <p>Convocatoria #${item.id}</p>
                    <span class="mini-tags">${(item.habilidades_requeridas || [])
                        .slice(0, 3)
                        .map((skill) => `<span>${C.escapeHTML(skill)}</span>`)
                        .join("")}</span>
                </button>`
            )
            .join("");
        renderOpportunityDetail(state.selectedOpeningId);
    }

    function renderOpportunityDetail(id) {
        const item = state.opportunities.find((opening) => opening.id === Number(id));
        if (!item) return;
        const application = state.applications.find(
            (candidate) => candidate.convocatoria_id === item.id
        );
        const activeApplication =
            application && application.estado !== "cancelada" ? application : null;
        $("#opportunity-detail").innerHTML = `
            <p class="eyebrow">Convocatoria activa</p>
            <h2>${C.escapeHTML(item.titulo)}</h2>
            <p class="detail-meta">Referencia #${item.id} · Publicada ${C.formatDate(item.fecha_publicacion)}</p>
            <div class="detail-block">
                <h3>Descripción</h3>
                <p>${C.escapeHTML(item.descripcion || "La empresa no añadió una descripción.")}</p>
            </div>
            <div class="detail-block">
                <h3>Habilidades requeridas</h3>
                <div class="mini-tags">${(item.habilidades_requeridas || [])
                    .map((skill) => `<span>${C.escapeHTML(skill)}</span>`)
                    .join("") || "<span>No especificadas</span>"}</div>
            </div>
            <div class="detail-block">
                <h3>Beneficios</h3>
                <ul>${(item.beneficios || [])
                    .map((benefit) => `<li>${C.escapeHTML(benefit)}</li>`)
                    .join("") || "<li>No especificados</li>"}</ul>
            </div>
            <div class="detail-actions">
                ${
                    activeApplication
                        ? `${C.statusBadge(activeApplication.estado)}`
                        : `<button class="button button-primary" data-apply-opening="${item.id}">${C.icon("send")} ${application ? "Postular nuevamente" : "Postular ahora"}</button>`
                }
            </div>`;
    }

    function renderMatches() {
        const list = $("#match-list");
        if (!state.matches.length) {
            list.innerHTML = C.emptyState(
                "Aún no hay recomendaciones",
                "Añade habilidades a tu perfil o actualiza el cálculo.",
                "sparkles"
            );
            return;
        }
        list.innerHTML = state.matches
            .map((match) => {
                const opening = match.convocatoria || {};
                const application = state.applications.find(
                    (item) =>
                        item.convocatoria_id === match.convocatoria_id &&
                        item.estado !== "cancelada"
                );
                return `
                    <article class="match-row">
                        <span class="match-score">${Math.round(match.score_compatibilidad)}%</span>
                        <div class="match-main">
                            <h3>${C.escapeHTML(opening.titulo || `Convocatoria #${match.convocatoria_id}`)}</h3>
                            <p>${C.escapeHTML(opening.descripcion || "Oportunidad recomendada según tus habilidades.")}</p>
                            <span class="mini-tags">${(opening.beneficios || [])
                                .slice(0, 2)
                                .map((item) => `<span>${C.escapeHTML(item)}</span>`)
                                .join("")}</span>
                        </div>
                        <div class="match-skills">
                            <span>Coincidencias</span>
                            <div class="mini-tags">${(match.habilidades_coincidentes || [])
                                .map((item) => `<span>${C.escapeHTML(item)}</span>`)
                                .join("") || "<span>Perfil general</span>"}</div>
                        </div>
                        ${
                            application
                                ? C.statusBadge(application.estado)
                                : `<button class="button button-secondary button-small" data-apply-opening="${match.convocatoria_id}">${C.icon("send")} Postular</button>`
                        }
                    </article>`;
            })
            .join("");
    }

    function renderApplications() {
        const filtered =
            state.applicationFilter === "todas"
                ? state.applications
                : state.applications.filter((item) => item.estado === state.applicationFilter);
        $("#applications-table").innerHTML = filtered.length
            ? filtered
                  .map(
                      (item) => `
                    <tr>
                        <td><strong>${C.escapeHTML(item.convocatoria?.titulo || `Convocatoria #${item.convocatoria_id}`)}</strong><small>Postulación #${item.id}</small></td>
                        <td>${C.statusBadge(item.estado)}</td>
                        <td>#${item.convocatoria_id}</td>
                        <td class="align-right"><div class="table-actions">
                            ${item.estado === "pendiente" ? `<button class="table-action danger" data-cancel-application="${item.id}">${C.icon("x")} Retirar</button>` : ""}
                            ${item.estado === "cancelada" && item.convocatoria?.estado === "publicada" ? `<button class="table-action" data-reapply-opening="${item.convocatoria_id}">${C.icon("undo")} Volver a postular</button>` : ""}
                        </div></td>
                    </tr>`
                  )
                  .join("")
            : `<tr><td colspan="4">${C.emptyState(
                  "No hay postulaciones",
                  "Los procesos con este estado aparecerán aquí.",
                  "send"
              )}</td></tr>`;
    }

    function renderOpenings() {
        const filtered =
            state.openingFilter === "todas"
                ? state.openings
                : state.openings.filter((item) => item.estado === state.openingFilter);
        $("#openings-table").innerHTML = filtered.length
            ? filtered
                  .map(
                      (item) => `
                    <tr>
                        <td><strong>${C.escapeHTML(item.titulo)}</strong><small>${C.escapeHTML((item.habilidades_requeridas || []).join(", ") || "Sin habilidades definidas")}</small></td>
                        <td>${C.statusBadge(item.estado)}</td>
                        <td>${C.formatDate(item.fecha_publicacion)}</td>
                        <td class="align-right"><div class="table-actions">
                            ${item.estado === "borrador" ? `<button class="table-action" data-edit-opening="${item.id}">${C.icon("edit")} Editar</button><button class="table-action" data-publish-opening="${item.id}">${C.icon("send")} Publicar</button>` : ""}
                            ${item.estado === "publicada" ? `<button class="table-action" data-candidates-opening="${item.id}">${C.icon("users")} Candidatos</button><button class="table-action danger" data-close-opening="${item.id}">${C.icon("x")} Cerrar</button>` : ""}
                            ${item.estado === "cerrada" ? `<button class="table-action" data-candidates-opening="${item.id}">${C.icon("users")} Candidatos</button><button class="table-action" data-reopen-opening="${item.id}">${C.icon("refresh")} Reabrir</button>` : ""}
                            <button class="table-action" data-duplicate-opening="${item.id}">${C.icon("copy")} Duplicar</button>
                            ${item.estado === "borrador" ? `<button class="table-action danger" data-delete-opening="${item.id}">${C.icon("trash")} Eliminar</button>` : ""}
                        </div></td>
                    </tr>`
                  )
                  .join("")
            : `<tr><td colspan="4">${C.emptyState(
                  "Sin convocatorias",
                  "Crea una convocatoria para empezar a recibir postulaciones.",
                  "briefcase"
              )}</td></tr>`;
    }

    function practiceTitle(practice) {
        if (role() === "practicante") {
            const application = state.applications.find(
                (item) => item.id === practice.postulacion_id
            );
            return application?.convocatoria?.titulo || `Práctica #${practice.id}`;
        }
        return `Práctica #${practice.id}`;
    }

    function renderPractices() {
        const list = $("#practice-list");
        if (!state.practices.length) {
            list.innerHTML = C.emptyState(
                "Aún no hay prácticas",
                role() === "empresa"
                    ? "Inicia una práctica desde un candidato seleccionado."
                    : "Tu práctica aparecerá cuando una empresa inicie el proceso.",
                "clipboard"
            );
            return;
        }
        list.innerHTML = state.practices
            .map(
                (item) => `
                <article class="practice-row">
                    <div><h3>${C.escapeHTML(practiceTitle(item))}</h3><p>Postulación #${item.postulacion_id}</p></div>
                    <div class="row-stat"><span>Estado</span>${C.statusBadge(item.estado)}</div>
                    <div class="row-stat"><span>Referencia</span><strong>#${item.id}</strong></div>
                    <button class="button button-secondary button-small" data-view-practice="${item.id}">${C.icon("eye")} Ver seguimiento</button>
                </article>`
            )
            .join("");
    }

    function renderCertificates() {
        const list = $("#certificate-list");
        if (!state.certificates.length) {
            list.innerHTML = C.emptyState(
                "Sin certificados emitidos",
                "Cuando finalices una práctica aprobada, encontrarás aquí tu documento.",
                "certificate"
            );
            return;
        }
        list.innerHTML = state.certificates
            .map(
                (item) => `
                <article class="certificate-row">
                    <div><h3>Certificado de práctica #${item.practica_id}</h3><p>Código ${C.escapeHTML(item.codigo_qr?.valor || "—")}</p></div>
                    <div class="row-stat"><span>Estado</span>${C.statusBadge("verificada")}</div>
                    <div class="row-stat"><span>Referencia</span><strong>#${item.id}</strong></div>
                    <div class="table-actions">
                        <a class="button button-secondary button-small" href="${C.escapeHTML(item.documento?.url)}" target="_blank" rel="noopener">${C.icon("download")} PDF</a>
                        <a class="button button-secondary button-small" href="${C.escapeHTML(item.codigo_qr?.imagen_url)}" target="_blank" rel="noopener">${C.icon("eye")} QR</a>
                    </div>
                </article>`
            )
            .join("");
    }

    function notificationSymbol(type) {
        if (type?.includes("CERTIFICADO")) return C.icon("certificate");
        if (type?.includes("EVALUACION")) return C.icon("clipboard");
        if (type?.includes("SUGERENCIAS")) return C.icon("sparkles");
        if (type?.includes("POSTULACION")) return C.icon("send");
        return C.icon("bell");
    }

    function notificationCategory(type) {
        if (type?.includes("CERTIFICADO")) return "Certificación";
        if (type?.includes("EVALUACION")) return "Evaluación";
        if (type?.includes("SUGERENCIAS")) return "Matching";
        if (type?.includes("POSTULACION")) return "Postulación";
        return "Actividad";
    }

    function renderNotifications() {
        const list = $("#notification-list");
        if (!state.notifications.length) {
            list.innerHTML = C.emptyState(
                "Todo está al día",
                "No tienes notificaciones por revisar.",
                "bell"
            );
            return;
        }
        list.innerHTML = state.notifications
            .map(
                (item) => `
                <article class="notification-row ${item.leida ? "" : "unread"}" data-notification-id="${item.id}">
                    <span class="row-mark">${notificationSymbol(item.tipo)}</span>
                    <div><h3>${C.escapeHTML(item.mensaje)}</h3><p>${C.escapeHTML(notificationCategory(item.tipo))}</p></div>
                    <time>${C.escapeHTML(C.relativeTime(item.created_at))}</time>
                </article>`
            )
            .join("");
    }

    async function applyToOpening(openingId, button) {
        C.setButtonLoading(button, true, "Postulando…");
        try {
            await C.api(`/postulaciones/convocatorias/${openingId}`, { method: "POST" });
            C.toast("Postulación registrada correctamente.");
            await loadApplications();
            renderOpportunities();
            renderMatches();
            renderDashboard();
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function cancelApplication(applicationId, button) {
        const confirmed = await confirmAction(
            "Retirar postulación",
            "La empresa dejará de considerarte en este proceso. Podrás volver a postular mientras la convocatoria siga publicada.",
            "Retirar postulación",
            true
        );
        if (!confirmed) return;
        C.setButtonLoading(button, true, "Retirando…");
        try {
            await C.api(`/postulaciones/${applicationId}/cancelar`, { method: "POST" });
            await loadApplications();
            renderOpportunities();
            renderMatches();
            renderDashboard();
            C.toast("Postulación retirada.");
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    function showOpeningDialog(opening = null) {
        if (!state.profile) {
            navigate("perfil");
            C.toast(
                "Primero guarda la razón social y un RUC válido de tu empresa.",
                "error"
            );
            return;
        }
        const form = $("#opening-form");
        form.reset();
        form.elements.id.value = opening?.id || "";
        form.elements.titulo.value = opening?.titulo || "";
        form.elements.descripcion.value = opening?.descripcion || "";
        form.elements.habilidades_requeridas.value = (
            opening?.habilidades_requeridas || []
        ).join(", ");
        form.elements.beneficios.value = (opening?.beneficios || []).join(", ");
        $("#opening-dialog-title").textContent = opening
            ? "Editar convocatoria"
            : "Nueva convocatoria";
        $("#opening-dialog").showModal();
    }

    async function changeOpeningState(id, action, button) {
        C.setButtonLoading(button, true);
        try {
            await C.api(`/convocatorias/${id}/${action}`, { method: "POST" });
            const messages = {
                publicar: "Convocatoria publicada.",
                cerrar: "Convocatoria cerrada.",
                reabrir: "Convocatoria reabierta.",
                duplicar: "Se creó una copia en borrador.",
            };
            C.toast(messages[action] || "Convocatoria actualizada.");
            await loadOpenings();
            renderDashboard();
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function deleteOpening(id, button) {
        const opening = state.openings.find((item) => item.id === Number(id));
        const confirmed = await confirmAction(
            "Eliminar borrador",
            `Se eliminará definitivamente “${opening?.titulo || "esta convocatoria"}”. Esta acción no se puede deshacer.`,
            "Eliminar borrador",
            true
        );
        if (!confirmed) return;
        C.setButtonLoading(button, true, "Eliminando…");
        try {
            await C.api(`/convocatorias/${id}`, { method: "DELETE" });
            await loadOpenings();
            renderDashboard();
            C.toast("Borrador eliminado.");
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function showCandidates(openingId) {
        const opening = state.openings.find((item) => item.id === Number(openingId));
        $("#candidates-title").textContent = opening?.titulo || "Postulaciones";
        $("#candidate-list").innerHTML = loadingMarkup();
        $("#candidates-dialog").dataset.openingId = openingId;
        if (!$("#candidates-dialog").open) $("#candidates-dialog").showModal();
        try {
            const candidates = await C.api(`/postulaciones/convocatorias/${openingId}`);
            renderCandidates(candidates);
        } catch (error) {
            $("#candidate-list").innerHTML = C.emptyState(
                "No se pudieron cargar",
                error.message,
                "alert"
            );
        }
    }

    function renderCandidates(candidates) {
        const list = $("#candidate-list");
        if (!candidates.length) {
            list.innerHTML = C.emptyState(
                "Aún no hay candidatos",
                "Las postulaciones aparecerán mientras la convocatoria esté publicada.",
                "users"
            );
            return;
        }
        list.innerHTML = candidates
            .map((item) => {
                const candidate = item.practicante || {};
                return `
                    <article class="candidate-row">
                        <span class="avatar">${C.escapeHTML(C.initials(candidate.nombres, candidate.apellidos))}</span>
                        <div>
                            <h3>${C.escapeHTML([candidate.nombres, candidate.apellidos].filter(Boolean).join(" ") || `Practicante #${item.practicante_id}`)}</h3>
                            <p>Reputación ${Math.round(candidate.score_reputacion || 0)}% · ${candidate.identidad_verificada ? "Identidad verificada" : "Identidad pendiente"}</p>
                            <div class="mini-tags">${(candidate.habilidades || [])
                                .slice(0, 5)
                                .map((skill) => `<span>${C.escapeHTML(skill)}</span>`)
                                .join("")}</div>
                        </div>
                        <div class="candidate-actions">
                            ${
                                item.estado === "pendiente"
                                    ? `<button class="button button-secondary button-small" data-reject-candidate="${item.id}">${C.icon("x")} Rechazar</button><button class="button button-primary button-small" data-select-candidate="${item.id}">${C.icon("check")} Seleccionar</button>`
                                    : item.estado === "seleccionada"
                                      ? item.practica_iniciada
                                          ? C.statusBadge(item.estado)
                                          : `<button class="button button-secondary button-small" data-reconsider-candidate="${item.id}">${C.icon("undo")} Reconsiderar</button><button class="button button-primary button-small" data-start-practice="${item.id}">${C.icon("clipboard")} Iniciar práctica</button>`
                                      : item.estado === "rechazada"
                                        ? `<button class="button button-secondary button-small" data-reconsider-candidate="${item.id}">${C.icon("undo")} Reconsiderar</button>`
                                        : C.statusBadge(item.estado)
                            }
                        </div>
                    </article>`;
            })
            .join("");
    }

    async function candidateAction(applicationId, action, button) {
        C.setButtonLoading(button, true);
        try {
            await C.api(`/postulaciones/${applicationId}/${action}`, { method: "POST" });
            const messages = {
                seleccionar: "Candidato seleccionado.",
                rechazar: "Postulación rechazada.",
                reconsiderar: "La postulación volvió a estado pendiente.",
            };
            C.toast(messages[action] || "Postulación actualizada.");
            await showCandidates($("#candidates-dialog").dataset.openingId);
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function startPractice(applicationId, button) {
        C.setButtonLoading(button, true, "Iniciando…");
        try {
            await C.api("/practicas", {
                method: "POST",
                body: { postulacion_id: Number(applicationId) },
            });
            C.toast("Práctica iniciada correctamente.");
            $("#candidates-dialog").close();
            await loadPractices();
            renderDashboard();
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function openPracticeDetail(practiceId) {
        const practice = state.practices.find((item) => item.id === Number(practiceId));
        if (!practice) return;
        state.currentPracticeId = practice.id;
        $("#practice-dialog-title").textContent = practiceTitle(practice);
        $("#practice-detail").innerHTML = loadingMarkup();
        if (!$("#practice-dialog").open) $("#practice-dialog").showModal();
        try {
            const [deliverables, evaluations, certificate] = await Promise.all([
                C.api(`/practicas/${practice.id}/entregables`),
                C.api(`/practicas/${practice.id}/evaluaciones`),
                safeApi(`/certificados/practica/${practice.id}`, null),
            ]);
            renderPracticeDetail(practice, deliverables, evaluations, certificate);
        } catch (error) {
            $("#practice-detail").innerHTML = C.emptyState(
                "No se pudo cargar el seguimiento",
                error.message,
                "alert"
            );
        }
    }

    function renderPracticeDetail(practice, deliverables, evaluations, certificate) {
        const isCompany = role() === "empresa";
        const canModify = practice.estado === "EN_CURSO";
        $("#practice-detail").innerHTML = `
            <section class="practice-detail-section">
                <div class="section-heading">
                    <div><h3>Estado general</h3><p>Práctica #${practice.id} · Postulación #${practice.postulacion_id}</p></div>
                    ${C.statusBadge(practice.estado)}
                </div>
            </section>
            <section class="practice-detail-section">
                <h3>Entregables</h3>
                ${
                    deliverables.length
                        ? deliverables
                              .map(
                                  (item) => `<div class="timeline-row">
                                      <span><strong>${C.escapeHTML(displayFileName(item.archivo))}</strong><small>${C.formatDate(item.fecha_subida, true)}</small></span>
                                      <div class="table-actions">
                                          <a class="text-link" href="${C.escapeHTML(item.archivo_url)}" target="_blank" rel="noopener">${C.icon("download")} Descargar</a>
                                          ${!isCompany && canModify ? `<button class="table-action danger" data-delete-deliverable="${item.id}">${C.icon("trash")} Eliminar</button>` : ""}
                                      </div>
                                  </div>`
                              )
                              .join("")
                        : `<p class="muted">Aún no se registraron entregables.</p>`
                }
                ${
                    !isCompany && canModify
                        ? `<form class="inline-form" id="deliverable-form">
                            <label class="field"><span>Subir archivo</span><input type="file" name="archivo" accept=".pdf,.doc,.docx,.zip" required></label>
                            <button class="button button-primary" type="submit">${C.icon("upload")} Subir entregable</button>
                           </form>`
                        : ""
                }
            </section>
            <section class="practice-detail-section">
                <h3>Evaluaciones</h3>
                ${
                    evaluations.length
                        ? evaluations
                              .map(
                                  (item) => `<div class="timeline-row">
                                      <span><strong>${item.puntaje} / 100</strong><small>${C.formatDate(item.fecha_evaluacion, true)}</small></span>
                                      <div class="table-actions">
                                          ${C.statusBadge(item.aprobada ? "verificada" : "rechazada")}
                                          ${isCompany && canModify ? `<button class="table-action danger" data-delete-evaluation="${item.id}">${C.icon("trash")} Eliminar</button>` : ""}
                                      </div>
                                  </div>`
                              )
                              .join("")
                        : `<p class="muted">Aún no se registraron evaluaciones.</p>`
                }
                ${
                    isCompany && canModify
                        ? `<form class="inline-form" id="evaluation-form">
                            <label class="field"><span>Puntaje</span><input type="number" name="puntaje" min="0" max="100" required></label>
                            <button class="button button-primary" type="submit">${C.icon("check")} Registrar evaluación</button>
                           </form>`
                        : ""
                }
            </section>
            <section class="practice-detail-section">
                <div class="section-heading">
                    <div><h3>Certificación</h3><p>${certificate ? "El documento digital ya está disponible." : "Se habilita después de finalizar una práctica aprobada."}</p></div>
                </div>
                ${
                    certificate
                        ? `<div class="table-actions" style="justify-content:flex-start">
                            <a class="button button-secondary button-small" href="${C.escapeHTML(certificate.documento?.url)}" target="_blank" rel="noopener">${C.icon("download")} Descargar PDF</a>
                            <a class="button button-secondary button-small" href="${C.escapeHTML(certificate.codigo_qr?.imagen_url)}" target="_blank" rel="noopener">${C.icon("eye")} Ver QR</a>
                           </div>`
                        : isCompany && practice.estado === "FINALIZADA"
                          ? `<button class="button button-primary" data-issue-certificate="${practice.id}">${C.icon("certificate")} Emitir certificado</button>`
                          : ""
                }
                ${
                    isCompany && canModify
                        ? `<div style="margin-top:18px"><button class="button button-secondary" data-finish-practice="${practice.id}">${C.icon("check")} Finalizar práctica</button></div>`
                        : ""
                }
            </section>`;

        $("#deliverable-form")?.addEventListener("submit", submitDeliverable);
        $("#evaluation-form")?.addEventListener("submit", submitEvaluation);
    }

    async function submitDeliverable(event) {
        event.preventDefault();
        const button = event.currentTarget.querySelector("button");
        C.setButtonLoading(button, true, "Subiendo…");
        try {
            await C.api(`/practicas/${state.currentPracticeId}/entregables`, {
                method: "POST",
                body: new FormData(event.currentTarget),
            });
            C.toast("Entregable registrado.");
            await openPracticeDetail(state.currentPracticeId);
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function submitEvaluation(event) {
        event.preventDefault();
        const button = event.currentTarget.querySelector("button");
        C.setButtonLoading(button, true);
        try {
            await C.api(`/practicas/${state.currentPracticeId}/evaluar`, {
                method: "POST",
                body: { puntaje: event.currentTarget.elements.puntaje.value },
            });
            C.toast("Evaluación registrada.");
            await openPracticeDetail(state.currentPracticeId);
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function deleteDeliverable(id, button) {
        const confirmed = await confirmAction(
            "Eliminar entregable",
            "El archivo y su registro se eliminarán de esta práctica.",
            "Eliminar entregable",
            true
        );
        if (!confirmed) return;
        C.setButtonLoading(button, true, "Eliminando…");
        try {
            await C.api(
                `/practicas/${state.currentPracticeId}/entregables/${id}`,
                { method: "DELETE" }
            );
            C.toast("Entregable eliminado.");
            await openPracticeDetail(state.currentPracticeId);
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function deleteEvaluation(id, button) {
        const confirmed = await confirmAction(
            "Eliminar evaluación",
            "El puntaje se eliminará del historial de esta práctica.",
            "Eliminar evaluación",
            true
        );
        if (!confirmed) return;
        C.setButtonLoading(button, true, "Eliminando…");
        try {
            await C.api(
                `/practicas/${state.currentPracticeId}/evaluaciones/${id}`,
                { method: "DELETE" }
            );
            C.toast("Evaluación eliminada.");
            await openPracticeDetail(state.currentPracticeId);
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function finishPractice(id, button) {
        C.setButtonLoading(button, true);
        try {
            await C.api(`/practicas/${id}/finalizar`, { method: "POST" });
            C.toast("Práctica finalizada.");
            await loadPractices();
            await openPracticeDetail(id);
            renderDashboard();
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function issueCertificate(id, button) {
        C.setButtonLoading(button, true, "Emitiendo…");
        try {
            await C.api(`/certificados/${id}/emitir`, { method: "POST" });
            C.toast("Certificado emitido.");
            await openPracticeDetail(id);
        } catch (error) {
            C.toast(error.message, "error");
        } finally {
            C.setButtonLoading(button, false);
        }
    }

    async function markNotification(id) {
        const item = state.notifications.find((notification) => notification.id === Number(id));
        if (!item || item.leida) return;
        try {
            await C.api(`/notificaciones/${id}/leer`, { method: "PUT" });
            item.leida = true;
            updateUnread();
            renderNotifications();
        } catch (error) {
            C.toast(error.message, "error");
        }
    }

    function bindNavigation() {
        $$(".nav-item").forEach((button) =>
            button.addEventListener("click", () => navigate(button.dataset.view))
        );
        document.addEventListener("click", (event) => {
            const goView = event.target.closest("[data-go-view]");
            if (goView) navigate(goView.dataset.goView);

            const targetView = event.target.closest("[data-target-view]");
            if (targetView) navigate(targetView.dataset.targetView);
        });
        $("#menu-button").addEventListener("click", openSidebar);
        $("#sidebar-close").addEventListener("click", closeSidebar);
        $("#sidebar-overlay").addEventListener("click", closeSidebar);
    }

    function bindProfile() {
        $("#add-skill").addEventListener("click", () => {
            const input = $("#skill-input");
            const value = input.value.trim();
            if (value && !state.studentSkills.includes(value)) state.studentSkills.push(value);
            input.value = "";
            renderTags();
        });
        $("#add-education").addEventListener("click", () => {
            const input = $("#education-input");
            const value = input.value.trim();
            if (value && !state.studentEducation.includes(value)) state.studentEducation.push(value);
            input.value = "";
            renderTags();
        });
        $("#skills-list").addEventListener("click", (event) => {
            const button = event.target.closest("[data-remove-skill]");
            if (!button) return;
            state.studentSkills.splice(Number(button.dataset.removeSkill), 1);
            renderTags();
        });
        $("#education-list").addEventListener("click", (event) => {
            const button = event.target.closest("[data-remove-education]");
            if (!button) return;
            state.studentEducation.splice(Number(button.dataset.removeEducation), 1);
            renderTags();
        });

        $("#student-profile-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const button = form.querySelector('[type="submit"]');
            C.setButtonLoading(button, true);
            const body = {
                nombres: form.elements.nombres.value.trim(),
                apellidos: form.elements.apellidos.value.trim(),
                dni: form.elements.dni.value.trim() || null,
                carnet_universitario:
                    form.elements.carnet_universitario.value.trim() || null,
                habilidades: state.studentSkills,
                formacion_educativa: state.studentEducation,
            };
            try {
                const wasMissing = !state.profile;
                await C.api("/perfil/me", { method: "PUT", body });
                if ((body.dni || body.carnet_universitario) && !state.profile?.identidad_verificada) {
                    await C.api("/perfil/me/identidad", {
                        method: "POST",
                        body: {
                            dni: body.dni,
                            carnet_universitario: body.carnet_universitario,
                        },
                    });
                }
                await loadProfile();
                if (wasMissing) {
                    await Promise.all([
                        loadPractices(),
                        loadApplications(),
                        loadMatches(),
                    ]);
                }
                C.toast("Perfil actualizado.");
                renderDashboard();
            } catch (error) {
                C.toast(error.message, "error");
            } finally {
                C.setButtonLoading(button, false);
            }
        });

        $("#company-profile-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const button = form.querySelector('[type="submit"]');
            C.setButtonLoading(button, true);
            try {
                const wasMissing = !state.profile;
                await C.api("/perfil/me/empresa", {
                    method: "PUT",
                    body: {
                        razon_social: form.elements.razon_social.value.trim(),
                        ruc: form.elements.ruc.value.trim(),
                    },
                });
                await loadProfile();
                if (wasMissing) {
                    await Promise.all([loadOpenings(), loadPractices()]);
                }
                C.toast(
                    wasMissing
                        ? "Empresa registrada. Ya puedes crear convocatorias."
                        : "Datos de la empresa actualizados."
                );
                renderDashboard();
                if (wasMissing) navigate("convocatorias");
            } catch (error) {
                C.toast(error.message, "error");
            } finally {
                C.setButtonLoading(button, false);
            }
        });
    }

    function bindOpportunities() {
        let searchTimer;
        $("#opportunity-search").addEventListener("input", (event) => {
            window.clearTimeout(searchTimer);
            searchTimer = window.setTimeout(async () => {
                $("#opportunity-list").innerHTML = loadingMarkup();
                try {
                    await loadOpportunities(event.target.value.trim());
                } catch (error) {
                    C.toast(error.message, "error");
                }
            }, 320);
        });
        $("#opportunity-list").addEventListener("click", (event) => {
            const item = event.target.closest("[data-select-opening]");
            if (!item) return;
            state.selectedOpeningId = Number(item.dataset.selectOpening);
            renderOpportunities();
        });
        document.addEventListener("click", (event) => {
            const apply = event.target.closest("[data-apply-opening]");
            if (apply) applyToOpening(Number(apply.dataset.applyOpening), apply);
        });
        $("#applications-table").addEventListener("click", (event) => {
            const cancel = event.target.closest("[data-cancel-application]");
            if (cancel) cancelApplication(cancel.dataset.cancelApplication, cancel);
            const reapply = event.target.closest("[data-reapply-opening]");
            if (reapply) applyToOpening(Number(reapply.dataset.reapplyOpening), reapply);
        });
        $("#recalculate-matches").addEventListener("click", async (event) => {
            C.setButtonLoading(event.currentTarget, true, "Actualizando…");
            try {
                state.matches = await C.api("/matching/calcular", { method: "POST" });
                renderMatches();
                await loadNotifications();
                C.toast("Recomendaciones actualizadas.");
            } catch (error) {
                C.toast(error.message, "error");
            } finally {
                C.setButtonLoading(event.currentTarget, false);
            }
        });
    }

    function bindFilters() {
        $("#application-filters").addEventListener("click", (event) => {
            const button = event.target.closest("[data-filter]");
            if (!button) return;
            $$("#application-filters button").forEach((item) =>
                item.classList.toggle("active", item === button)
            );
            state.applicationFilter = button.dataset.filter;
            renderApplications();
        });
        $("#opening-filters").addEventListener("click", (event) => {
            const button = event.target.closest("[data-filter]");
            if (!button) return;
            $$("#opening-filters button").forEach((item) =>
                item.classList.toggle("active", item === button)
            );
            state.openingFilter = button.dataset.filter;
            renderOpenings();
        });
    }

    function bindOpenings() {
        $("#new-opening-button").addEventListener("click", () => showOpeningDialog());
        $("#primary-action").addEventListener("click", (event) => {
            if (event.currentTarget.dataset.action === "new-opening") showOpeningDialog();
            else if (event.currentTarget.dataset.targetView) {
                navigate(event.currentTarget.dataset.targetView);
            }
        });
        $("#dashboard-list-action").addEventListener("click", (event) =>
            navigate(event.currentTarget.dataset.targetView)
        );
        $("#opening-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            const form = event.currentTarget;
            const id = form.elements.id.value;
            const button = form.querySelector('[type="submit"]');
            C.setButtonLoading(button, true);
            try {
                const body = {
                    titulo: form.elements.titulo.value.trim(),
                    descripcion: form.elements.descripcion.value.trim(),
                    habilidades_requeridas: C.splitComma(
                        form.elements.habilidades_requeridas.value
                    ),
                    beneficios: C.splitComma(form.elements.beneficios.value),
                };
                await C.api(id ? `/convocatorias/${id}` : "/convocatorias", {
                    method: id ? "PUT" : "POST",
                    body,
                });
                $("#opening-dialog").close();
                C.toast(id ? "Convocatoria actualizada." : "Borrador creado.");
                await loadOpenings();
                renderDashboard();
            } catch (error) {
                C.toast(error.message, "error");
            } finally {
                C.setButtonLoading(button, false);
            }
        });
        $("#openings-table").addEventListener("click", (event) => {
            const edit = event.target.closest("[data-edit-opening]");
            if (edit) {
                showOpeningDialog(
                    state.openings.find((item) => item.id === Number(edit.dataset.editOpening))
                );
            }
            const publish = event.target.closest("[data-publish-opening]");
            if (publish) changeOpeningState(publish.dataset.publishOpening, "publicar", publish);
            const close = event.target.closest("[data-close-opening]");
            if (close) changeOpeningState(close.dataset.closeOpening, "cerrar", close);
            const reopen = event.target.closest("[data-reopen-opening]");
            if (reopen) changeOpeningState(reopen.dataset.reopenOpening, "reabrir", reopen);
            const duplicate = event.target.closest("[data-duplicate-opening]");
            if (duplicate) {
                changeOpeningState(
                    duplicate.dataset.duplicateOpening,
                    "duplicar",
                    duplicate
                );
            }
            const remove = event.target.closest("[data-delete-opening]");
            if (remove) deleteOpening(remove.dataset.deleteOpening, remove);
            const candidates = event.target.closest("[data-candidates-opening]");
            if (candidates) showCandidates(candidates.dataset.candidatesOpening);
        });
        $("#candidate-list").addEventListener("click", (event) => {
            const select = event.target.closest("[data-select-candidate]");
            if (select) candidateAction(select.dataset.selectCandidate, "seleccionar", select);
            const reject = event.target.closest("[data-reject-candidate]");
            if (reject) candidateAction(reject.dataset.rejectCandidate, "rechazar", reject);
            const reconsider = event.target.closest("[data-reconsider-candidate]");
            if (reconsider) {
                candidateAction(
                    reconsider.dataset.reconsiderCandidate,
                    "reconsiderar",
                    reconsider
                );
            }
            const start = event.target.closest("[data-start-practice]");
            if (start) startPractice(start.dataset.startPractice, start);
        });
    }

    function bindPractices() {
        $("#practice-list").addEventListener("click", (event) => {
            const button = event.target.closest("[data-view-practice]");
            if (button) openPracticeDetail(button.dataset.viewPractice);
        });
        $("#practice-detail").addEventListener("click", (event) => {
            const finish = event.target.closest("[data-finish-practice]");
            if (finish) finishPractice(finish.dataset.finishPractice, finish);
            const issue = event.target.closest("[data-issue-certificate]");
            if (issue) issueCertificate(issue.dataset.issueCertificate, issue);
            const deliverable = event.target.closest("[data-delete-deliverable]");
            if (deliverable) {
                deleteDeliverable(deliverable.dataset.deleteDeliverable, deliverable);
            }
            const evaluation = event.target.closest("[data-delete-evaluation]");
            if (evaluation) {
                deleteEvaluation(evaluation.dataset.deleteEvaluation, evaluation);
            }
        });
    }

    function bindNotifications() {
        $("#notification-list").addEventListener("click", (event) => {
            const row = event.target.closest("[data-notification-id]");
            if (row) markNotification(row.dataset.notificationId);
        });
        $("#mark-all-read").addEventListener("click", async (event) => {
            C.setButtonLoading(event.currentTarget, true);
            try {
                await C.api("/notificaciones/leer-todas", { method: "PUT" });
                state.notifications.forEach((item) => {
                    item.leida = true;
                });
                updateUnread();
                renderNotifications();
                C.toast("Notificaciones actualizadas.");
            } catch (error) {
                C.toast(error.message, "error");
            } finally {
                C.setButtonLoading(event.currentTarget, false);
            }
        });
    }

    function bindDialogs() {
        $$("[data-close-dialog]").forEach((button) => {
            button.addEventListener("click", () => {
                document.getElementById(button.dataset.closeDialog).close();
            });
        });
        $$(".app-dialog").forEach((dialog) => {
            dialog.addEventListener("click", (event) => {
                if (event.target === dialog) dialog.close();
            });
        });
    }

    function bindSession() {
        $("#logout-button").addEventListener("click", async () => {
            try {
                await C.api("/auth/logout", { method: "POST" });
            } finally {
                window.location.assign("/ingresar");
            }
        });
    }

    function bindEvents() {
        bindNavigation();
        bindProfile();
        bindOpportunities();
        bindFilters();
        bindOpenings();
        bindPractices();
        bindNotifications();
        bindDialogs();
        bindSession();
    }

    async function initialize() {
        try {
            state.user = await C.api("/auth/me");
        } catch (error) {
            window.location.assign("/ingresar");
            return;
        }

        configureRole();
        bindEvents();
        await loadProfile();

        const shared = [loadNotifications()];
        if (state.profile) {
            shared.push(loadPractices());
            if (role() === "empresa") {
                shared.push(loadOpenings());
            } else {
                shared.push(loadOpportunities(), loadApplications(), loadMatches());
            }
        } else if (role() === "practicante") {
            shared.push(loadOpportunities());
        }
        try {
            await Promise.all(shared);
            if (role() === "practicante") await loadCertificates();
        } catch (error) {
            C.toast(error.message, "error", 6500);
        }

        renderDashboard();
        $("#app-loading").hidden = true;
        $("#app-shell").hidden = false;
        const initialView = state.profile
            ? window.location.hash.slice(1) || "resumen"
            : "perfil";
        navigate(initialView, false);
        if (!state.profile) {
            C.toast(
                role() === "empresa"
                    ? "Completa la razón social y el RUC para habilitar las convocatorias."
                    : "Completa tus datos para habilitar todas las funciones."
            );
        }
    }

    initialize();
})();
