import json
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Prompt Stress Test",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Prompt Stress Test")

st.write(
    "Evaluate how robust a prompt is against ambiguity, prompt injection, jailbreak attempts, bias, edge cases, contradictory instructions, long context, and output consistency."
)

api_key = st.secrets.get("OPENAI_API_KEY", None)

if not api_key:
    st.error("OPENAI_API_KEY not found.")
    st.stop()

client = OpenAI(api_key=api_key)

prompt_input = st.text_area(
    "Paste Prompt",
    height=250
)

if st.button("🧪 Run Stress Test"):

    if not prompt_input.strip():
        st.warning("Please enter a prompt.")
        st.stop()

    analysis_prompt = f"""
You are a Prompt Engineering evaluator.

Evaluate ONLY the prompt below.

Return ONLY valid JSON.

Schema:

{{
"overall_score": 0,
"summary": "",

"ambiguity": {{
"score":0,
"issues":[],
"suggestions":[]
}},

"prompt_injection": {{
"score":0,
"issues":[],
"suggestions":[]
}},

"jailbreak_resistance": {{
"score":0,
"issues":[],
"suggestions":[]
}},

"bias": {{
"score":0,
"issues":[],
"suggestions":[]
}},

"edge_cases": {{
"score":0,
"issues":[],
"suggestions":[]
}},

"contradictions": {{
"score":0,
"issues":[],
"suggestions":[]
}},

"long_context": {{
"score":0,
"issues":[],
"suggestions":[]
}},

"output_consistency": {{
"score":0,
"issues":[],
"suggestions":[]
}}
}}

Prompt:

{prompt_input}
"""

    with st.spinner("Running stress test..."):

        response = client.chat.completions.create(
    model="gpt-5-mini",
    response_format={"type": "json_object"},
    messages=[
        {
            "role":"system",
            "content":"You are an expert Prompt Engineering evaluator. Always return valid JSON only."
        },
        {
            "role":"user",
            "content":analysis_prompt
        }
    ]
        )

    try:

        result = json.loads(response.choices[0].message.content)

        st.success("Stress test completed!")

        st.metric(
            "Overall Robustness Score",
            f"{result['overall_score']}/100"
        )

        st.info(result["summary"])

        sections = [
            ("Ambiguity","ambiguity"),
            ("Prompt Injection","prompt_injection"),
            ("Jailbreak Resistance","jailbreak_resistance"),
            ("Bias","bias"),
            ("Edge Cases","edge_cases"),
            ("Contradictions","contradictions"),
            ("Long Context","long_context"),
            ("Output Consistency","output_consistency")
        ]

        markdown_report = f"# Prompt Stress Test\n\n"
        markdown_report += f"Overall Score: {result['overall_score']}/100\n\n"
        markdown_report += f"{result['summary']}\n\n"

        for title,key in sections:

            data = result[key]

            with st.expander(f"{title} ({data['score']}/100)", expanded=False):

                st.markdown("### Issues")

                if data["issues"]:
                    for item in data["issues"]:
                        st.markdown(f"- {item}")
                else:
                    st.success("No major issues found.")

                st.markdown("### Suggestions")

                if data["suggestions"]:
                    for item in data["suggestions"]:
                        st.markdown(f"- {item}")
                else:
                    st.success("No suggestions.")

            markdown_report += f"## {title}\n"
            markdown_report += f"Score: {data['score']}/100\n\n"

            markdown_report += "Issues\n"

            for item in data["issues"]:
                markdown_report += f"- {item}\n"

            markdown_report += "\nSuggestions\n"

            for item in data["suggestions"]:
                markdown_report += f"- {item}\n"

            markdown_report += "\n"

        st.download_button(
            "📄 Download Markdown Report",
            markdown_report,
            file_name="prompt_stress_test.md",
            mime="text/markdown"
        )

        with st.expander("📋 Original Prompt"):
            st.write(prompt_input)

    except Exception:

        st.error("Model did not return valid JSON.")

        st.code(response.choices[0].message.content)
