from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
import chromadb
from pypdf import PdfReader
from syslog import Syslog


class VectorDB:
    def __init__(self):
        self.syslog = Syslog(log_file="logs/vector_db.log")
        self.dbName = "rag_syscom"
        self.dbPath = "chroma_db"
        self.filepath = "data/syscom.pdf"
        self.chroma_client = None
        self.collection = None

    def loadDataToVectorDB(self):
        try:
            self.chroma_client = chromadb.PersistentClient(path=self.dbPath)
            self.collection = self.chroma_client.get_or_create_collection(name=self.dbName)
            reader = PdfReader(self.filepath)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    self.collection.add(documents=[text], ids=[str(i)])
            self.syslog.log("VectorDB Initializaton Success", level="INFO")
        except:
            self.syslog.log("Initializing VectorDB Failed !", level="ERROR")

    def retriever(self, context):
        results = self.collection.query(query_texts=[context], n_results=3)
        retrieved_text = "\n".join(results["documents"][0]) if results["documents"] else ""
        return retrieved_text


    