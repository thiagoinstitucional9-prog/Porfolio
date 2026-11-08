from django.core.management.base import BaseCommand

from core.services import DIAS_DE_SALIDAS, asegurar_viajes


class Command(BaseCommand):
    help = "Genera en MySQL las salidas de los próximos días."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dias", type=int, default=DIAS_DE_SALIDAS,
            help=f"Cantidad de días a generar (por defecto {DIAS_DE_SALIDAS}).",
        )

    def handle(self, *args, **options):
        creados = asegurar_viajes(dias=options["dias"])
        self.stdout.write(self.style.SUCCESS(
            f"Viajes generados: {creados}"
        ))
