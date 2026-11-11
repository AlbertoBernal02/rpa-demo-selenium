"""Jerarquía de excepciones tipadas con código `PREFIJO-DETALLE`.

El código viaja en el log, en el informe de resultado y en el nombre de la captura,
de modo que un fallo se puede clasificar sin abrir el navegador.
"""


class RPAError(Exception):
    """Error base de la automatización. Lleva un código estable y un mensaje legible."""

    prefijo = "RPA"

    def __init__(self, detalle: str, mensaje: str = ""):
        self.codigo = f"{self.prefijo}-{detalle}"
        self.mensaje = mensaje
        super().__init__(f"[{self.codigo}] {mensaje}" if mensaje else f"[{self.codigo}]")


class NavegacionError(RPAError):
    """No se pudo llegar a una página o un elemento no apareció a tiempo."""

    prefijo = "NAV"


class FormularioError(RPAError):
    """El sitio rechazó el formulario o su resultado no es el esperado."""

    prefijo = "FORM"


class DescargaError(RPAError):
    """El archivo descargado no llegó a la carpeta de destino."""

    prefijo = "DESC"
