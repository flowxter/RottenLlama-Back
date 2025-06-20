# tests/test_peliculas_models.py
import pytest
from peliculas.models import Pelicula
from django.core.exceptions import ValidationError

@pytest.mark.django_db
class TestPeliculaModel:
    def test_creacion_pelicula_valida(self):
        pelicula = Pelicula.objects.create(
            titulo="The Dark Knight",
            fecha=2008,
            categoria="acción",
            calificacion=9.0,
            director="Christopher Nolan"
        )
        assert pelicula.id is not None
        assert str(pelicula) == "The Dark Knight"

    def test_calificacion_maxima(self):
        with pytest.raises(ValidationError):
            pelicula = Pelicula(
                titulo="Película inválida",
                fecha=2020,
                categoria="drama",
                calificacion=10.1,  # Más del máximo permitido (3 dígitos, 1 decimal)
                director="Director X"
            )
            pelicula.full_clean()  # Esto activa la validación

    def test_campos_obligatorios(self):
        with pytest.raises(ValidationError):
            pelicula = Pelicula()
            pelicula.full_clean()