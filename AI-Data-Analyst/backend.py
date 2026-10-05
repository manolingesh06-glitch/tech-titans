import os
import re
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"


def describe_dataframe(df):
    """Turn the dataset into a short text description for the AI."""
    lines = ["Columns and types:"]
    for col, dtype in df.dtypes.items():
        lines.append(f"- {col} ({dtype})")
    lines.append("")
    lines.append("First 5 rows:")
    lines.append(df.head(5).to_string())
    return "\n".join(lines)


def get_code_from_ai(question, df):
    """Ask the AI to write pandas code that answers the question."""
    system_prompt = (
        "You are a data analyst. A pandas DataFrame named df is already loaded. "
        "Write Python code that answers the user's question.\n"
        "Rules:\n"
        "- Use only df and pd. No imports, no file access, no print.\n"
        "- Store the final answer in a variable named result.\n"
        "- result must be a number, a string, or a DataFrame.\n"
        "- Reply with ONLY the code. No explanation, no markdown."
    )
    user_prompt = f"{describe_dataframe(df)}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )
    code = response.choices[0].message.content
    # Remove ``` fences in case the AI adds them anyway
    code = re.sub(r"```(?:python)?", "", code).replace("```", "").strip()
    return code


def run_code(code, df):
    """Run the AI's code in a restricted space and return `result`."""
    banned = ["import", "open(", "__", "exec(", "eval(", "os.", "sys."]
    for word in banned:
        if word in code:
            raise ValueError(f"Unsafe code blocked: found '{word}'")

    safe_builtins = {
        "len": len, "sum": sum, "min": min, "max": max, "round": round,
        "abs": abs, "sorted": sorted, "list": list, "str": str,
        "int": int, "float": float, "range": range, "enumerate": enumerate,
        "zip": zip, "dict": dict, "set": set, "tuple": tuple, "bool": bool,
        "any": any, "all": all,
    }
    env = {"__builtins__": safe_builtins, "df": df.copy(), "pd": pd}
    exec(code, env)
    if "result" not in env:
        raise ValueError("The AI's code did not produce a result.")
    return env["result"]


def ask_ai(question, df):
    """Main function: question in, (code, result) out."""
    code = get_code_from_ai(question, df)
    result = run_code(code, df)
    return code, result