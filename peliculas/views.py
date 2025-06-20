from rest_framework import generics
from .models import Pelicula
from .serializers import PeliculaSerializer
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

#endpoint para filtros
class PeliculaListView(generics.ListAPIView):
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer
    filterset_fields = ['titulo', 'fecha', 'categoria']
    ordering_fields = ['calificacion']

#logica filtro 

class PeliculaPorCategoriaView(generics.ListAPIView):
    serializer_class = PeliculaSerializer

    def get_queryset(self):
        """
        Filtra las películas por categoría si se proporciona un parámetro 'categoria' en la URL.
        """
        categoria = self.request.query_params.get('categoria', None)
        if categoria:
            # Aquí: iexact en el CharField 'categoria'
            return Pelicula.objects.filter(categoria__iexact=categoria)
        return Pelicula.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"mensaje": "No se encontraron películas en esta categoría."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# endpoint para popularidad
class PeliculasPopularesView(APIView):
    def get(self, request):
        # Ordenar las películas por calificación en orden descendente
        peliculas_populares = Pelicula.objects.order_by('-calificacion')[:10]  # cauntas muestra
        serializer = PeliculaSerializer(peliculas_populares, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#Metodo CRUD para las peliculas

class PeliculaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer

class PeliculaCreateView(generics.CreateAPIView):
    queryset = Pelicula.objects.all()
    serializer_class = PeliculaSerializer

class PeliculasRecientesView(generics.ListAPIView):
    """
    Endpoint para obtener las películas más recientes, ordenadas por fecha descendente.
    """
    serializer_class = PeliculaSerializer

    def get_queryset(self):
        return Pelicula.objects.all().order_by('-fecha')[:10]  # Devuelve las 10 películas más recientes


