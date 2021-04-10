from django.conf.urls import url
from .views import DocumentOverview, DocumentDownload

app_name = 'docs'

urlpatterns = (
    url(r'^download/(?P<slug>[a-z0-9\-]+)/$',
        DocumentDownload.as_view(),
        name="docs.document_download"),
    url(r'^', DocumentOverview.as_view(),
        name="docs.document_overview"),
)
