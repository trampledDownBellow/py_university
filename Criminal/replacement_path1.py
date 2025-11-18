from abc import ABC, abstractmethod

class Document(ABC):
    @abstractmethod
    def render(self) -> str:
        pass

class Report(Document):
    def render(self) -> str:
        return "[CORP] Standard Corporate Report"

class Invoice(Document):
    def render(self) -> str:
        return "[CORP] Official Invoice"

class Contract(Document):
    def render(self) -> str:
        return "[CORP] Legal Corporate Contract"

class ShadowReport(Document):
    def render(self) -> str:
        return "[SHADOW] Report::SYS-META{tracking=hidden, lvl=2}"

class ShadowInvoice(Document):
    def render(self) -> str:
        return "[SHADOW] Invoice::SYS-META{ghost-field=checksum89}"

class ShadowContract(Document):
    def render(self) -> str:
        return "[SHADOW] Contract::SYS-META{flag=stealth-contract}"

class NullDocument(Document):
    def __init__(self, reason: str):
        self.reason = reason

    def render(self) -> str:
        return f"[ERROR] {self.reason}"

class CorporateDocumentFactory:
    registry = {
        "report": Report,
        "invoice": Invoice,
        "contract": Contract,
    }
    @staticmethod
    def create(doc_type: str) -> Document:
        cls = CorporateDocumentFactory.registry.get(doc_type)
        if cls is None:
            return NullDocument("Unknown document type (corp).")
        return cls()

class ShadowDocumentFactory:
    registry = {
        "report": ShadowReport,
        "invoice": ShadowInvoice,
        "contract": ShadowContract,
    }

    @staticmethod
    def create(doc_type: str) -> Document:
        cls = ShadowDocumentFactory.registry.get(doc_type)
        if cls is None:
            return NullDocument("Unknown document type (shadow).")
        return cls()


CONFIG = {
    "mode": "corp"
}
ALLOWED_TYPES = {"report", "invoice", "contract"}

def get_factory():
    if CONFIG["mode"] == "corp":
        return CorporateDocumentFactory
    elif CONFIG["mode"] == "shadow":
        return ShadowDocumentFactory
    else:
        raise ValueError("Invalid mode in config.")

def client_code(doc_type: str):
    if doc_type not in ALLOWED_TYPES:
        return print(NullDocument("Document type is not allowed.").render())

    factory = get_factory()
    doc = factory.create(doc_type)
    print(doc.render())

if __name__ == "__main__":
    print("\n===CORP MODE===")
    CONFIG["mode"] = "corp"
    client_code("report")
    client_code("invoice")
    client_code("contract")
    print("\n===SHADOW MOD===")
    CONFIG["mode"] = "shadow"
    client_code("report")
    client_code("invoice")
    client_code("contract")
