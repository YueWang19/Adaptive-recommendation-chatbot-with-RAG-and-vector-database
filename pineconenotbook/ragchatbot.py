import os
import time
from pinecone import Pinecone, ServerlessSpec 
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

# Set your API keys
os.environ['PINECONE_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''

# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Define embeddings
# model_name = 'text-embedding-ada-002'
model_name = 'text-embedding-3-small'
embeddings = OpenAIEmbeddings(
    model=model_name,
    openai_api_key=os.environ.get('OPENAI_API_KEY')
)

# Define index and namespace
index_name = "coop-bot"
namespace = "coopvector"

# Setup Pinecone index
cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
region = os.environ.get('PINECONE_REGION') or 'us-east-1'
spec = ServerlessSpec(cloud=cloud, region=region)

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric="cosine",
        spec=spec
    )
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

# Prepare document for search
markdown_document = """## Introduction

Welcome to the dynamic and integrative world of Cooperative Education at Northeastern University, a premier program designed to weave real-world experience with academic study across a variety of global industries. This program is not just about gaining work experience, but about creating a tapestry of learning that enhances your academic journey and prepares you for a successful career. Dive into the depths of this innovative program, where practical experience meets academic rigor to create a unique and enriching educational adventure.

## Program Overview

Northeastern's Cooperative Education program, or co-op, is a cornerstone of the university's experiential learning model. Students alternate between academic study and full-time employment, gaining experience in fields directly related to their academic and career interests. This blend of classroom and practical learning provides a holistic education that enhances both personal and professional growth.

### Key Features

- **Full-Time Employment**: Engage in full-time work in positions that complement your academic pursuits.
- **Global Opportunities**: Explore work opportunities across the globe, applying your knowledge in diverse cultural and professional settings.
- **Integrated Learning**: Apply classroom theories to practical challenges in the workplace, enhancing your academic knowledge and professional skills simultaneously.

### General Requirements

- **Enrollment**: Must be enrolled as a full-time student.
- **Academic Standing**: Complete at least two full-time semesters prior to your first co-op.
- **Pre-Co-op Preparation**: Fulfill all college-specific pre-co-op requirements.

### Special Provisions for Diverse Student Groups

- **Transfer Students**: Complete similar pre-co-op prerequisites and at least one semester at Northeastern.
- **International Students**: Fulfill one academic year and secure proper work authorization.

## Academic Requirements

Experience work in a full-time role, defined by either one full-time job or multiple part-time positions, ensuring a minimum of 32-40 hours per week. The co-op is assessed on a Satisfactory/Unsatisfactory basis, influencing your academic standing and professional trajectory.

## Getting Started

Embark on your co-op journey by following these whimsical yet practical steps:

1. **Validation of Eligibility**: Meet with a co-op coordinator to verify your readiness and eligibility.
2. **Position Selection**: Utilize Northeastern's extensive job portal to find and secure a position that aligns with your career goals.
3. **Official Registration**: Register your co-op position through the university’s designated system, ensuring all details are correctly documented.

## Troubleshooting Common Co-op Conundrums

Even in a well-structured program like co-op, challenges may arise. Here are some quick fixes:

- **Problem: Difficulty in Securing a Position**:
  - **Magic Fix**: Enhance your resume and interview skills with help from career services.
  
- **Problem: Co-op Registration Errors**:
  - **Magic Fix**: Double-check all details for accuracy and consult your co-op advisor for immediate rectification.
  
- **Problem: Work Authorization Issues (International Students)**:
  - **Magic Fix**: Contact the Office of Global Services well in advance to ensure all paperwork is flawless.

## Conclusion

Step into the world of Cooperative Education at Northeastern University where academic theories and professional realities intermingle to prepare you for a future as vibrant and dynamic as the co-op program itself. Forge your path, gather invaluable experiences, and build a robust professional network through a program designed to elevate your educational journey."""  # Add your markdown document here
headers_to_split_on = [("##", "Header 2")]
markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on, strip_headers=False
)
md_header_splits = markdown_splitter.split_text(markdown_document)

print(md_header_splits)

# Create vector store
docsearch = PineconeVectorStore.from_documents(
    documents=md_header_splits,
    index_name=index_name,
    embedding=embeddings,
    namespace=namespace
)
time.sleep(1)

index = pc.Index(index_name)

for ids in index.list(namespace=namespace):
    query = index.query(
        id=ids[0],
        namespace=namespace,
        top_k=1,
        include_values=True,
        include_metadata=True
    )
    print(query)

# Initialize the LLM and QA system
llm = ChatOpenAI(
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
    model_name='gpt-3.5-turbo',
    temperature=0.0
)
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=docsearch.as_retriever()
)

def get_answers(query):
    return qa.invoke(query)

# Sample queries
queries = [
    "What are the Academic Requirements of northeastern university Cooperative Education?",
    "How do I register for Co-op?",
    "What are the most popular foods at Northeastern University?"
]

if __name__ == "__main__":
    for query in queries:
        print(f"Query: {query}")
        print(f"Answer: {get_answers(query)}\n")
