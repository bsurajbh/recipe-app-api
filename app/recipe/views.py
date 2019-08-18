from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe.serialisers import (
    TagSerializer, IngredientSerializer, RecipeSerializer,
    RecipeDetailSerializer, UploadImageSerializer)


class BaseRecipeViewSet(viewsets.GenericViewSet, mixins.ListModelMixin,
                        mixins.CreateModelMixin):
    """common base class for tags and recipe"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user
                               ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """create objects"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseRecipeViewSet):
    """manage ingredients"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """manage recipes"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _filter_extract_params(self, qs):
        """extract params in list"""
        return [int(id) for id in qs.split(',')]

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_id = self._filter_extract_params(tags)
            queryset = queryset.filter(tags__id__in=tag_id)
        if ingredients:
            ingredient_id = self._filter_extract_params(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_id)
        return queryset.filter(user=self.request.user)

    # to get details instead of id in retrieve
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return UploadImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """create objects"""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
