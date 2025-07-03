import streamlit as st
import openai
import os

# Set API key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else os.getenv("OPENAI_API_KEY")

# Page Config
st.set_page_config(page_title="Auto Prompt Optimizer", layout="centered")
st.title("PromptCraft - Auto Prompt Optimizer (Crafting high-quality prompts—art that meets logic)")
st.markdown("Improve your prompts using AI-driven suggestions and explanations.")

# Input prompt
user_prompt = st.text_area("Enter your initial prompt", height=20, key="user_prompt")

# Model & parameters
model = st.selectbox("Choose model", ["gpt-3.5-turbo", "gpt-4","gpt-4-0613","gpt-4-1106-preview","gpt-4-0125-previe"], key="model")
temperature = st.slider("Creativity (Temperature)", 0.0, 2.0, 0.7, 0.1, key="temp")
num_suggestions = st.slider("Number of optimized prompts", 1, 10, 5, key="num_suggestions")

# Initialize session state
if "optimized_prompts" not in st.session_state:
    st.session_state.optimized_prompts = []
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None

# Button to generate optimized prompts
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
                st.session_state.selected_prompt = st.session_state.optimized_prompts[0]
            except Exception as e:
                st.error(f"❌ Error generating prompts: {e}")

# Show optimized prompts
if st.session_state.optimized_prompts:
    st.markdown("### ✨ Optimized Prompts")
    st.session_state.selected_prompt = st.radio(
        "Select the best optimized prompt:",
        st.session_state.optimized_prompts,
        index=st.session_state.optimized_prompts.index(st.session_state.selected_prompt) if st.session_state.selected_prompt else 0,
        key="selected_prompt_radio"
    )

    # Store selection
    st.session_state.selected_prompt = st.session_state.selected_prompt_radio

    # Explain why it's better
    if st.button("🤔 Why this prompt is better?"):
        with st.spinner("Generating explanation..."):
            try:
                explain_prompt = f"""Original Prompt: {user_prompt}\n\nImproved Prompt: {st.session_state.selected_prompt}\n\nExplain why the improved prompt is more effective."""
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
    st.info("Enter a prompt and click Optimize to begin.")
