from django.urls import path


def crash(request):
    raise RuntimeError("boom")


urlpatterns = [path("crash/", crash)]
