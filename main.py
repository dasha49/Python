
from abc import ABC, abstractmethod


# Інтерфейс Document
class Document(ABC):

    @abstractmethod
    def render(self) -> str:
        pass


# Звичайний звіт
class Report(Document):

    def render(self) -> str:
        return "Rendering Report"


# Рахунок
class Invoice(Document):

    def render(self) -> str:
        return "Rendering Invoice"


# Контракт
class Contract(Document):

    def render(self) -> str:
        return "Rendering Contract"


# Фабрика документів
class DocumentFactory:

    @staticmethod
    def create(doc_type: str) -> Document:

        if doc_type == "report":
            return Report()

        if doc_type == "invoice":
            return Invoice()

        if doc_type == "contract":
            return Contract()

        raise ValueError("Unknown document type")


# Клієнтський код
doc_type = "report"

document = DocumentFactory.create(doc_type)

print(document.render())
