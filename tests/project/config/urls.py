from django.urls import include, path


urlpatterns = [
    path(
        "whatsapp/",
        include(
            "django_whatsapp.webhooks.urls"
        ),
    ),
]