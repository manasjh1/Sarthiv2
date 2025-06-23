import os
from dotenv import load_dotenv
import openai
from pinecone import Pinecone, ServerlessSpec
from keywords import red_list, yellow_list

load_dotenv()

# Load environment variables
api_key = os.getenv("PINECONE_API_KEY")
env = os.getenv("PINECONE_ENV")  
index_name = os.getenv("PINECONE_INDEX")
namespace = os.getenv("PINECONE_NAMESPACE", "distress")
openai.api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# Create Pinecone client
pc = Pinecone(api_key=api_key)

# Create index if it doesn’t exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud=env.split("-")[0], region=env)
    )

index = pc.Index(index_name)

# Generate embeddings
def get_embeddings(text_list):
    response = openai.embeddings.create(
        model=model,
        input=text_list
    )
    return [item.embedding for item in response.data]

# Upload red list
red_embeddings = get_embeddings(red_list)
red_ids = [f"red_{i}" for i in range(len(red_list))]
red_metadata = [{"category": "red", "text": t} for t in red_list]

index.upsert(
    vectors=zip(red_ids, red_embeddings, red_metadata),
    namespace=namespace
)

# Upload yellow list
yellow_embeddings = get_embeddings(yellow_list)
yellow_ids = [f"yellow_{i}" for i in range(len(yellow_list))]
yellow_metadata = [{"category": "yellow", "text": t} for t in yellow_list]

index.upsert(
    vectors=zip(yellow_ids, yellow_embeddings, yellow_metadata),
    namespace=namespace
)

print(f"Uploaded vectors to Pinecone namespace '{namespace}' using model '{model}'")
