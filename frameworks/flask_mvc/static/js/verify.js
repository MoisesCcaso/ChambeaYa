(function () {
    "use strict";

    const form = document.getElementById("verify-form");
    const result = document.getElementById("verification-result");
    if (!form || !result) return;

    const queryCode = new URLSearchParams(window.location.search).get("codigo");
    if (queryCode) {
        form.elements.codigo.value = queryCode;
        window.setTimeout(() => form.requestSubmit(), 0);
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const code = form.elements.codigo.value.trim();
        const button = form.querySelector("button");
        Chambea.setButtonLoading(button, true, "Verificando…");
        result.hidden = true;
        try {
            const data = await Chambea.api(`/certificados/verificar/${encodeURIComponent(code)}`);
            result.hidden = false;
            result.className = `verification-result ${data.valido ? "valid" : "invalid"}`;
            result.innerHTML = data.valido
                ? `<span class="result-mark">${Chambea.icon("check")}</span><h3>Certificado válido</h3><p>El código y el contenido registrado conservan su integridad.</p>`
                : `<span class="result-mark">${Chambea.icon("alert")}</span><h3>No se pudo validar</h3><p>El certificado no conserva su integridad o el código no coincide.</p>`;
        } catch (error) {
            result.hidden = false;
            result.className = "verification-result invalid";
            result.innerHTML = `<span class="result-mark">${Chambea.icon("alert")}</span><h3>Certificado no encontrado</h3><p>${Chambea.escapeHTML(error.message)}</p>`;
        } finally {
            Chambea.setButtonLoading(button, false);
        }
    });
})();
