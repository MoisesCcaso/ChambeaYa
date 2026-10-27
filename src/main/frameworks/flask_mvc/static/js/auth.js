(function () {
    "use strict";

    const box = document.querySelector("[data-auth-mode]");
    const form = document.getElementById("auth-form");
    if (!box || !form) return;

    const mode = box.dataset.authMode;
    const feedback = document.getElementById("form-feedback");
    const query = new URLSearchParams(window.location.search);
    const activationToken = query.get("token");

    document.querySelectorAll("[data-toggle-password]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = button.parentElement.querySelector("input");
            input.type = input.type === "password" ? "text" : "password";
            const label = input.type === "password" ? "Mostrar contraseña" : "Ocultar contraseña";
            button.setAttribute("aria-label", label);
            button.querySelector(".sr-only").textContent = label;
        });
    });

    if (form.elements.token && activationToken) {
        form.elements.token.value = activationToken;
    }
    if (mode === "register" && query.get("tipo")) {
        const role = form.querySelector(`[name="tipo"][value="${query.get("tipo")}"]`);
        if (role) role.checked = true;
    }
    if (mode === "activate") {
        const emailField = document.getElementById("activation-email-field");
        const email = query.get("email");
        if (email && form.elements.email) form.elements.email.value = email;
        if (activationToken) {
            emailField.hidden = true;
            form.elements.email.required = false;
            document.getElementById("auth-title").textContent = "Confirma tu cuenta";
            document.getElementById("auth-description").textContent =
                "Completa la activación para comenzar a utilizar ChambeaYa.";
            document.getElementById("activation-notice-text").textContent =
                "El enlace es personal y tiene una vigencia de 48 horas.";
            document.getElementById("activation-submit").innerHTML =
                `${Chambea.icon("check")} Activar mi cuenta`;
        } else {
            form.elements.email.required = true;
        }
    }

    const passwordInput = form.querySelector("[data-password-source]");
    const passwordRules = {
        length: (value) => value.length >= 8,
        lowercase: (value) => /[a-z]/.test(value),
        uppercase: (value) => /[A-Z]/.test(value),
        number: (value) => /\d/.test(value),
    };

    function updatePasswordRequirements() {
        if (!passwordInput) return true;
        const value = passwordInput.value;
        let valid = true;
        Object.entries(passwordRules).forEach(([rule, validator]) => {
            const fulfilled = validator(value);
            valid = valid && fulfilled;
            document
                .querySelector(`[data-password-rule="${rule}"]`)
                ?.classList.toggle("valid", fulfilled);
        });
        return valid;
    }

    passwordInput?.addEventListener("input", updatePasswordRequirements);

    document.querySelectorAll("[data-demo-login]").forEach((button) => {
        button.addEventListener("click", () => {
            form.elements.email.value = button.dataset.demoLogin;
            form.elements.password.value = "Demo1234";
            form.elements.email.focus();
        });
    });

    function showFeedback(message, type) {
        feedback.hidden = false;
        feedback.className = `form-feedback ${type}`;
        feedback.textContent = message;
    }

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        feedback.hidden = true;
        const button = form.querySelector('[type="submit"]');
        Chambea.setButtonLoading(button, true);
        const values = Object.fromEntries(new FormData(form).entries());

        try {
            if (mode === "login") {
                await Chambea.api("/auth/login", { method: "POST", body: values });
                window.location.assign("/app");
                return;
            }

            if (mode === "register") {
                if (!updatePasswordRequirements()) {
                    showFeedback(
                        "La contraseña todavía no cumple todos los requisitos.",
                        "error"
                    );
                    return;
                }
                if (values.password !== values.password_confirmation) {
                    showFeedback("Las contraseñas no coinciden.", "error");
                    return;
                }
                const data = await Chambea.api("/auth/register", { method: "POST", body: values });
                if (data.activation_token) {
                    showFeedback("Cuenta creada. Te llevaremos a la activación.", "success");
                    window.setTimeout(() => {
                        window.location.assign(`/activar?token=${encodeURIComponent(data.activation_token)}`);
                    }, 900);
                } else {
                    showFeedback(
                        "Cuenta creada. Revisa tu correo para activarla.",
                        "success"
                    );
                    window.setTimeout(() => {
                        window.location.assign(
                            `/activar?email=${encodeURIComponent(values.email)}`
                        );
                    }, 900);
                }
                return;
            }

            if (mode === "activate") {
                if (activationToken) {
                    await Chambea.api("/auth/activate", {
                        method: "POST",
                        body: { token: values.token },
                    });
                    showFeedback("Tu cuenta está activa. Ya puedes ingresar.", "success");
                    window.setTimeout(() => window.location.assign("/ingresar"), 1000);
                } else {
                    const data = await Chambea.api("/auth/resend-activation", {
                        method: "POST",
                        body: { email: values.email },
                    });
                    if (data.activation_token) {
                        window.location.assign(
                            `/activar?token=${encodeURIComponent(data.activation_token)}`
                        );
                    } else {
                        showFeedback(
                            "Si la cuenta está pendiente, recibirás un nuevo enlace.",
                            "success"
                        );
                    }
                }
                return;
            }

            if (mode === "recover") {
                const data = await Chambea.api("/auth/recover-password", {
                    method: "POST",
                    body: values,
                });
                if (data.password_reset_token) {
                    showFeedback("Solicitud procesada. Te llevaremos al cambio de contraseña.", "success");
                    window.setTimeout(() => {
                        window.location.assign(
                            `/restablecer?token=${encodeURIComponent(data.password_reset_token)}`
                        );
                    }, 900);
                } else {
                    showFeedback("Si la cuenta existe, recibirás las instrucciones de recuperación.", "success");
                }
                return;
            }

            if (mode === "reset") {
                await Chambea.api("/auth/reset-password", { method: "POST", body: values });
                showFeedback("Contraseña actualizada. Ya puedes ingresar.", "success");
                window.setTimeout(() => window.location.assign("/ingresar"), 1000);
            }
        } catch (error) {
            showFeedback(error.message, "error");
        } finally {
            Chambea.setButtonLoading(button, false);
        }
    });
})();
