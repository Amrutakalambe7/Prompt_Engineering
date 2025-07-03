import streamlit as st
import openai
import os

# Set API Key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Streamlit page config
st.set_page_config(page_title="PromptCraft - Auto Prompt Optimizer", layout="centered")
st.markdown("""
    <h1 style='color: #ffcc00;'>PromptCraft - Auto Prompt Optimizer</h1>
    <p style='font-size: 18px;'><i>Crafts high-quality prompts—art meets logic</i></p>
""", unsafe_allow_html=True)

# Custom CSS Styling
st.markdown("""
    <style>
    .main { background-color: #0f1117; color: #ffffff; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .stTextArea textarea { background-color: #1e1e1e; color: #ffffff; border-radius: 0.5rem; }
    .stSelectbox div { color: #ffffff; }
    .stSlider .css-1m4cszk { color: #ffffff; }
    .stRadio div { color: #ffffff; }
    .stButton button {
        background-color: #ff4b4b;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1.2rem;
        font-weight: bold;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #ff3030;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("Improve your prompts using AI-driven suggestions and explanations.")

# Inputs
st.subheader("🖋️ Enter your initial prompt")
user_prompt = st.text_area("", height=120)

model = st.selectbox("Choose model", ["gpt-3.5-turbo", "gpt-4", "gpt-4-0613", "gpt-4-1106-preview", "gpt-4-0125-preview"])
temperature = st.slider("Creativity (Temperature)", 0.0, 2.0, 0.7, 0.1)
num_suggestions = st.slider("Number of optimized prompts", 1, 10, 5)

# Session state initialization
if "optimized_prompts" not in st.session_state:
    st.session_state.optimized_prompts = []
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None

# ------------------ Prompt Comparison Table -------------------
st.markdown("### 🧮 Side-by-Side Prompt Comparison")

def get_complexity(prompt):
    punctuations = ",.;:"
    complexity = sum(1 for c in prompt if c in punctuations) + len(prompt.split())
    return complexity

import pandas as pd
comparison_data = {
    "Prompt #": [f"{i+1}" for i in range(len(st.session_state.optimized_prompts))],
    "Prompt Text": st.session_state.optimized_prompts,
    "Word Count": [len(p.split()) for p in st.session_state.optimized_prompts],
    "Complexity Score": [get_complexity(p) for p in st.session_state.optimized_prompts]
}
df = pd.DataFrame(comparison_data)
st.dataframe(df)

# Optimize Prompt
if st.button("🚀 Optimize Prompt"):
    if user_prompt.strip() == "":
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Generating improved prompts..."):
            system_msg = f"""
            You are a prompt engineering assistant. Your task is to improve user prompts.
            Suggest {num_suggestions} optimized versions of the prompt below, formatted as a numbered list.
            """
            try:
                response = openai.ChatCompletion.create(
                    model=model,
                    temperature=temperature,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                raw_output = response['choices'][0]['message']['content']
                st.session_state.optimized_prompts = [line.strip("1234567890). ").strip()
                                                      for line in raw_output.strip().split("\n") if line.strip()]
                st.session_state.selected_prompt = None  # Reset selection
            except Exception as e:
                st.error(f"❌ Error generating prompts: {e}")

# Show and select from optimized prompts
if st.session_state.optimized_prompts:
    st.markdown("### 🌟 Optimized Prompts")

    selected_prompt = st.radio(
        label="Select the best optimized prompt:",
        options=["⬜️ Select a prompt"] + st.session_state.optimized_prompts,
        key="selected_prompt_radio"
    )

    # Only update if a real prompt is selected
    if selected_prompt != "⬜️ Select a prompt":
        st.session_state.selected_prompt = selected_prompt

    # Save to session state
    if selected_prompt:
        st.session_state.selected_prompt = selected_prompt

    # Explain button
    if st.button("🤔 Why this prompt is better?"):
        if st.session_state.selected_prompt:
            with st.spinner("Generating explanation..."):
                try:
                    explain_prompt = f"""Original Prompt: {user_prompt}

Improved Prompt: {st.session_state.selected_prompt}

Explain why the improved prompt is more effective."""
                    response = openai.ChatCompletion.create(
                        model=model,
                        temperature=0.5,
                        messages=[
                            {"role": "system", "content": "You are a prompt engineering expert who explains prompt design improvements."},
                            {"role": "user", "content": explain_prompt}
                        ]
                    )
                    explanation = response['choices'][0]['message']['content']
                    st.markdown("### 🔍 Explanation:")
                    st.write(explanation)
                except Exception as e:
                    st.error(f"❌ Error generating explanation: {e}")
        else:
            st.warning("⚠️ Please select a prompt first.")
else:
    st.info("Enter a prompt and click Optimize to begin.")
