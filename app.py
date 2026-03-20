import streamlit as st
from groq import Groq
import PyPDF2
import io
import json
import time
from gtts import gTTS

# --- 1. SET WIDE LAYOUT (Must be first line) ---
st.set_page_config(page_title="Learnify.Ai", page_icon="🚀", layout="wide")

# --- INITIALIZE APP MEMORY ---
if "sop_text" not in st.session_state:
    st.session_state.sop_text = ""
if "training_data" not in st.session_state:
    st.session_state.training_data = None
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- CUSTOM THEME TOGGLE & CSS ---
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppToolbar {display: none;}
    </style>
    """
st.markdown(hide_style, unsafe_allow_html=True)

# --- HEADER LAYOUT ---
col_head1, col_head2 = st.columns([8, 2])
with col_head1:
    st.title("🚀 Learnify.Ai: SOP to AI Training System")
    st.markdown("Upload a Standard Operating Procedure (SOP) to instantly generate a complete training module.")
with col_head2:
    st.write("") 
    dark_mode = st.toggle("🌙 Dark/Light Mode", value=True)

if dark_mode:
    st.markdown("<style>.stApp {background-color: #0E1117;} h1, h2, h3, p, li, label, .stMarkdown {color: #FAFAFA !important;}</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp {background-color: #F8F9FA;} h1, h2, h3, p, li, label, .stMarkdown {color: #101116 !important;}</style>", unsafe_allow_html=True)

# --- MAIN INTERFACE ---
uploaded_file = st.file_uploader("Upload SOP (PDF format)", type="pdf")

if st.button("Generate Training Module", type="primary"):
    if not uploaded_file:
        st.warning("Please upload a PDF file first.")
    else:
        try:
            # Securely connect to Groq using the Streamlit Vault
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            
            with st.status("⚙️ Processing SOP Document...", expanded=True) as status:
                st.write("📄 Extracting raw text from PDF...")
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
                sop_text = ""
                for page in pdf_reader.pages:
                    sop_text += page.extract_text()
                time.sleep(0.5) 
                
                st.write("🧠 AI is analyzing and structuring data...")
                json_prompt = f"""
                You are an expert Corporate Trainer at Nutrabay. Analyze the Standard Operating Procedure (SOP) below and return a strictly valid JSON object with exactly four keys. 
                
                "audio_script": A friendly, enthusiastic 2-3 sentence spoken introduction summarizing the SOP.
                "summary": A detailed markdown string of 5-7 comprehensive bullet points explaining the core policies and objectives of the document.
                "guide": A highly detailed, extensively formatted markdown string of the step-by-step training content. Use headings (###) and bold text for emphasis.
                "quiz": A markdown string of a 5-question multiple choice quiz with an answer key at the bottom.
                
                CRITICAL JSON INSTRUCTIONS: 
                1. Return ONLY valid JSON.
                2. DO NOT use Python-style triple quotes ("""). You must use standard double quotes (") for all string values.
                3. You MUST properly escape all newlines inside strings using \\n.
                4. DO NOT wrap the response in ```json or any other markdown formatting.
                
                SOP Content:
                {sop_text}
                """
                
                # Ask Llama 3 on Groq
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": json_prompt}],
                    model="llama-3.1-8b-instant", 
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )
                
                raw_response = chat_completion.choices[0].message.content
                clean_json = raw_response.replace('```json', '').replace('```', '').strip()
                training_data = json.loads(clean_json)
                
                st.write("🎙️ Synthesizing audio briefing...")
                tts = gTTS(text=training_data["audio_script"], lang='en', slow=False)
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                
                # Save to Memory
                st.session_state.sop_text = sop_text
                st.session_state.audio_bytes = audio_buffer.getvalue()
                st.session_state.training_data = training_data
                st.session_state.chat_history = []
                
                status.update(label="✅ Training Module Successfully Generated!", state="complete", expanded=False)

        except Exception as e:
            st.error(f"Error processing document. Details: {e}")

# --- DISPLAY LAYER ---
if st.session_state.training_data:
    st.divider()
    
    col_audio, col_summary = st.columns([1, 1.5], gap="large")
    with col_audio:
        st.info("🎧 **Audio Briefing**")
        st.markdown("Listen to the quick overview before diving into the details.")
        st.audio(st.session_state.audio_bytes, format='audio/mp3')
        
    with col_summary:
        st.success("📌 **Executive Summary**")
        st.markdown(st.session_state.training_data["summary"])
    
    st.write("") 
    
    with st.expander("📖 **View Step-by-Step Training Guide**", expanded=False):
        st.markdown(st.session_state.training_data["guide"])
        
    with st.expander("📝 **Take the 5-Question Evaluation Quiz**", expanded=False):
        st.markdown(st.session_state.training_data["quiz"])
    
    st.write("")
    
    full_export = f"{st.session_state.training_data['summary']}\n\n{st.session_state.training_data['guide']}\n\n{st.session_state.training_data['quiz']}"
    st.download_button(
        label="📥 Download Complete Training Document", 
        data=full_export, 
        file_name="Learnify_Training_Export.md",
        type="primary"
    )
    
    # --- CHATBOT INTERFACE ---
    st.divider()
    st.markdown("### 💬 Document Q&A Assistant")
    st.caption("Ask specific questions about the SOP. The AI will only answer based on the uploaded document.")
    
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if user_question := st.chat_input("E.g., What is the policy for out-of-stock damaged items?"):
        with st.chat_message("user"):
            st.markdown(user_question)
            
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            chat_prompt = f"Answer the user's question STRICTLY based on the following SOP text. If the answer is not in the text, say so.\n\nSOP: {st.session_state.sop_text}\n\nQuestion: {user_question}"
            
            with st.chat_message("assistant"):
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": chat_prompt}],
                    model="llama-3.1-8b-instant",
                    temperature=0.3,
                )
                response_text = chat_completion.choices[0].message.content
                st.markdown(response_text)
                
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"Chat Error: {e}")
