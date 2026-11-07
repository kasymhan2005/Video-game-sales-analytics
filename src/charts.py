"""Reusable Plotly charts with consistent visual design."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

PALETTE = ["#60a5fa", "#34d399", "#fb923c", "#c084fc", "#f472b6", "#facc15"]


def style(fig: go.Figure, height: int = 410) -> go.Figure:
    fig.update_layout(
        template="plotly_dark", height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dbeafe", family="Arial"),
        margin=dict(l=12, r=12, t=34, b=18),
        legend=dict(orientation="h", y=-0.2, title_text=""),
        hovermode="x unified",
    )
    fig.update_xaxes(showgrid=False, linecolor="#35465d")
    fig.update_yaxes(gridcolor="rgba(150,180,220,.13)", zeroline=False)
    return fig


def horizontal_ranking(df: pd.DataFrame, label: str, title: str) -> go.Figure:
    ordered = df.sort_values("sales_m")
    fig = px.bar(ordered, x="sales_m", y=label, orientation="h", color_discrete_sequence=[PALETTE[0]],
                 labels={"sales_m": "Million copies", label: ""}, title=title,
                 hover_data={"sales_m": ":.2f", "releases": True} if "releases" in ordered else {"sales_m": ":.2f"})
    return style(fig, max(380, 32 * len(ordered) + 85))


def trend_line(df: pd.DataFrame, title: str, color: str | None = None) -> go.Figure:
    fig = px.line(df, x="Year", y="sales_m", color=color,
                  markers=True if color is None else False, title=title,
                  labels={"sales_m": "Million copies", "Year": "Release year"},
                  color_discrete_sequence=PALETTE)
    fig.update_traces(line_width=3)
    return style(fig)


def donut_mix(df: pd.DataFrame) -> go.Figure:
    fig = px.pie(df, names="region", values="sales_m", hole=.64,
                 title="Regional unit sales share", color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value:.2f}M units<extra></extra>")
    return style(fig)


def heatmap(matrix: pd.DataFrame) -> go.Figure:
    fig = px.imshow(matrix, aspect="auto", color_continuous_scale=["#14243a", "#2563eb", "#60a5fa", "#93c5fd"],
                    labels=dict(color="Million copies", x="Genre", y="Platform"),
                    title="Platform × genre: cumulative unit sales")
    return style(fig, 490)


def box_plot(df: pd.DataFrame) -> go.Figure:
    fig = px.box(df, x="Genre", y="JP_Sales", points="outliers",
                 title="Nintendo games: Japan sales distribution by genre",
                 labels={"JP_Sales": "Million copies", "Genre": "Genre"},
                 color_discrete_sequence=PALETTE)
    fig.update_xaxes(tickangle=-40)
    return style(fig, 510)
