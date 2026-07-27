# Vistas web de ChambeaYa

La interfaz web está implementada directamente sobre Flask con plantillas
Jinja, CSS y JavaScript nativo. No requiere un proceso adicional de compilación.

## Acceso

Al ejecutar la aplicación, las vistas disponibles son:

| Ruta | Vista |
| --- | --- |
| `/` | Página de presentación |
| `/ingresar` | Inicio de sesión |
| `/registro` | Registro con confirmación y requisitos de contraseña |
| `/activar` | Activación mediante enlace enviado al correo y reenvío |
| `/recuperar` | Solicitud de recuperación de contraseña |
| `/restablecer` | Restablecimiento de contraseña |
| `/verificar-certificado` | Validación pública de certificados |
| `/app` | Aplicación autenticada según el rol |

La ruta `/app` detecta el rol de la sesión y presenta únicamente las funciones
correspondientes:

- Practicante: perfil, oportunidades, sugerencias, postulaciones, prácticas,
  entregables, evaluaciones, certificados y notificaciones.
- Empresa: perfil, convocatorias, candidatos, selección, prácticas,
  evaluaciones, emisión de certificados y notificaciones.

## Diseño

El sistema visual usa una paleta sobria de azul profundo, grises fríos y
`#0062fc` como color primario, tomado de la identidad gráfica de ChambeaYa. No
utiliza degradados. Las pantallas priorizan tablas, listas y secciones amplias
sobre grupos repetitivos de tarjetas, con navegación adaptable para escritorio,
tableta y móvil.

Los archivos principales son:

- `frameworks/flask_mvc/templates/`: estructura de las vistas.
- `frameworks/flask_mvc/static/css/app.css`: sistema visual y responsive.
- `frameworks/flask_mvc/static/icons.svg`: iconografía SVG reutilizable.
- `frameworks/flask_mvc/static/img/`: logos horizontal y cuadrado.
- `frameworks/flask_mvc/static/js/common.js`: utilidades y cliente HTTP.
- `frameworks/flask_mvc/static/js/app.js`: interacción de la aplicación.
- `frameworks/flask_mvc/static/js/auth.js`: flujos de autenticación.
- `frameworks/flask_mvc/static/js/verify.js`: validación de certificados.

## Ejecución

```bash
flask --app frameworks.flask_mvc.app:create_app run --debug
```

Luego se puede abrir `http://127.0.0.1:5000/`.

Las vistas consumen los endpoints existentes con la sesión de Flask. Los
errores de validación y de autorización se muestran en contexto, y las acciones
incluyen estados de carga, confirmaciones y estados vacíos.
