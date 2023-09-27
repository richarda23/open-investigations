import os

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.pydantic_v1 import BaseModel, root_validator
from typing import Any, Dict, List, Optional, Iterator
from dotenv import load_dotenv
load_dotenv()


class RSpaceLoader(BaseLoader, BaseModel):
    def lazy_load(self) -> Iterator[Document]:
        cli = self._create_rspace_client()
        docs_in_folder = cli.list_folder_tree(folder_id=self.folder_id, typesToInclude=['document'])
        doc_ids = [d['id'] for d in docs_in_folder['records']]
        for doc_id in doc_ids:
            content = ""
            doc = cli.get_document(doc_id)
            content += f"<h2>{doc['name']}<h2/>"
            for f in doc['fields']:
                content += f"<h3>{f['name']}"
                content += f['content']
                content += '\n'

            yield Document(metadata={'source': f"rspace:{doc['globalId']}"}, page_content=content)

    api_key: str
    url: str
    folder_id: str | int

    def _create_rspace_client(self) -> Any:
        """Create a RSpace client."""
        try:
            from rspace_client.eln import eln

        except ImportError:
            raise ImportError("You must run " "`pip install rspace_client")

        try:
            eln = eln.ELNClient(self.url, self.api_key)
            eln.get_status()

        except Exception:
            raise Exception(
                f"Unable to initialise client - is url {self.url} or key of length {len(self.api_key)} correct?")

        return eln

    def load(self) -> List[Document]:
        return list(self.lazy_load())


if __name__ == '__main__':
    loader = RSpaceLoader(url=os.getenv("RSPACE_URL"), api_key=os.getenv("RSPACE_API_KEY"), folder_id="182183")
    lc_docs = loader.lazy_load()
    for lc_doc in lc_docs:
        print(lc_doc.page_content)
        print(lc_doc.metadata)
