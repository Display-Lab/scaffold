from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class CommunicationRequest:
    identifier: str
    status: str = "active"
    subject_reference: str | None = None
    authored_on: str | None = None
    about: list[dict[str, object]] = field(default_factory=list)
    payload: list[dict[str, object]] = field(default_factory=list)
    contained: list[dict[str, object]] = field(default_factory=list)
    extension: list[dict[str, object]] = field(default_factory=list)

    def add_about(
        self,
        reference: str | None = None,
        display: str | None = None,
        type: str | None = None,
        identifier_system: str | None = None,
        identifier_value: str | None = None,
    ) -> "CommunicationRequest":
        if reference is None and identifier_value is None:
            raise ValueError("About requires a reference or an identifier value")

        identifier = (
            self._identifier_json(identifier_system, identifier_value)
            if identifier_value is not None
            else None
        )
        optional_fields = {
            "reference": reference,
            "identifier": identifier,
            "type": type,
            "display": display,
        }
        about = {
            key: value for key, value in optional_fields.items() if value is not None
        }

        self.about.append(about)
        return self

    @staticmethod
    def _identifier_json(system: str | None, value: str) -> dict[str, object]:
        identifier: dict[str, object] = {"value": value}
        if system is not None:
            identifier["system"] = system
        return identifier

    def add_text_payload(self, content: str) -> "CommunicationRequest":
        self.payload.append({"contentString": content})
        return self

    def add_attachment_payload(
        self,
        content_type: str,
        data: str | None = None,
        url: str | None = None,
        title: str | None = None,
    ) -> "CommunicationRequest":
        if data is None and url is None:
            raise ValueError("Attachment requires data or url")

        attachment: dict[str, object] = {"contentType": content_type}
        if data is not None:
            attachment["data"] = data
        if url is not None:
            attachment["url"] = url
        if title is not None:
            attachment["title"] = title

        self.payload.append({"contentAttachment": attachment})
        return self

    def add_extension(
        self,
        url: str,
        value_key: str | None = None,
        value: object | None = None,
        extensions: list[dict[str, object]] | None = None,
    ) -> "CommunicationRequest":
        self.extension.append(self.build_extension(url, value_key, value, extensions))
        return self

    @staticmethod
    def build_extension(
        url: str,
        value_key: str | None = None,
        value: object | None = None,
        extensions: list[dict[str, object]] | None = None,
    ) -> dict[str, object]:
        if value_key is None and not extensions:
            raise ValueError("Extension requires a value or nested extensions")

        extension: dict[str, object] = {"url": url}
        if value_key is not None:
            extension[value_key] = value
        if extensions:
            extension["extension"] = deepcopy(extensions)

        return extension

    def add_contained(self, resource: dict[str, object]) -> "CommunicationRequest":
        resource_type = resource.get("resourceType")
        resource_id = resource.get("id")
        if not isinstance(resource_type, str) or not resource_type:
            raise ValueError("Contained resource requires resourceType")
        if not isinstance(resource_id, str) or not resource_id:
            raise ValueError("Contained resource requires id")
        if any(item.get("id") == resource_id for item in self.contained):
            raise ValueError(f"Contained resource id already exists: {resource_id}")

        self.contained.append(deepcopy(resource))
        return self

    def add_parameters(
        self,
        identifier: str,
        parameters: list[dict[str, object]],
    ) -> "CommunicationRequest":
        return self.add_contained(
            {
                "resourceType": "Parameters",
                "id": identifier,
                "parameter": parameters,
            }
        )

    def to_json(self) -> dict[str, object]:
        resource: dict[str, object] = {
            "resourceType": "CommunicationRequest",
            "id": self.identifier,
            "status": self.status,
        }

        optional_fields = {
            "subject": self._subject_json(),
            "authoredOn": self.authored_on,
            "about": self.about or None,
            "payload": self.payload or None,
            "contained": self.contained or None,
            "extension": self.extension or None,
        }
        resource.update(
            deepcopy(
                {
                    key: value
                    for key, value in optional_fields.items()
                    if value is not None
                }
            )
        )

        return resource

    def _subject_json(self) -> dict[str, str] | None:
        if self.subject_reference is None:
            return None
        return {"reference": self.subject_reference}
