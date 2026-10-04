# Aetherion: cliente alineado con la web

Referencia: `index.html`, `monochrome.css` y `brand-symbol.svg` del 4 de octubre de 2026.

- Superficies #080C12 / #101823, texto #EDF2F7 y acento #8EAFFF; botones principales claros.
- Inicio editorial con tres líneas, acceso directo al benchmark e ilustración vectorial del hardware.
- Símbolo orbital nativo, sin descargas de recursos ni animaciones continuas.
- Formularios, descarga GGUF, mensajes y tablas usan tokens del tema.
- Se mantienen cuentas, almacenamiento, motor y navegación existentes.

La búsqueda de ui-ux-pro-max para «benchmark data dashboard» devolvió Data-Dense Dashboard, apropiado para las vistas de resultados. La búsqueda amplia de sistema visual devolvió Glassmorphism y una landing comercial: no se adoptaron; la web existente es la referencia visual solicitada. Tkinter no tiene una guía específica en los stacks de la skill.

Verificación: 39 pruebas aprobadas; las siete vistas se renderizaron a 1020×720, 1200×820 y 1600×1000 usando almacenamiento temporal. Captura del inicio en workspace.png, sin experimentos ficticios. No se probó autenticación online ni inferencia real como parte de este cambio visual.

Ejecutable: dist-web-aligned/Aetherion-Client.exe. Compilación local con PyInstaller; los ejecutables anteriores se conservan.
