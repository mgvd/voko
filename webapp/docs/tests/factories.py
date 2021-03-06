from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = "docs.Document"

    name = FuzzyText()
    file = FuzzyText()
    slug = FuzzyText()


class LinkFactory(DjangoModelFactory):
    class Meta:
        model = "docs.Link"

    name = FuzzyText()
    url = FuzzyText()
