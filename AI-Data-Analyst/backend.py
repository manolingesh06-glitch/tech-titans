import os
import re
import tempfile

import pandas as pd

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# GROQ SETUP
# ============================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "openai/gpt-oss-120b"


# ============================================================
# DATASET DESCRIPTION
# ============================================================

def describe_dataframe(df):
    """Create a useful description of the uploaded dataset."""

    lines = [
        "Dataset information:",
        f"Rows: {len(df):,}",
        f"Columns: {len(df.columns)}",
        "",
        "Columns and data types:"
    ]

    for col, dtype in df.dtypes.items():
        lines.append(f"- {col} ({dtype})")

    numeric_columns = (
        df.select_dtypes(include="number")
        .columns
        .tolist()
    )

    text_columns = (
        df.select_dtypes(exclude="number")
        .columns
        .tolist()
    )

    lines.extend([
        "",
        f"Numeric columns: {numeric_columns}",
        f"Text/category columns: {text_columns}",
        "",
        "First 5 rows:",
        df.head(5).to_string()
    ])

    return "\n".join(lines)


# ============================================================
# AI CODE GENERATION
# ============================================================

def get_code_from_ai(question, df, previous_error=None):

    system_prompt = """
You are an expert Python data analyst.

A pandas DataFrame named df is already loaded.

Write Python code that answers the user's question.

STRICT RULES:

- Use only df and pd.
- Do not import anything.
- Do not access files.
- Do not access the internet.
- Do not use os, sys, subprocess, socket, requests,
  urllib, or environment variables.
- Do not use print().
- Store the final answer in a variable named result.
- result must be a number, string, pandas Series,
  or pandas DataFrame.
- Never assume text is numeric.
- Use pd.to_numeric(..., errors="coerce")
  when numeric conversion is necessary.
- Handle missing values.
- Do not invent data.
- Reply ONLY with Python code.
"""

    user_prompt = (
        describe_dataframe(df)
        + "\n\nUser question:\n"
        + question
    )

    if previous_error:

        user_prompt += (
            "\n\nPrevious code failed with this error:\n"
            + previous_error
            + "\nFix the code."
        )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0
    )

    code = response.choices[0].message.content

    code = re.sub(
        r"```(?:python)?",
        "",
        code
    )

    code = code.replace(
        "```",
        ""
    )

    return code.strip()


# ============================================================
# SAFE CODE EXECUTION
# ============================================================

def run_code(code, df):

    banned = [
        "import ",
        "open(",
        "__",
        "exec(",
        "eval(",
        "os.",
        "sys.",
        "subprocess",
        "socket",
        "requests",
        "urllib"
    ]

    for word in banned:

        if word in code:

            raise ValueError(
                f"Unsafe code blocked: found '{word}'"
            )

    safe_builtins = {
        "len": len,
        "sum": sum,
        "min": min,
        "max": max,
        "round": round,
        "abs": abs,
        "sorted": sorted,
        "list": list,
        "str": str,
        "int": int,
        "float": float,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "bool": bool
    }

    env = {
        "__builtins__": safe_builtins,
        "df": df.copy(),
        "pd": pd
    }

    exec(
        code,
        env
    )

    if "result" not in env:

        raise ValueError(
            "The AI's code did not produce a result."
        )

    return env["result"]


# ============================================================
# MAIN AI ANALYSIS
# ============================================================

def ask_ai(question, df):

    previous_error = None

    for attempt in range(3):

        try:

            code = get_code_from_ai(
                question,
                df,
                previous_error
            )

            result = run_code(
                code,
                df
            )

            return code, result

        except Exception as e:

            previous_error = str(e)

            if attempt == 2:
                raise

    raise ValueError(
        "Unable to analyze the dataset."
    )


# ============================================================
# NATURAL LANGUAGE EXPLANATION
# ============================================================

def explain_result(question, result):

    if isinstance(result, pd.DataFrame):

        result_text = result.to_string(
            index=False
        )

    elif isinstance(result, pd.Series):

        result_text = result.to_string()

    else:

        result_text = str(result)

    prompt = f"""
You are an expert data analyst.

The user asked:

{question}

The Python analysis produced:

{result_text}

Explain the result clearly.

Rules:

- Give the direct answer first.
- Explain what the numbers mean.
- Explain changes between years/categories.
- Calculate percentage changes when appropriate.
- Give an example when requested.
- Do not invent numbers.
- Summarize important trends.
- Use simple language.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clear and accurate "
                    "data analyst."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


# ============================================================
# ADVANCED AI INSIGHTS
# ============================================================

def generate_insights(df):

    dataset_text = describe_dataframe(df)

    prompt = f"""
You are an expert data analyst.

Analyze this dataset:

{dataset_text}

Generate useful high-level insights.

Look for:

1. Important trends
2. Highest and lowest values
3. Large increases or decreases
4. Percentage changes where meaningful
5. Important category differences
6. Missing data
7. Unusual or potentially interesting patterns
8. Useful observations for a normal user

Rules:

- Only use information present in the dataset.
- Do not invent numbers.
- Keep each insight concise.
- Give 5 to 8 useful insights.
- Use simple language.
- Return ONLY a numbered list.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert data analyst "
                    "who finds useful patterns in datasets."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


# ============================================================
# SPEECH TO TEXT
# ============================================================

def transcribe_audio(audio_file):

    transcription = client.audio.transcriptions.create(
        file=(
            "voice.wav",
            audio_file.getvalue()
        ),
        model="whisper-large-v3",
        language="en",
        prompt=(
            "This is a question about data analysis, "
            "datasets, CSV files, Excel files, numbers, "
            "statistics, averages, percentages, trends, "
            "cutoffs, charts, and comparisons."
        ),
        response_format="json",
        temperature=0
    )

    return transcription.text.strip()


# ============================================================
# TEXT TO SPEECH
# ============================================================

def generate_voice(text):

    summary_response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Summarize this answer naturally for speech. "
                    "Keep it under 180 characters. "
                    "Use simple spoken English. "
                    "No Markdown or emojis."
                )
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.2
    )

    spoken_text = (
        summary_response
        .choices[0]
        .message
        .content
        .strip()
    )

    response = client.audio.speech.create(
        model="canopylabs/orpheus-v1-english",
        voice="troy",
        input=spoken_text,
        response_format="wav"
    )

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as audio_file:

        response.write_to_file(
            audio_file.name
        )

        with open(
            audio_file.name,
            "rb"
        ) as f:

            return f.read()


# ============================================================
# AI CHART SELECTION
# ============================================================

def choose_chart_type(question, df):

    prompt = f"""
You are a data visualization expert.

User question:
{question}

Available columns:
{list(df.columns)}

Choose the best chart type.

Allowed values:

bar
line
pie
scatter

Rules:

- line = trends over time
- bar = category comparisons
- pie = simple parts of a whole
- scatter = relationship between two numeric variables

Reply with ONLY one word.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You choose appropriate "
                    "data visualizations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    chart_type = (
        response
        .choices[0]
        .message
        .content
        .strip()
        .lower()
    )

    if chart_type not in [
        "bar",
        "line",
        "pie",
        "scatter"
    ]:

        chart_type = "bar"

    return chart_type