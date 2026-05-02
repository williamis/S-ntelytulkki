import streamlit as st
import anthropic
from vector_store import search_regulations
from regulations import REGULATIONS

# Page Configuration
st.set_page_config(
    page_title="Regulatory AI Copilot – Energy Sector",
    page_icon="⚖️",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query" not in st.session_state:
    st.session_state.query = ""

st.title("⚖️ Regulatory AI Copilot")
st.markdown("**Enterprise-grade regulatory intelligence** – AI assistant for energy sector compliance")
st.divider()

# Sidebar
with st.sidebar:
    st.header("📚 Knowledge Base")
    st.markdown("The database currently includes regulations from:")
    
    categories = list(set(r["category"] for r in REGULATIONS))
    for cat in categories:
        regs_in_cat = [r["name"] for r in REGULATIONS if r["category"] == cat]
        with st.expander(f"📁 {cat} ({len(regs_in_cat)} acts)"):
            for r in regs_in_cat:
                st.markdown(f"- {r}")
    
    st.divider()
    
    st.header("📤 Add Custom Context")
    st.markdown("Upload a custom regulatory text file (e.g., internal policies, new drafts):")
    uploaded_file = st.file_uploader("Upload .txt file", type=["txt"])
    custom_context = ""
    
    if uploaded_file is not None:
        custom_context = uploaded_file.read().decode("utf-8")
        st.success("✅ Custom document loaded successfully!")

    st.divider()
    st.caption("Data sources: Finlex, Energy Authority Finland, and EUR-Lex. Powered by Anthropic Claude.")

# Main Content Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Query the Regulatory Framework")
    
    st.markdown("**Suggested business queries:**")
    examples = [
        "What is the maximum allowed annual increase for electricity distribution fees?",
        "What are the security of supply requirements for distribution network operators?",
        "What mandatory information must be included in an electricity bill?",
        "How is demand response defined in the current legislation?",
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(examples):
        if cols[i % 2].button(example, key=f"example_{i}", use_container_width=True):
            st.session_state["query"] = example

    query = st.text_area(
        "Enter your regulatory query:",
        value=st.session_state.get("query", ""),
        height=100,
        placeholder="e.g., What does the Electricity Market Act say about supply security limits?"
    )

    if st.button("🔍 Generate Analysis", type="primary", use_container_width=True):
        if not query.strip():
            st.warning("Please enter a query first.")
        else:
            relevant_regs = search_regulations(query, n_results=3)
            context = "\n\n".join([
                f"[{r['name']}]\nSource: {r['url']}\n{r['content']}"
                for r in relevant_regs
            ])
            
            if custom_context:
                context += f"\n\n[Uploaded User Document]\n{custom_context}"

            history = st.session_state.messages.copy()
            history.append({"role": "user", "content": query})

            system_prompt = f"""You are a Senior Regulatory Consultant specializing in the European and Finnish energy sectors.

CRITICAL INSTRUCTIONS:
- Always cite specific acts, sections, or directives from the provided database.
- Use professional, clear business language but maintain strict legal accuracy.
- If the answer is not in the provided database, state clearly that you cannot answer. Do not hallucinate.

REGULATORY DATABASE & CONTEXT:
{context}

Structure your response clearly using Markdown:
1. **Executive Summary:** A direct, concise answer to the query.
2. **Legal Basis:** The specific Act/Directive and Section supporting the answer.
3. **Business Implications:** Practical implications for energy sector companies."""

            with st.spinner("Analyzing regulatory framework..."):
                try:
                    client = anthropic.Anthropic()
                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=1000,
                        system=system_prompt,
                        messages=history
                    )
                    answer = response.content[0].text

                    st.session_state.messages.append({"role": "user", "content": query})
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                    st.divider()
                    st.markdown("### 📎 Sources Used")
                    for r in relevant_regs:
                        st.markdown(f"- [{r['name']}]({r['url']})")

                except Exception as e:
                    st.error(f"API Error: {e}")
                    st.info("Ensure that ANTHROPIC_API_KEY is properly set in your environment variables.")

    if st.session_state.messages:
        st.divider()
        st.markdown("### 💬 Conversation History")
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"**🧑 You:** {msg['content']}")
            else:
                st.markdown(f"**⚖️ Copilot:**\n\n{msg['content']}")
            st.divider()
        
        full_conversation = "\n\n".join([
            f"{'USER' if m['role'] == 'user' else 'COPILOT'}: {m['content']}"
            for m in st.session_state.messages
        ])
        st.download_button(
            label="📥 Export Full Conversation",
            data=full_conversation,
            file_name="regulatory_conversation.txt",
            mime="text/plain"
        )
        
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

with col2:
    st.subheader("ℹ️ System Guidelines")
    st.info("""
**Enterprise Capabilities:**
- **Regulatory Database:** Pre-loaded with official energy legislation.
- **Vector Search:** Only the most relevant regulations are retrieved per query.
- **Conversation Memory:** Ask follow-up questions in context.
- **Dynamic Context:** Upload custom documents via sidebar.
- **Executive Output:** Structured reports for C-level executives.
""")
    
    st.subheader("⚠️ Disclaimer")
    st.warning("""
This tool is an AI-powered assistant designed for information retrieval and initial analysis. 
It does not replace formal legal counsel.
""")

st.divider()
st.caption("Regulatory AI Copilot v3.0 | Architecture: Python, Streamlit, ChromaDB, Anthropic Claude | Enterprise Ready")