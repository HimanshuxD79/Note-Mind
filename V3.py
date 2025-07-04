import os
os.environ["CHROMA_TELEMETRY"] = "FALSE"
import ollama
import chromadb
import psycopg2
from chromadb.errors import NotFoundError
import ast
from tqdm import tqdm
import streamlit as st
from dotenv import load_dotenv
load_dotenv() 
# Disable Chroma telemetry
try:
    chromadb.telemetry.capture = lambda *args, **kwargs: None
except Exception:
    pass

system_prompt = (
    "You are an AI assistant with access to specific memories provided by the user. "
    "When relevant memories are provided, use them to inform your response. "
    "If no relevant memories are provided or if they are not useful, respond based on your general knowledge. "
    "Do not mention the memories unless they are directly relevant to the user's query."
)

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
}

def connect_db():
    return psycopg2.connect(**DB_PARAMS)


conn = connect_db()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS memories (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content TEXT
)
""")
conn.commit()
conn.close()


client = chromadb.PersistentClient(path="./chroma_data")
try:
    vector_db = client.get_or_create_collection(name="memories")
except NotFoundError:
    vector_db = client.create_collection(name="memories")

# Sync existing memories into Chroma (replacing load_memories)
def sync_memories_to_chroma():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM memories")
    memories = cursor.fetchall()
    conn.close()
    existing_ids = set(vector_db.get()['ids'])
    for id, content in memories:
        if str(id) not in existing_ids:
            response = ollama.embeddings(model="nomic-embed-text", prompt=content)
            embedding = response["embedding"]
            vector_db.add(ids=[str(id)], embeddings=[embedding], documents=[content])

sync_memories_to_chroma()

def store_memory(content):
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO memories (content) VALUES (%s) RETURNING id", (content,))
        id = cursor.fetchone()[0]
        conn.commit()
    conn.close()
    # Add to Chroma
    response = ollama.embeddings(model="nomic-embed-text", prompt=content)
    embedding = response["embedding"]
    vector_db.add(ids=[str(id)], embeddings=[embedding], documents=[content])

# Retrieve relevant memories
def retrieve_relevant_memories(queries, results_per_query=2):
    memories = set()
    for query in tqdm(queries, desc="Retrieving memories"):
        response = ollama.embeddings(model="nomic-embed-text", prompt=query)
        query_embedding = response["embedding"]
        results = vector_db.query(query_embeddings=[query_embedding], n_results=results_per_query)
        best_memories = results["documents"][0]
        for memory in best_memories:
            if memory not in memories and 'yes' in classify_memory(query=query, memory=memory):
                memories.add(memory)
    return list(memories)

# Classify memory relevance
def classify_memory(query, memory):
    classify_msg = (
        "You are an embedding classification AI agent. Your input will be a search query and a memory. "
        'You only respond "yes" or "no". '
        "Determine whether the memory contains data directly related to the search query. "
        'Respond "yes" if the memory is exactly what the query needs, "no" otherwise.'
    )
    classify_convo = [
        {"role": "system", "content": classify_msg},
        {"role": "user", "content": "SEARCH QUERY: passport photo location \n\nMEMORY: My passport photo is in C:/folder/"},
        {"role": "assistant", "content": "yes"},
        {"role": "user", "content": "SEARCH QUERY: favorite color \n\nMEMORY: I like blue."},
        {"role": "assistant", "content": "yes"},
        {"role": "user", "content": "SEARCH QUERY: favorite color \n\nMEMORY: The sky is blue."},
        {"role": "assistant", "content": "no"},
        {"role": "user", "content": f"SEARCH QUERY: {query} \n\nMEMORY: {memory}"},
    ]
    response = ollama.chat(model="llama3:8b", messages=classify_convo)
    return response["message"]["content"].strip().lower()


def generate_response(convo):
    response = ""
    stream = ollama.chat(model="llama3:8b", messages=convo, stream=True)
    for chunk in stream:
        content = chunk["message"]["content"]
        response += content
    return response

# Create queries
def create_queries(prompt):
    query_msg = (
        "You are a first principle reasoning search query AI agent. "
        "Create a Python list of queries to search the embeddings database for data necessary to respond to the prompt."
    )
    query_convo = [
        {"role": "system", "content": query_msg},
        {"role": "user", "content": "Write an email to my car insurance company..."},
        {"role": "assistant", "content": '["What is the user name?", "What is the user\'s current auto insurance provider?"]'},
        {"role": "user", "content": prompt},
    ]
    response = ollama.chat(model="llama3:8b", messages=query_convo)
    try:
        return ast.literal_eval(response["message"]["content"])
    except:
        return [prompt]

# Fetch all memories for display
def fetch_all_memories():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT content FROM memories ORDER BY timestamp DESC")
    memories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return memories

# Streamlit UI
st.title("Memory Assistant")

st.info("Use '/memorize <info>' to store information, or ask questions like 'Where is my passport?'")

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Sidebar to show memories
with st.sidebar:
    if st.button("Show Memories"):
        memories = fetch_all_memories()
        if memories:
            for i, memory in enumerate(memories, 1):
                st.write(f"{i}. {memory}")
        else:
            st.write("No memories stored yet.")

# Callback to clear input after submit
def submit_callback():
    user_input = st.session_state.user_input.strip()
    if user_input:
        if user_input.lower().startswith("/memorize"):
            memory = user_input[10:].strip()
            store_memory(memory)
            st.success(f"Memorized: {memory}")
        else:
            with st.spinner("Thinking..."):
                convo = [{"role": "system", "content": system_prompt}]
                queries = create_queries(user_input)
                memories = retrieve_relevant_memories(queries)
                if memories:
                    memories_str = "\n".join(memories)
                    convo.append({"role": "user", "content": f"MEMORIES:\n{memories_str}"})
                convo.append({"role": "user", "content": user_input})
                response = generate_response(convo)
                st.markdown(f"**Assistant:** {response}")
    else:
        st.warning("Please enter a command or question.")
    
    # Clear input
    st.session_state.user_input = ""

# Main input area (uses session state + on_change callback)
st.text_input("Type your command or question", key="user_input", on_change=submit_callback)