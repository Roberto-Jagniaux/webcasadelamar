import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Genera un respaldo local en backups/<fecha>/: un dump JSON de la base "
        "de datos y una copia zip de media/. No sube nada a ningún servicio "
        "externo, solo lo deja listo en disco para que se copie a donde "
        "corresponda (disco externo, nube, etc.)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--mantener",
            type=int,
            default=10,
            help="Cantidad de respaldos recientes a conservar (default: 10, 0 = no borrar ninguno).",
        )

    def handle(self, *args, **options):
        backups_dir = Path(settings.BASE_DIR) / "backups"
        destino = backups_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
        destino.mkdir(parents=True, exist_ok=True)

        dump_path = destino / "datos.json"
        with open(dump_path, "w", encoding="utf-8") as f:
            management.call_command(
                "dumpdata",
                exclude=[
                    "contenttypes",
                    "auth.permission",
                    "sessions.session",
                    "admin.logentry",
                ],
                indent=2,
                stdout=f,
            )
        self.stdout.write(self.style.SUCCESS(f"Dump de datos: {dump_path}"))

        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists() and any(media_root.iterdir()):
            media_zip = shutil.make_archive(str(destino / "media"), "zip", root_dir=media_root)
            self.stdout.write(self.style.SUCCESS(f"Copia de media/: {media_zip}"))
        else:
            self.stdout.write("No hay archivos en media/, se omite la copia.")

        self._limpiar_antiguos(backups_dir, options["mantener"], destino)
        self.stdout.write(self.style.SUCCESS(f"Respaldo completo en {destino}"))

    def _limpiar_antiguos(self, backups_dir, mantener, actual):
        if mantener <= 0:
            return
        carpetas = sorted(
            (p for p in backups_dir.iterdir() if p.is_dir() and p != actual),
            key=lambda p: p.name,
        )
        exceso = len(carpetas) + 1 - mantener
        for vieja in carpetas[:exceso]:
            shutil.rmtree(vieja)
            self.stdout.write(f"Respaldo antiguo eliminado: {vieja.name}")
