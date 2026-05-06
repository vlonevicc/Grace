import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

load_dotenv()

URLS = [
    "https://missouri.edu/about",
    "https://missouri.edu/academics",
    "https://missouri.edu/student-life",
    "https://housing.missouri.edu/housing-options/",
    "https://housing.missouri.edu/housing-process-guide/",
    "https://housing.missouri.edu/frequently-asked-questions/",
    "https://housing.missouri.edu/housing-accommodations/",
    "https://dining.missouri.edu/locations/",
    "https://dining.missouri.edu/faq/",
    "https://dining.missouri.edu/mizzou-meals/",
    "https://mizzourec.missouri.edu/",
    "https://mizzourec.missouri.edu/memberships/",
    "https://mizzourec.missouri.edu/facilities/",
    "https://mizzourec.missouri.edu/club-sports/",
    "https://mizzourec.missouri.edu/esports/",
    "https://getinvolved.missouri.edu/",
    "https://getinvolved.missouri.edu/student-activities-engagement/",
    "https://missouri.edu/research",
    "https://missouri.edu/admissions",
    "https://engineering.missouri.edu",
    "https://engineering.missouri.edu/academics/",
    "https://engineering.missouri.edu/academics/undergraduate-degrees/",
    "https://engineering.missouri.edu/academics/graduate-degrees/",
    "https://engineering.missouri.edu/academics/minors-and-certificates/",
    "https://engineering.missouri.edu/academics/online/",
    "https://engineering.missouri.edu/about/abet/",
    "https://engineering.missouri.edu/departments/chbme/chbme-faculty/",
    "https://engineering.missouri.edu/departments/cee/cee-faculty/",
    "https://engineering.missouri.edu/departments/eecs/eecs-faculty/",
    "https://engineering.missouri.edu/departments/eit/faculty/",
    "https://engineering.missouri.edu/departments/ise/ise-faculty/",
    "https://engineering.missouri.edu/departments/mae/faculty/",
    "https://engineering.missouri.edu/research/centers/",
    "https://engineering.missouri.edu/about/",
    "https://engineering.missouri.edu/about/meet-the-dean/",
    "https://engineering.missouri.edu/student-services/advising/tutoring/",
    "https://engineering.missouri.edu/engineers-week/",
    "https://engineering.missouri.edu/engineers-week/history/",
    "https://missouri.edu/admissions/cost-and-aid",
    "https://financialaid.missouri.edu/cost-of-attendance/undergraduate/",
    "https://financialaid.missouri.edu/scholarships/undergraduate-scholarships/",
    "https://financialaid.missouri.edu/cost-of-attendance/graduate/",
    "https://financialaid.missouri.edu/scholarships/graduate-professional/",
    "https://financialaid.missouri.edu/help/faq/",
    "https://financialaid.missouri.edu/types-of-aid/",
    "https://missouri.edu/about/mission-values",
    "https://calendar.missouri.edu/academic-calendar/all/search/Spring%202026",
    "https://calendar.missouri.edu/academic-calendar/all/search/Summer%202026",
    "https://calendar.missouri.edu/academic-calendar/all/search/Fall%202026",
    "https://engineering.missouri.edu/faculty/",
    "https://missouri.edu/about/facts-figures",
    "https://missouri.edu/about/columbia",
    "https://missouri.edu/about/traditions",
    "https://missouri.edu/research",
    "https://mutigers.com",
    "https://engage.missouri.edu/events",
    "https://www.mizzou.com/s/1002/alumni/19/interior.aspx?sid=1002&gid=1001&pgid=10458"
]

SYSTEM_PROMPT = """You are Grace, the friendly humanoid robot at the University of Missouri - Columbia.
Use the context above as your main source. If the answer is incomplete, fill in gaps using your knowledge of the University 
of Missouri.
If asked anything unrelated, respond with:
"I can only answer questions about Mizzou."
Keep answers short, clear, and conversational."""

class MizzouKnowledge:
    def __init__(self, ingest=False):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embed_model = "text-embedding-3-small"
        self.llm_model = "gpt-4.1"
        self.index_name = "mizzou-knowledge"

        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

        if self.index_name not in pc.list_indexes().names():
            pc.create_index(
                name=self.index_name,
                dimension=1536,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.index = pc.Index(self.index_name)

        if ingest:
            self._ingest_all(URLS)



    def ask(self, question: str) -> str:
        """Main entry point — query knowledge base and return answer."""
        context = self._query_knowledge(question)

        prompt = f""" Use the context below as your primary source. 
        If the answer is not clearly in the context, use your best judgment to provide 
        a helpful answer related to the Univeristy of Missouri. If you are unsure, say so but still try to help.

Context:
{context}

Question:
{question}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[MizzouKnowledge] LLM error: {e}")
            return "Sorry, I had trouble finding an answer. Please try again."



    def _scrape_page(self, url: str) -> str:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return " ".join(soup.get_text(separator=" ").split())

    def _split_text(self, text: str, chunk_size=500, overlap=100) -> list:
        chunks, start = [], 0
        while start < len(text):
            chunks.append(text[start:start + chunk_size])
            start += chunk_size - overlap
        return chunks

    def _get_embedding(self, text: str) -> list:
        response = self.client.embeddings.create(model=self.embed_model, input=text)
        return response.data[0].embedding

    def _ingest_url(self, url: str):
        print(f"[MizzouKnowledge] Scraping: {url}")
        try:
            text = self._scrape_page(url)
            chunks = self._split_text(text)
            vectors = [
                {
                    "id": f"{url}_{i}",
                    "values": self._get_embedding(chunk),
                    "metadata": {"text": chunk, "source": url}
                }
                for i, chunk in enumerate(chunks)
            ]
            self.index.upsert(vectors)
            print(f"[MizzouKnowledge] Inserted {len(vectors)} chunks from {url}")
        except Exception as e:
            print(f"[MizzouKnowledge] Failed {url}: {e}")

    def _ingest_all(self, urls: list):
        for url in urls:
            self._ingest_url(url)

    def _query_knowledge(self, question: str) -> str:
        embedding = self._get_embedding(question)
        results = self.index.query(vector=embedding, top_k=8, include_metadata=True)
        return "\n".join(m["metadata"]["text"] for m in results["matches"])