import streamlit as st
import pandas as pd
import plotly.express as px
from backend import ask_ai

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title("🤖 AI Data Analyst")
st.write(
    "Upload a CSV or Excel dataset and explore it with automatic analysis."
)


# ==========================================
# FILE UPLOAD
# ==========================================

uploaded_file = st.file_uploader(
    "📁 Upload your dataset",
    type=["csv", "xlsx"]
)


# ==========================================
# PROCESS DATASET
# ==========================================

if uploaded_file is not None:

    # --------------------------------------
    # LOAD DATA
    # --------------------------------------

    try:

        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ Dataset loaded successfully!")

    except Exception as e:

        st.error(f"❌ Could not load the dataset: {e}")
        st.stop()


    # ======================================
    # DATASET PREVIEW
    # ======================================

    st.subheader("📋 Dataset Preview")

    display_df = df.copy()

    # Convert object columns to strings
    # to avoid Arrow display errors
    for col in display_df.select_dtypes(include="object").columns:
        display_df[col] = display_df[col].astype(str)

    st.dataframe(
        display_df,
        width="stretch"
    )


    # ======================================
    # DATASET INFORMATION
    # ======================================

    st.subheader("📊 Dataset Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Rows",
            f"{df.shape[0]:,}"
        )

    with col2:
        st.metric(
            "Columns",
            df.shape[1]
        )

    with col3:
        missing_values = int(df.isna().sum().sum())

        st.metric(
            "Missing Values",
            f"{missing_values:,}"
        )


    # ======================================
    # DATA TYPES
    # ======================================

    st.subheader("🔎 Column Data Types")

    datatype_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values
    })

    st.dataframe(
        datatype_df,
        width="stretch"
    )


    # ======================================
    # AUTOMATIC VISUALIZATION
    # ======================================

    st.subheader("📈 Automatic Visualization")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if numeric_columns:

        selected_column = st.selectbox(
            "Select a numeric column",
            numeric_columns
        )

        fig = px.histogram(
            df,
            x=selected_column,
            title=f"Distribution of {selected_column}"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    else:

        st.info(
            "No numeric columns were found for automatic visualization."
        )


    # ======================================
    # SMART DATA INSIGHTS
    # ======================================

    st.subheader("🤖 Smart Data Insights")

    st.write(
        f"Your dataset contains **{df.shape[0]:,} rows** "
        f"and **{df.shape[1]} columns**."
    )


    # --------------------------------------
    # MISSING VALUES INSIGHT
    # --------------------------------------

    total_missing = int(
        df.isna().sum().sum()
    )

    if total_missing == 0:

        st.success(
            "✅ No missing values were detected."
        )

    else:

        st.warning(
            f"⚠️ This dataset contains "
            f"**{total_missing:,} missing values**."
        )


    # --------------------------------------
    # NUMERIC INSIGHTS
    # --------------------------------------

    if numeric_columns:

        st.markdown("### 📊 Numeric Insights")

        for col in numeric_columns[:5]:

            col_data = df[col].dropna()

            if len(col_data) > 0:

                st.write(
                    f"**{col}** — "
                    f"Average: **{col_data.mean():,.2f}** | "
                    f"Minimum: **{col_data.min():,.2f}** | "
                    f"Maximum: **{col_data.max():,.2f}**"
                )


    # --------------------------------------
    # CATEGORICAL INSIGHTS
    # --------------------------------------

    categorical_columns = df.select_dtypes(
        include="object"
    ).columns.tolist()

    if categorical_columns:

        st.markdown("### 🏷️ Category Insights")

        for col in categorical_columns[:5]:

            value_counts = df[col].dropna().value_counts()

            if len(value_counts) > 0:

                top_value = value_counts.index[0]
                top_count = value_counts.iloc[0]

                st.write(
                    f"**{col}** — "
                    f"Most common: **{top_value}** "
                    f"({top_count:,} records)"
                )


    # ======================================
    # FOOTER
    # ======================================

    st.info(
        "💡 Insights are automatically generated "
        "from your uploaded dataset."
    )
    # ======================================
    # ASK YOUR DATA
    # ======================================

    st.subheader("💬 Ask Your Data")

    st.write(
        "Ask a question about your uploaded dataset."
    )

    question = st.text_input(
        "Type your question",
        placeholder="Example: What is the average price?"
    )

    if st.button("🔍 Analyze"):

        if question.strip() == "":
            st.warning("Please enter a question.")

        else:
            try:
                with st.spinner("Thinking..."):
                    code, answer = ask_ai(question, df)

                st.success("Answer:")

                if isinstance(answer, (pd.DataFrame, pd.Series)):
                    st.dataframe(answer, width="stretch")
                else:
                    st.write(answer)

                with st.expander("Show the code the AI wrote"):
                    st.code(code, language="python")

            except Exception as e:
                st.error(f"Sorry, I couldn't answer that: {e}")