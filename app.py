import streamlit as st
import pandas as pd
import json

from pipeline import process_uploaded_file
from plotting import (
    plot_summary,
    plot_gc_distribution,
    plot_length_vs_gc
)


def main():

    st.set_page_config(layout="wide")
    st.title("GenesisQC")
    st.markdown("---")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        processing_mode = st.radio(
            "Processing Mode",
            ["Full Processing", "Statistics Only"]
        )

        filter_ids = st.text_area(
            "Filter by Sequence IDs (comma-separated)",
            placeholder="seq1, seq2, seq3 (optional)"
        )

    uploaded_file = st.file_uploader(
        "Upload your sequence file",
        type=["fa", "fasta", "fna",
              "fq", "fastq",
              "gb", "gbk", "genbank",
              "embl",
              "gz", "bz2"]
    )

    if uploaded_file is None:
        st.info("Upload a file to begin.")
        return

    # File info display
    col1, col2, col3 = st.columns(3)
    col1.metric("Filename", uploaded_file.name)
    col2.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
    col3.metric("Type", uploaded_file.type or "Unknown")

    st.markdown("---")

    try:
        content = uploaded_file.read()

        stats_only = processing_mode == "Statistics Only"

        if st.button("🚀 Process File", type="primary"):

            with st.spinner("Processing..."):
                result = process_uploaded_file(
                    content=content,
                    filename=uploaded_file.name,
                    filter_ids=filter_ids,
                    stats_only=stats_only
                )

            st.success("✅ Processing complete!")

            # ===============================
            # SUMMARY METRICS
            # ===============================
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Format", result["format"].upper())
            col2.metric("Compression", result["compression"].upper())
            col3.metric("Sequences", result["total_sequences"])
            col4.metric("Total Bases", f"{result['total_bases']:,}")

            st.plotly_chart(
                plot_summary(result),
                use_container_width=True
            )

            # ===============================
            # IF FULL PROCESSING
            # ===============================
            if not stats_only and "sequences" in result:

                df = pd.DataFrame(result["sequences"])

                tab1, tab2, tab3 = st.tabs(
                    ["📋 Data Table", "📊 Visualizations", "📥 Export"]
                )

                # -------------------------------
                # Data Table
                # -------------------------------
                with tab1:
                    st.dataframe(df, use_container_width=True)

                # -------------------------------
                # Visualizations
                # -------------------------------
                with tab2:
                    if len(df) > 50000:
                        st.warning("Dataset too large for detailed plotting.")
                    else:
                        col1, col2 = st.columns(2)

                        col1.plotly_chart(
                            plot_gc_distribution(result["sequences"]),
                            use_container_width=True
                        )

                        col2.plotly_chart(
                            plot_length_vs_gc(result["sequences"]),
                            use_container_width=True
                        )

                # -------------------------------
                # Export
                # -------------------------------
                with tab3:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download CSV",
                        data=csv,
                        file_name=f"{uploaded_file.name}_processed.csv",
                        mime="text/csv"
                    )

                    json_str = json.dumps(result, indent=2)
                    st.download_button(
                        "⬇️ Download JSON",
                        data=json_str,
                        file_name=f"{uploaded_file.name}_processed.json",
                        mime="application/json"
                    )

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()
