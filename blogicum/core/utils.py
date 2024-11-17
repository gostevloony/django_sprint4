from django.shortcuts import get_object_or_404


def get_published_objects(model, slug=None):
    if slug:
        return get_object_or_404(model, is_published=True, slug=slug)
    return get_object_or_404(model, is_published=True)
