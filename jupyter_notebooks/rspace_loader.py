import os

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader
from langchain.pydantic_v1 import BaseModel
from typing import Any, Dict, List, Optional, Iterator, Union
from dotenv import load_dotenv
from langchain.document_loaders import PyPDFLoader


load_dotenv()


class RSpaceLoader(BaseLoader, BaseModel):
    def _load_folder_tree(self) -> Iterator[Document]:
        cli, field_content = self._create_rspace_client()
        docs_in_folder = cli.list_folder_tree(folder_id=self.global_id[2:], typesToInclude=['document'])
        doc_ids = [d['id'] for d in docs_in_folder['records']]
        for doc_id in doc_ids:
            content = ""
            doc = cli.get_document(doc_id)
            content += f"<h2>{doc['name']}<h2/>"
            for f in doc['fields']:
                content += f"{f['name']}\n"
                fc = field_content(f['content'])
                content += fc.get_text()
                content += '\n'
        yield Document(metadata={'source': f"rspace: {doc['name']}-{doc['globalId']}"}, page_content=content)

    def _load_pdf(self) -> Iterator[Document]:
        cli, field_content = self._create_rspace_client()
        file_info = cli.get_file_info(self.global_id)
        print(file_info)
        _, ext = os.path.splitext(file_info['name'])
        if ext.lower() == '.pdf':
            outfile = f"{self.global_id}.pdf"
            cli.download_file(self.global_id, outfile)
            pdf_loader = PyPDFLoader(outfile)
            pdf_docs = pdf_loader.load()
            for pdf in pdf_docs:
                pdf.metadata['rspace_src'] = self.global_id
                yield pdf

    def lazy_load(self) -> Iterator[Document]:
        if 'GL' in self.global_id:
            return self._load_pdf()
        else:
            return self._load_folder_tree()

    api_key: str
    url: str
    global_id: Union[int, str]

    def _create_rspace_client(self) -> Any:
        """Create a RSpace client."""
        try:
            from rspace_client.eln import eln, field_content

        except ImportError:
            raise ImportError("You must run " "`pip install rspace_client")

        try:
            eln = eln.ELNClient(self.url, self.api_key)
            eln.get_status()

        except Exception:
            raise Exception(
                f"Unable to initialise client - is url {self.url} or key of length {len(self.api_key)} correct?")

        return eln, field_content.FieldContent

    def load(self) -> List[Document]:
        return list(self.lazy_load())


if __name__ == '__main__':
    loader = RSpaceLoader(url=os.getenv("RSPACE_URL"), api_key=os.getenv("RSPACE_API_KEY"), global_id="GL1932384")
    lc_docs = loader.lazy_load()
    for lc_doc in lc_docs:
        print(lc_doc.page_content)
        print(lc_doc.metadata)
