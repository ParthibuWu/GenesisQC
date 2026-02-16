import plotly.express as px
import pandas as pd


def plot_summary(result):
    df = pd.DataFrame({
        "Metric": ["Average Length", "Average GC"],
        "Value": [result["average_length"],
                  result["average_gc_content"]]
    })
    return px.bar(df, x="Metric", y="Value",
                  title="File Summary")


def plot_gc_distribution(sequences):
    df = pd.DataFrame(sequences)
    return px.histogram(df,
                        x="GC_content",
                        nbins=30,
                        title="GC Distribution")


def plot_length_vs_gc(sequences):
    df = pd.DataFrame(sequences)
    return px.scatter(df,
                      x="Length",
                      y="GC_content",
                      title="Length vs GC")
