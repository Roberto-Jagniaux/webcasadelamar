// Configuración de Tailwind (Play CDN). Debe ejecutarse justo después de
// cargar el script de cdn.tailwindcss.com, antes de que Tailwind escanee el
// DOM por primera vez — por eso este archivo se carga sin "defer" e
// inmediatamente a continuación del script de Tailwind en base.html.
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#F9A392',
            },
            fontFamily: {
                // Antes llegaba heredado desde 1style.css (la hoja de
                // Bootstrap que el roadmap planea eliminar en la migración a
                // Tailwind) — declarado acá para que no dependa de un
                // archivo que va a desaparecer.
                sans: ['Poppins', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
                // Voz editorial: títulos, nombre de marca, headline del
                // carrusel. No se usa en formularios, fechas ni texto legal
                // — esos siguen en Poppins (font-sans, el default).
                serif: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
            },
        },
    },
};

// Componentes de Alpine.js. Este archivo se carga sin "defer" y ANTES del
// script de Alpine en base.html, así que el listener de "alpine:init" queda
// enganchado de inmediato — mucho antes de que el script de Alpine (que sí
// tiene "defer") llegue a ejecutarse y dispare ese evento.
document.addEventListener('alpine:init', () => {
    // Menú hamburguesa del header (mobile/tablet).
    Alpine.data('mobileMenu', () => ({
        mobileMenuOpen: false,
    }));

    // Carrusel del hero (home). Rota de slide cada 6 segundos.
    Alpine.data('heroCarousel', () => ({
        slide: 0,
        total: 3,
        init() {
            setInterval(() => {
                this.slide = (this.slide + 1) % this.total;
            }, 6000);
        },
    }));

    // Botón flotante "volver arriba". Se oculta cada vez que su posición
    // fija (esquina inferior derecha) coincide con un campo de formulario o
    // con el footer, sin depender de que haya foco activo (cubre el caso de
    // que ya tape algo apenas carga la página, antes de que el usuario
    // toque nada).
    Alpine.data('backToTop', () => ({
        oculto: false,
        actualizar() {
            const margen = 24;
            const tam = 48;
            const boton = {
                left: window.innerWidth - margen - tam,
                right: window.innerWidth - margen,
                top: window.innerHeight - margen - tam,
                bottom: window.innerHeight - margen,
            };
            this.oculto = Array.from(
                document.querySelectorAll('input, select, textarea, footer, .campo-seleccionable')
            ).some((el) => {
                const r = el.getBoundingClientRect();
                return !(boton.right < r.left || boton.left > r.right || boton.bottom < r.top || boton.top > r.bottom);
            });
        },
    }));

    // Formulario de reserva: aviso en vivo cuando la fecha elegida está
    // bloqueada. "bloqueadas" llega desde Django (fechas_bloqueadas_json) al
    // invocar el componente en el template: reservaForm({{ fechas_bloqueadas_json|safe }}).
    Alpine.data('reservaForm', (bloqueadas) => ({
        fecha: '',
        bloqueadas: bloqueadas || [],
    }));

    // Lightbox de la galería de autocuidado para equipos.
    Alpine.data('galeriaLightbox', () => ({
        imagenAbierta: null,
    }));
});
