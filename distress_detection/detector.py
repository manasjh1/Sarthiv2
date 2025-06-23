import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

class DistressDetector:
    def __init__(self, threshold=0.65):
        self.threshold = threshold

        # Load environment variables
        self.index_name = os.getenv("PINECONE_INDEX")
        self.namespace = os.getenv("PINECONE_NAMESPACE", "distress")
        self.model_name = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")

        # OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # New Pinecone client
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(self.index_name)

    def get_embedding(self, text: str):
        response = self.client.embeddings.create(
            model=self.model_name,
            input=[text]
        )
        return response.data[0].embedding

    def check(self, message: str) -> int:
        embedding = self.get_embedding(message)
        result = self.index.query(
            vector=embedding,
            top_k=5,
            include_metadata=True,
            namespace=self.namespace
        )

        if result and result.matches:
            match = result.matches[0]
            score = match.score
            category = match.metadata.get("category", "")

            if category == "red" and score >= 0.65:
                return 1
            elif category == "yellow" and score >= 0.55:
                return 2

        return 0
