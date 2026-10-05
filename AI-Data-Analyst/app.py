import os

import streamlit as st
import pandas as pd
import plotly.express as px

from backend import (
    ask_ai,
    transcribe_audio,
    generate_voice,
    explain_result,
    choose_chart_type,
    generate_insights,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD CSS
# ============================================================

CSS_PATH = os.path.join(
    os.path.dirname(__file__),
    "frontend",
    "style.css",
)

if os.path.exists(CSS_PATH):

    with open(
        CSS_PATH,
        "r",
        encoding="utf-8",
    ) as css_file:

        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )


# ============================================================
# LOAD JAVASCRIPT
# ============================================================

JS_PATH = os.path.join(
    os.path.dirname(__file__),
    "frontend",
    "script.js",
)

if os.path.exists(JS_PATH):

    with open(
        JS_PATH,
        "r",
        encoding="utf-8",
    ) as js_file:

        js_code = js_file.read()

    st.components.v1.html(
        f"""
        <script>
        {js_code}
        </script>
        """,
        height=0,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "question" not in st.session_state:
    st.session_state.question = ""

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# CHART STYLING
# ============================================================

def style_chart(fig, title=None):

    fig.update_layout(
        title=dict(
            text=title or "",
            font=dict(
                size=18,
                color="#172033",
                family="Arial",
            ),
            x=0,
            xanchor="left",
        ),

        height=400,

        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",

        margin=dict(
            l=55,
            r=25,
            t=60,
            b=55,
        ),

        font=dict(
            family="Arial",
            size=12,
            color="#344054",
        ),

        hoverlabel=dict(
            bgcolor="#172033",
            bordercolor="#172033",
            font=dict(
                color="#ffffff",
                size=12,
            ),
        ),

        showlegend=False,
    )

    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="#d9dee7",
        linewidth=1,
        tickfont=dict(
            color="#667085",
            size=11,
        ),
        title_font=dict(
            color="#475467",
            size=12,
        ),
        automargin=True,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#eef1f5",
        gridwidth=1,
        zeroline=False,
        showline=False,
        tickfont=dict(
            color="#667085",
            size=11,
        ),
        title_font=dict(
            color="#475467",
            size=12,
        ),
        automargin=True,
    )

    return fig


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("📊 AI Data Analyst")

    st.caption(
        "Explore your data with AI"
    )

    st.divider()

    st.subheader(
        "How it works"
    )

    st.write(
        "1. Upload your dataset"
    )

    st.write(
        "2. Ask a question"
    )

    st.write(
        "3. AI analyzes your data"
    )

    st.write(
        "4. Get insights and charts"
    )

    st.write(
        "5. Ask follow-up questions"
    )

    st.divider()

    if st.button(
        "🧹 Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.chat_history = []

        st.session_state.question = ""

        st.rerun()

    st.divider()

    st.caption(
        "AI Data Analyst"
    )


# ============================================================
# HEADER
# ============================================================

st.caption(
    "AI-POWERED DATA ANALYSIS"
)

st.title(
    "Understand your data in plain English."
)

st.write(
    "Upload a CSV or Excel file, ask questions naturally, "
    "and get analysis, explanations, charts, and voice answers."
)

st.divider()


# ============================================================
# UPLOAD
# ============================================================

st.header(
    "📁 Upload your dataset"
)

st.caption(
    "Supported formats: CSV and Excel"
)

uploaded_file = st.file_uploader(
    "Choose your dataset",
    type=[
        "csv",
        "xlsx",
    ],
)


if uploaded_file is None:

    st.info(
        "Upload a dataset to start exploring your data."
    )

    st.stop()


# ============================================================
# LOAD DATASET
# ============================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):

        df = pd.read_csv(
            uploaded_file
        )

    else:

        df = pd.read_excel(
            uploaded_file
        )

except Exception as error:

    st.error(
        f"Could not load the dataset: {error}"
    )

    st.stop()


st.success(
    f"Dataset loaded: {uploaded_file.name}"
)


# ============================================================
# DATASET OVERVIEW
# ============================================================

st.header(
    "📊 Dataset Overview"
)

st.caption(
    "A quick summary of your uploaded dataset."
)


total_rows = len(df)

total_columns = len(df.columns)

total_missing = int(
    df.isna().sum().sum()
)

numeric_columns = (
    df.select_dtypes(
        include="number"
    )
    .columns
    .tolist()
)


metric1, metric2, metric3, metric4 = st.columns(4)


with metric1:

    st.metric(
        "Rows",
        f"{total_rows:,}",
    )


with metric2:

    st.metric(
        "Columns",
        total_columns,
    )


with metric3:

    st.metric(
        "Missing Values",
        f"{total_missing:,}",
    )


with metric4:

    st.metric(
        "Numeric Columns",
        len(numeric_columns),
    )


# ============================================================
# DATA PREVIEW
# ============================================================

with st.expander(
    "📋 View Dataset Preview"
):

    st.dataframe(
        df.head(100),
        width="stretch",
    )


# ============================================================
# DATA TYPES
# ============================================================

with st.expander(
    "🔎 View Column Data Types"
):

    datatype_df = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": [
                str(dtype)
                for dtype in df.dtypes
            ],
        }
    )

    st.dataframe(
        datatype_df,
        width="stretch",
    )


# ============================================================
# QUICK INSIGHTS
# ============================================================

st.header(
    "🔎 Quick Insights"
)

st.caption(
    "Basic observations calculated directly from your dataset."
)


if total_missing == 0:

    st.success(
        "No missing values were detected."
    )

else:

    st.warning(
        f"{total_missing:,} missing values were detected."
    )


if numeric_columns:

    insight_count = min(
        len(numeric_columns),
        3,
    )

    insight_columns = st.columns(
        insight_count
    )

    for index, column in enumerate(
        numeric_columns[:3]
    ):

        series = df[column].dropna()

        if len(series) == 0:
            continue

        with insight_columns[index]:

            st.metric(
                f"Average · {column}",
                f"{series.mean():,.2f}",
            )

            st.caption(
                f"Minimum: {series.min():,.2f}"
            )

            st.caption(
                f"Maximum: {series.max():,.2f}"
            )


# ============================================================
# DATA EXPLORATION CHART
# ============================================================

if numeric_columns:

    st.header("📈 Explore Your Data")

    st.caption(
        "Explore the distribution and basic statistics of a numeric column."
    )

    selected_column = st.selectbox(
        "Numeric column",
        numeric_columns,
        key="basic_chart_column",
    )

    chart_data = (
        pd.to_numeric(
            df[selected_column],
            errors="coerce"
        )
        .dropna()
    )

    if len(chart_data) > 0:

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        average = chart_data.mean()
        median = chart_data.median()
        minimum = chart_data.min()
        maximum = chart_data.max()

        stat1, stat2, stat3, stat4 = st.columns(4)

        with stat1:
            st.metric(
                "Average",
                f"{average:,.2f}"
            )

        with stat2:
            st.metric(
                "Median",
                f"{median:,.2f}"
            )

        with stat3:
            st.metric(
                "Minimum",
                f"{minimum:,.2f}"
            )

        with stat4:
            st.metric(
                "Maximum",
                f"{maximum:,.2f}"
            )


        # ----------------------------------------------------
        # SMART NUMBER OF BINS
        # ----------------------------------------------------

        unique_values = chart_data.nunique()

        if unique_values <= 20:

            number_of_bins = unique_values

        elif unique_values <= 100:

            number_of_bins = 18

        else:

            number_of_bins = 25


        # ----------------------------------------------------
        # HISTOGRAM
        # ----------------------------------------------------

        histogram = px.histogram(
            chart_data,
            x=selected_column,
            nbins=number_of_bins,
        )

        histogram.update_traces(
            marker_color="#6ea8df",
            marker_line_color="#ffffff",
            marker_line_width=1,
            opacity=0.88,

            hovertemplate=(
                "<b>%{x}</b><br>"
                "Records: %{y}"
                "<extra></extra>"
            ),
        )


        # ----------------------------------------------------
        # MEAN LINE
        # ----------------------------------------------------

        histogram.add_vline(
            x=average,
            line_width=2,
            line_dash="dash",
            line_color="#344054",
            annotation_text="Average",
            annotation_position="top",
        )


        # ----------------------------------------------------
        # MEDIAN LINE
        # ----------------------------------------------------

        histogram.add_vline(
            x=median,
            line_width=2,
            line_dash="dot",
            line_color="#667085",
            annotation_text="Median",
            annotation_position="bottom",
        )


        # ----------------------------------------------------
        # CHART STYLE
        # ----------------------------------------------------

        histogram.update_layout(
            height=360,

            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",

            margin=dict(
                l=45,
                r=25,
                t=55,
                b=45,
            ),

            title=dict(
                text=f"{selected_column} Distribution",
                font=dict(
                    size=18,
                    color="#172033",
                    family="Arial",
                ),
                x=0,
            ),

            font=dict(
                family="Arial",
                size=12,
                color="#344054",
            ),

            hoverlabel=dict(
                bgcolor="#172033",
                font=dict(
                    color="#ffffff",
                ),
            ),

            showlegend=False,
        )


        # ----------------------------------------------------
        # X AXIS
        # ----------------------------------------------------

        histogram.update_xaxes(
            title_text=selected_column,

            showgrid=False,

            showline=True,
            linecolor="#d9dee7",

            tickfont=dict(
                color="#667085",
                size=11,
            ),

            title_font=dict(
                color="#475467",
                size=12,
            ),

            automargin=True,
        )


        # ----------------------------------------------------
        # Y AXIS
        # ----------------------------------------------------

        histogram.update_yaxes(
            title_text="Records",

            showgrid=True,
            gridcolor="#eef1f5",
            gridwidth=1,

            zeroline=False,

            showline=False,

            tickfont=dict(
                color="#667085",
                size=11,
            ),

            title_font=dict(
                color="#475467",
                size=12,
            ),

            automargin=True,
        )


        # ----------------------------------------------------
        # DISPLAY
        # ----------------------------------------------------

        st.plotly_chart(
            histogram,
            width="stretch",
            config={
                "displayModeBar": False,
                "responsive": True,
            },
        )


    else:

        st.warning(
            f"No numeric values available for {selected_column}."
        )
# ============================================================
# AI ADVANCED INSIGHTS
# ============================================================

st.header(
    "💡 AI-Generated Insights"
)

st.caption(
    "Let AI identify important trends, patterns, changes, "
    "and interesting observations."
)


if st.button(
    "✨ Generate Advanced Insights",
    use_container_width=True,
):

    try:

        with st.spinner(
            "AI is analyzing your dataset..."
        ):

            insights = generate_insights(
                df
            )

        st.markdown(
            insights
        )

    except Exception as error:

        st.error(
            f"Could not generate insights: {error}"
        )


# ============================================================
# ASK YOUR DATA
# ============================================================

st.header(
    "💬 Ask Your Data"
)

st.caption(
    "Ask questions in normal language or use your voice."
)


# ============================================================
# CONVERSATION HISTORY
# ============================================================

if st.session_state.chat_history:

    st.subheader(
        "Conversation"
    )

    for item in st.session_state.chat_history:

        with st.chat_message("user"):

            st.write(
                item["question"]
            )

        with st.chat_message("assistant"):

            st.write(
                item["answer"]
            )


# ============================================================
# QUESTION INPUT
# ============================================================

question = st.text_input(
    "Your question",
    value=st.session_state.question,
    placeholder=(
        "Example: What is the average bill amount?"
    ),
)


st.session_state.question = question


# ============================================================
# VOICE INPUT
# ============================================================

st.write(
    "🎤 Ask by voice"
)


audio_input = st.audio_input(
    "Record your question",
    sample_rate=16000,
)


if audio_input is not None:

    try:

        with st.spinner(
            "Transcribing your question..."
        ):

            voice_question = transcribe_audio(
                audio_input
            )

        if voice_question:

            st.session_state.question = (
                voice_question
            )

            st.success(
                "Voice question detected."
            )

            st.write(
                f"**You asked:** {voice_question}"
            )

    except Exception as error:

        st.error(
            f"Could not understand the voice input: {error}"
        )


# ============================================================
# ANALYZE
# ============================================================

if st.button(
    "🔍 Analyze",
    use_container_width=True,
):

    current_question = (
        st.session_state.question.strip()
    )


    if not current_question:

        st.warning(
            "Please enter a question first."
        )

    else:

        try:

            # =================================================
            # CONVERSATION CONTEXT
            # =================================================

            conversation_context = ""

            if st.session_state.chat_history:

                conversation_context = (
                    "\n\nPrevious conversation:\n"
                )

                for item in (
                    st.session_state.chat_history[-5:]
                ):

                    conversation_context += (
                        f"User: {item['question']}\n"
                        f"AI: {item['answer']}\n"
                    )

                conversation_context += (
                    "\nCurrent question:\n"
                )


            ai_question = (
                conversation_context
                + current_question
            )


            # =================================================
            # AI ANALYSIS
            # =================================================

            with st.spinner(
                "🤖 Analyzing your data..."
            ):

                code, result = ask_ai(
                    ai_question,
                    df,
                )


            # =================================================
            # EXPLANATION
            # =================================================

            with st.spinner(
                "🧠 Preparing explanation..."
            ):

                explanation = explain_result(
                    current_question,
                    result,
                )


            # =================================================
            # SAVE CONVERSATION
            # =================================================

            st.session_state.chat_history.append(
                {
                    "question": current_question,
                    "answer": explanation,
                }
            )


            # =================================================
            # AI ANSWER
            # =================================================

            with st.chat_message(
                "assistant"
            ):

                st.write(
                    explanation
                )


            # =================================================
            # VOICE OUTPUT
            # =================================================

            try:

                with st.spinner(
                    "🔊 Preparing voice answer..."
                ):

                    audio_data = generate_voice(
                        explanation
                    )

                st.audio(
                    audio_data,
                    format="audio/wav",
                )

            except Exception as voice_error:

                st.warning(
                    f"Voice output unavailable: {voice_error}"
                )


            # =================================================
            # DATAFRAME RESULT
            # =================================================

            if isinstance(
                result,
                pd.DataFrame,
            ):

                st.subheader(
                    "📊 Supporting Data"
                )

                st.dataframe(
                    result,
                    width="stretch",
                )


                chart_numeric_columns = (
                    result
                    .select_dtypes(
                        include="number"
                    )
                    .columns
                    .tolist()
                )

                chart_text_columns = (
                    result
                    .select_dtypes(
                        exclude="number"
                    )
                    .columns
                    .tolist()
                )


                # =================================================
                # AI CHART
                # =================================================

                if chart_numeric_columns:

                    st.subheader(
                        "📈 AI-Generated Chart"
                    )

                    try:

                        chart_type = choose_chart_type(
                            current_question,
                            result,
                        )

                    except Exception:

                        chart_type = "bar"


                    st.caption(
                        f"Visualization selected by AI: "
                        f"**{chart_type.title()}**"
                    )


                    # =================================================
                    # LINE CHART
                    # =================================================

                    if (
                        chart_type == "line"
                        and chart_text_columns
                    ):

                        x_column = (
                            chart_text_columns[0]
                        )

                        y_column = (
                            chart_numeric_columns[0]
                        )

                        fig = px.line(
                            result,
                            x=x_column,
                            y=y_column,
                            markers=True,
                        )

                        fig.update_traces(
                            line=dict(
                                width=3,
                            ),
                            marker=dict(
                                size=7,
                            ),
                            hovertemplate=(
                                "<b>%{x}</b><br>"
                                f"{y_column}: "
                                "%{y}"
                                "<extra></extra>"
                            ),
                        )

                        fig = style_chart(
                            fig,
                            f"{y_column} over {x_column}",
                        )

                        fig.update_xaxes(
                            title_text=x_column
                        )

                        fig.update_yaxes(
                            title_text=y_column
                        )


                    # =================================================
                    # PIE / DONUT CHART
                    # =================================================

                    elif (
                        chart_type == "pie"
                        and chart_text_columns
                    ):

                        name_column = (
                            chart_text_columns[0]
                        )

                        value_column = (
                            chart_numeric_columns[0]
                        )

                        fig = px.pie(
                            result,
                            names=name_column,
                            values=value_column,
                            hole=0.42,
                        )

                        fig.update_traces(
                            textposition="inside",
                            textinfo="percent",
                            hovertemplate=(
                                "<b>%{label}</b><br>"
                                "Value: %{value}<br>"
                                "Share: %{percent}"
                                "<extra></extra>"
                            ),
                        )

                        fig.update_layout(
                            height=400,
                            paper_bgcolor="#ffffff",
                            plot_bgcolor="#ffffff",
                            margin=dict(
                                l=25,
                                r=25,
                                t=60,
                                b=25,
                            ),
                            title=dict(
                                text=(
                                    f"{value_column} "
                                    f"by "
                                    f"{name_column}"
                                ),
                                font=dict(
                                    size=18,
                                    color="#172033",
                                ),
                                x=0,
                            ),
                            font=dict(
                                family="Arial",
                                color="#344054",
                            ),
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.15,
                                xanchor="center",
                                x=0.5,
                            ),
                        )


                    # =================================================
                    # SCATTER CHART
                    # =================================================

                    elif (
                        chart_type == "scatter"
                        and len(chart_numeric_columns) >= 2
                    ):

                        x_column = (
                            chart_numeric_columns[0]
                        )

                        y_column = (
                            chart_numeric_columns[1]
                        )

                        fig = px.scatter(
                            result,
                            x=x_column,
                            y=y_column,
                        )

                        fig.update_traces(
                            marker=dict(
                                size=9,
                                opacity=0.75,
                            ),
                            hovertemplate=(
                                f"<b>{x_column}</b>: "
                                "%{x}<br>"
                                f"<b>{y_column}</b>: "
                                "%{y}"
                                "<extra></extra>"
                            ),
                        )

                        fig = style_chart(
                            fig,
                            f"{y_column} vs {x_column}",
                        )

                        fig.update_xaxes(
                            title_text=x_column
                        )

                        fig.update_yaxes(
                            title_text=y_column
                        )


                    # =================================================
                    # BAR CHART
                    # =================================================

                    else:

                        x_column = (
                            chart_text_columns[0]
                            if chart_text_columns
                            else None
                        )

                        y_column = (
                            chart_numeric_columns[0]
                        )


                        # ---------------------------------------------
                        # MANY CATEGORIES
                        # Horizontal ranked bars
                        # ---------------------------------------------

                        if (
                            x_column
                            and len(result) >= 7
                        ):

                            sorted_result = (
                                result
                                .sort_values(
                                    y_column,
                                    ascending=True,
                                )
                            )

                            fig = px.bar(
                                sorted_result,
                                x=y_column,
                                y=x_column,
                                orientation="h",
                            )

                            fig.update_traces(
                                marker_line_width=0,
                                opacity=0.88,
                                hovertemplate=(
                                    f"<b>%{{y}}</b><br>"
                                    f"{y_column}: %{{x}}"
                                    "<extra></extra>"
                                ),
                            )

                            fig = style_chart(
                                fig,
                                f"{y_column} by {x_column}",
                            )

                            fig.update_xaxes(
                                title_text=y_column
                            )

                            fig.update_yaxes(
                                title_text=x_column
                            )


                        # ---------------------------------------------
                        # SMALL NUMBER OF CATEGORIES
                        # Vertical bars
                        # ---------------------------------------------

                        elif x_column:

                            fig = px.bar(
                                result,
                                x=x_column,
                                y=y_column,
                            )

                            fig.update_traces(
                                marker_line_width=0,
                                opacity=0.88,
                                hovertemplate=(
                                    f"<b>%{{x}}</b><br>"
                                    f"{y_column}: %{{y}}"
                                    "<extra></extra>"
                                ),
                            )

                            fig = style_chart(
                                fig,
                                f"{y_column} by {x_column}",
                            )

                            fig.update_xaxes(
                                title_text=x_column
                            )

                            fig.update_yaxes(
                                title_text=y_column
                            )


                        # ---------------------------------------------
                        # NUMERIC ONLY
                        # ---------------------------------------------

                        else:

                            fig = px.bar(
                                result,
                                y=y_column,
                            )

                            fig.update_traces(
                                marker_line_width=0,
                                opacity=0.88,
                                hovertemplate=(
                                    f"{y_column}: %{{y}}"
                                    "<extra></extra>"
                                ),
                            )

                            fig = style_chart(
                                fig,
                                y_column,
                            )

                            fig.update_yaxes(
                                title_text=y_column
                            )


                    # =================================================
                    # DISPLAY CHART
                    # =================================================

                    st.plotly_chart(
                        fig,
                        width="stretch",
                        config={
                            "displayModeBar": False,
                            "responsive": True,
                        },
                    )


            # =================================================
            # SERIES RESULT
            # =================================================

            elif isinstance(
                result,
                pd.Series,
            ):

                st.subheader(
                    "📊 Supporting Data"
                )

                st.dataframe(
                    result,
                    width="stretch",
                )


            # =================================================
            # AI GENERATED CODE
            # =================================================

            with st.expander(
                "🧑‍💻 Show AI-generated Python code"
            ):

                st.code(
                    code,
                    language="python",
                )


        except Exception as error:

            st.error(
                f"Sorry, I couldn't answer that: {error}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Data Analyst · Intelligent dataset exploration"
)