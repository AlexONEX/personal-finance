"""Clase base abstracta para data sources."""

from abc import ABC, abstractmethod
from datetime import date


class DataSource(ABC):
    """Interfaz abstracta para fuentes de datos.

    Todas las fuentes de datos deben implementar el método fetch()
    que devuelve un diccionario de fecha -> valor.
    """

    @abstractmethod
    def fetch(self, since: date, until: date) -> dict[date, float]:
        """Obtiene datos históricos desde una fecha hasta otra.

        Args:
            since: Fecha de inicio (inclusive)
            until: Fecha de fin (inclusive)

        Returns:
            Diccionario de fecha -> valor (dict[date, float])
        """
        pass
