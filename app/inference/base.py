from abc import ABC, abstractmethod
from typing import Any
from PIL import Image


class VisionEngine(ABC):
    """Portable inference contract. A future browser/WASM adapter can implement this."""

    @abstractmethod
    def describe(self, image: Image.Image, keywords: list[str] | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def extract(self, image: Image.Image, form: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
