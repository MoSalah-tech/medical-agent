import asyncio

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import os
import sys
from pathlib import Path
from app.medical_agent.core.config import langsmith_api_key

from dotenv import load_dotenv
load_dotenv()

# LangSmith setup (optional)
if os.getenv("LANGSMITH_TRACING") != "true":
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = "medical-agent"
    os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"

from langchain_community.vectorstores import PGVector
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.medical_agent.core.config import database_url_psycopg
from app.medical_agent.core.config import gemini_api_key, gemini_embedding_model
from app.medical_agent.services import rag_service
from app.medical_agent.agents.graph import get_compiled_graph
from app.medical_agent.agents.state import new_state

# Sample medical document text (you can replace with a file later)
SAMPLE_TEXT = """
Patient: John Doe (fictional)
Age: 45
Medical History: Hypertension diagnosed 2015, Type 2 Diabetes 2018.
Medications: Lisinopril 10mg daily, Metformin 500mg twice daily.
Lab Results (2024):
- Fasting glucose: 145 mg/dL (high)
- HbA1c: 7.2%
- Blood pressure: 140/90 mmHg
Recent Visit Notes: Patient reports occasional headaches and fatigue. Recommended follow-up in 3 months.
"""

SAMPLE_TEXT_2 = """ 
Patient: Sarah Lee (fictional)
Age: 62
Sex: Female
Date of Visit: 2024-03-15

Chief Complaint:
Patient presents with persistent dry cough and shortness of breath for the past three weeks. Cough is worse at night and after mild exertion. No fever. No chest pain. Reports mild fatigue.

Past Medical History:
- Hypertension (diagnosed 2010), currently well controlled.
- Hyperlipidemia (diagnosed 2012).
- No known drug allergies.

Current Medications:
- Amlodipine 5 mg once daily
- Atorvastatin 20 mg once daily
- Losartan 50 mg once daily

Lab Results (2024-03-01):
- Total cholesterol: 210 mg/dL (borderline high)
- LDL: 130 mg/dL (borderline high)
- HDL: 48 mg/dL (normal)
- Triglycerides: 150 mg/dL (borderline high)
- Blood pressure: 132/84 mmHg
- Fasting glucose: 98 mg/dL (normal)

Recent Imaging / Tests:
- Chest X-ray (2024-03-10): No acute infiltrates, mild hyperinflation noted. Possible early COPD changes.
- Spirometry: FEV1/FVC ratio 0.68, suggestive of mild obstructive pattern.

Assessment / Plan:
1. Cough and dyspnea likely due to early chronic obstructive pulmonary disease (COPD). Start inhaled bronchodilator (tiotropium 5 mcg daily).
2. Continue current antihypertensive and statin therapy.
3. Smoking cessation counseling provided. Patient has 20 pack-year history, currently smokes 5 cigarettes/day.
4. Follow-up in 6 weeks with repeat spirometry and symptom review.
"""



def get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=gemini_embedding_model,
        google_api_key=gemini_api_key
    )



async def main():
    # 1. Ingest a test document for user_id = "user_456"
    docs = rag_service.chunk_text(SAMPLE_TEXT_2, source="sarah_lee.txt", user_id="user_456")
    rag_service.get_vectorstore().add_documents(docs)
    print("Ingested test document for user_456")

    # 2. Build the graph and run the query inside the context manager
    async with get_compiled_graph() as graph:
        print("Graph compiled and ready.")

        # 3. Ask a question as user_456
        state = new_state(
            query="What medications is the patient taking?",
            session_id="test-full-rag",
            user_id="user_456",
            input_mode="text",
        )
        config = {"configurable": {"thread_id": "test-full-rag-thread"}}

        result = await graph.ainvoke(state, config=config)   # <-- inside block

    # After exiting the block, result is still available
    print("\n--- Agent Response ---")
    print(result.get("response"))

    print("\n--- Citations ---")
    print(result.get("citations"))

if __name__ == "__main__":
    asyncio.run(main())