import os

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.pydantic_v1 import BaseModel, root_validator
from typing import Any, Dict, List, Optional, Iterator
from dotenv import load_dotenv

load_dotenv()


class RSpaceLoader(BaseLoader, BaseModel):
    def lazy_load(self) -> Iterator[Document]:
        pass

    api_key: str
    url: str
    folder_id: str | int

    def _create_rspace_client(self) -> Any:
        """Create a RSpace client."""
        try:
            from rspace_client.eln import eln

        except ImportError:
            raise ImportError("You must run " "`pip install rspace_client")

        eln = eln.ELNClient(self.url, self.api_key)
        eln.get_documents()
        return eln

    def load(self):
        cli = self._create_rspace_client()

        print(cli.get_status())


if __name__ == '__main__':
    loader = RSpaceLoader(url=os.getenv("RSPACE_URL"), api_key=os.getenv("RSPACE_API_KEY"))
    print(loader)
    loader.load()
