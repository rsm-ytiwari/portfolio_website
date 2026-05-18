"""End-to-end analysis for the Blueprinty deep dive.

Reads the raw CSV, runs Poisson MLE and Poisson regression, builds six
Plotly figures themed to match the portfolio site, and writes them as
Quarto-includeable `.qmd` snippets (each wrapping the Plotly div+script
in a `{=html}` raw block).

Also writes a `numbers.json` with every quantity cited in the post body.

Run from the repo root:

    uv run --with pandas --with numpy --with scipy --with statsmodels --with plotly \\
        python src/blueprinty/analyze.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import optimize
from scipy.special import gammaln
import statsmodels.api as sm

# ──────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "others" / "blueprinty" / "blueprinty.csv"
ASSETS = ROOT / "posts" / "blueprinty-poisson-mle-assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────
# Site-matched Plotly theme
# Blue = customer (the treatment group, primary accent).
# Violet = non-customer (secondary accent).
# Backgrounds transparent so the site bg (light or dark) shows through.
# ──────────────────────────────────────────────────────────────────────
COLOR_CUST = "#3B82F6"
COLOR_NON = "#A78BFA"
COLOR_NEUTRAL = "#9CA3AF"
COLOR_HIGHLIGHT = "#3B82F6"
COLOR_GRID = "rgba(150,150,150,0.15)"
COLOR_AXIS = "rgba(150,150,150,0.7)"
FONT = dict(family="Geist, system-ui, -apple-system, sans-serif", size=13, color="#888")


def apply_theme(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=FONT,
        height=height,
        margin=dict(t=30, r=20, b=50, l=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(bgcolor="#161614", font=dict(color="#F0EEE8", family="Geist")),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=COLOR_GRID,
        zeroline=False,
        linecolor=COLOR_AXIS,
        tickfont=dict(color=COLOR_AXIS),
        title_font=dict(color=COLOR_AXIS),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLOR_GRID,
        zeroline=False,
        linecolor=COLOR_AXIS,
        tickfont=dict(color=COLOR_AXIS),
        title_font=dict(color=COLOR_AXIS),
    )
    return fig


def save_fig(fig: go.Figure, slug: str) -> None:
    """Write a Plotly figure as a Quarto-includeable .qmd snippet.

    The snippet wraps Plotly's div+script in a Quarto raw-HTML block so the
    main post can `{{< include fileN.qmd >}}` it without the contents being
    parsed as Markdown.
    """
    fragment = fig.to_html(
        include_plotlyjs="cdn",
        full_html=False,
        div_id=slug,
        config={"displayModeBar": False, "responsive": True},
    )
    # Leading underscore signals Quarto to skip rendering this as a standalone
    # page. `{{< include >}}` still resolves by literal path.
    qmd_path = ASSETS / f"_{slug}.qmd"
    qmd_path.write_text(f"```{{=html}}\n{fragment}\n```\n")


# ──────────────────────────────────────────────────────────────────────
# Load + describe
# ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA)
df["age2"] = df["age"] ** 2

numbers: dict = {}

numbers["n_total"] = int(len(df))
numbers["n_customer"] = int((df["iscustomer"] == 1).sum())
numbers["n_noncustomer"] = int((df["iscustomer"] == 0).sum())
numbers["patents_mean"] = float(df["patents"].mean())
numbers["patents_var"] = float(df["patents"].var())
numbers["patents_max"] = int(df["patents"].max())

by_cust = df.groupby("iscustomer")["patents"].agg(["mean", "std", "count"]).to_dict("index")
numbers["mean_patents_noncustomer"] = float(by_cust[0]["mean"])
numbers["mean_patents_customer"] = float(by_cust[1]["mean"])
numbers["raw_gap"] = numbers["mean_patents_customer"] - numbers["mean_patents_noncustomer"]

region_share = pd.crosstab(df["region"], df["iscustomer"], normalize="columns")
numbers["region_share"] = {
    region: {"noncustomer": float(region_share.loc[region, 0]), "customer": float(region_share.loc[region, 1])}
    for region in region_share.index
}

age_by_cust = df.groupby("iscustomer")["age"].agg(["mean", "std"]).to_dict("index")
numbers["mean_age_noncustomer"] = float(age_by_cust[0]["mean"])
numbers["mean_age_customer"] = float(age_by_cust[1]["mean"])

# ──────────────────────────────────────────────────────────────────────
# Fig 1: patents histograms by customer status
# ──────────────────────────────────────────────────────────────────────
fig1 = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=("Non-customers (n=1,019)", "Customers (n=481)"),
    shared_yaxes=True,
    horizontal_spacing=0.08,
)
bins = dict(start=-0.5, end=16.5, size=1)
non = df.loc[df["iscustomer"] == 0, "patents"]
cus = df.loc[df["iscustomer"] == 1, "patents"]
fig1.add_trace(
    go.Histogram(
        x=non,
        xbins=bins,
        marker_color=COLOR_NON,
        opacity=0.85,
        name="Non-customer",
        hovertemplate="Patents: %{x}<br>Firms: %{y}<extra></extra>",
    ),
    row=1,
    col=1,
)
fig1.add_trace(
    go.Histogram(
        x=cus,
        xbins=bins,
        marker_color=COLOR_CUST,
        opacity=0.9,
        name="Customer",
        hovertemplate="Patents: %{x}<br>Firms: %{y}<extra></extra>",
    ),
    row=1,
    col=2,
)
non_mean = float(non.mean())
cus_mean = float(cus.mean())
for col, mean, color in [(1, non_mean, COLOR_NON), (2, cus_mean, COLOR_CUST)]:
    fig1.add_vline(x=mean, line=dict(color=color, dash="dot", width=2), row=1, col=col)
    x_axis_ref = "x" if col == 1 else f"x{col}"
    y_axis_ref = "y domain" if col == 1 else f"y{col} domain"
    fig1.add_annotation(
        x=mean,
        y=1.02,
        xref=x_axis_ref,
        yref=y_axis_ref,
        text=f"mean = {mean:.2f}",
        showarrow=False,
        font=dict(color=color, size=12),
        yanchor="bottom",
    )
fig1.update_xaxes(title_text="Patents awarded over 5 years", range=[-0.5, 16.5])
fig1.update_yaxes(title_text="Number of firms", row=1, col=1)
fig1 = apply_theme(fig1, height=380)
fig1.update_layout(showlegend=False, bargap=0.05)
for a in fig1.layout.annotations:
    if a.text.startswith("Non-customers") or a.text.startswith("Customers"):
        a.font = dict(color="#F0EEE8", size=13, family="Geist")
save_fig(fig1, "fig1-patents-by-customer")

# ──────────────────────────────────────────────────────────────────────
# Fig 2: region distribution by customer status (grouped horizontal bars)
# ──────────────────────────────────────────────────────────────────────
regions_ordered = ["Northeast", "Southwest", "Midwest", "Northwest", "South"]
non_shares = [float(region_share.loc[r, 0]) for r in regions_ordered]
cus_shares = [float(region_share.loc[r, 1]) for r in regions_ordered]
fig2 = go.Figure()
fig2.add_trace(
    go.Bar(
        y=regions_ordered,
        x=non_shares,
        name="Non-customers",
        marker_color=COLOR_NON,
        orientation="h",
        hovertemplate="Region: %{y}<br>Share: %{x:.1%}<extra>Non-customers</extra>",
    )
)
fig2.add_trace(
    go.Bar(
        y=regions_ordered,
        x=cus_shares,
        name="Customers",
        marker_color=COLOR_CUST,
        orientation="h",
        hovertemplate="Region: %{y}<br>Share: %{x:.1%}<extra>Customers</extra>",
    )
)
fig2.update_layout(barmode="group", bargap=0.25)
fig2.update_xaxes(tickformat=".0%", title_text="Share of group based in region", range=[0, 0.75])
fig2.update_yaxes(title_text="", autorange="reversed")
fig2 = apply_theme(fig2, height=420)
save_fig(fig2, "fig2-region-distribution")

# ──────────────────────────────────────────────────────────────────────
# Fig 3: age distributions by customer status (overlaid histograms)
# ──────────────────────────────────────────────────────────────────────
age_bins = dict(start=5, end=55, size=2.5)
fig3 = go.Figure()
fig3.add_trace(
    go.Histogram(
        x=df.loc[df["iscustomer"] == 0, "age"],
        xbins=age_bins,
        histnorm="probability density",
        marker_color=COLOR_NON,
        opacity=0.55,
        name="Non-customers",
        hovertemplate="Age: %{x}<br>Density: %{y:.3f}<extra>Non-customers</extra>",
    )
)
fig3.add_trace(
    go.Histogram(
        x=df.loc[df["iscustomer"] == 1, "age"],
        xbins=age_bins,
        histnorm="probability density",
        marker_color=COLOR_CUST,
        opacity=0.55,
        name="Customers",
        hovertemplate="Age: %{x}<br>Density: %{y:.3f}<extra>Customers</extra>",
    )
)
fig3.add_vline(x=numbers["mean_age_noncustomer"], line=dict(color=COLOR_NON, dash="dot", width=2))
fig3.add_vline(x=numbers["mean_age_customer"], line=dict(color=COLOR_CUST, dash="dot", width=2))
fig3.add_annotation(
    x=numbers["mean_age_noncustomer"],
    y=1.02,
    yref="paper",
    text=f"non-cust mean = {numbers['mean_age_noncustomer']:.1f}",
    showarrow=False,
    font=dict(color=COLOR_NON, size=11),
    yanchor="bottom",
    xshift=-60,
)
fig3.add_annotation(
    x=numbers["mean_age_customer"],
    y=1.02,
    yref="paper",
    text=f"cust mean = {numbers['mean_age_customer']:.1f}",
    showarrow=False,
    font=dict(color=COLOR_CUST, size=11),
    yanchor="bottom",
    xshift=60,
)
fig3.update_layout(barmode="overlay", bargap=0.02)
fig3.update_xaxes(title_text="Firm age (years)", range=[5, 52])
fig3.update_yaxes(title_text="Density")
fig3 = apply_theme(fig3, height=380)
save_fig(fig3, "fig3-age-distribution")

# ──────────────────────────────────────────────────────────────────────
# Section 3: simple Poisson MLE
# ──────────────────────────────────────────────────────────────────────
Y = df["patents"].to_numpy()


def poisson_loglikelihood(lam: float, Y: np.ndarray) -> float:
    """Log-likelihood of an iid Poisson(lambda) sample, vectorized in lam."""
    if lam <= 0:
        return -np.inf
    return float(-len(Y) * lam + np.log(lam) * Y.sum() - gammaln(Y + 1).sum())


lam_grid = np.linspace(0.5, 8.0, 300)
ll_grid = np.array([poisson_loglikelihood(lam, Y) for lam in lam_grid])
sample_mean = float(Y.mean())

result_univariate = optimize.minimize_scalar(
    lambda lam: -poisson_loglikelihood(lam, Y),
    bounds=(0.01, 50),
    method="bounded",
    options={"xatol": 1e-8},
)
numbers["mle_univariate"] = float(result_univariate.x)
numbers["sample_mean"] = sample_mean
numbers["mle_vs_mean_abs_diff"] = abs(numbers["mle_univariate"] - sample_mean)

# Fig 4: log-likelihood curve
fig4 = go.Figure()
fig4.add_trace(
    go.Scatter(
        x=lam_grid,
        y=ll_grid,
        mode="lines",
        line=dict(color=COLOR_CUST, width=2.5),
        name="log-likelihood",
        hovertemplate="λ = %{x:.2f}<br>log L = %{y:.1f}<extra></extra>",
    )
)
fig4.add_vline(
    x=sample_mean,
    line=dict(color=COLOR_NON, dash="dot", width=2),
)
fig4.add_annotation(
    x=sample_mean,
    y=ll_grid.max(),
    text=f"MLE = ȳ = {sample_mean:.4f}",
    showarrow=True,
    arrowhead=2,
    arrowcolor=COLOR_NON,
    ax=70,
    ay=-40,
    font=dict(color=COLOR_NON, size=12),
)
fig4.update_xaxes(title_text="λ (rate parameter)")
fig4.update_yaxes(title_text="log-likelihood")
fig4 = apply_theme(fig4, height=400)
save_fig(fig4, "fig4-loglik-curve")

# ──────────────────────────────────────────────────────────────────────
# Section 4: Poisson regression by hand + GLM cross-check
# ──────────────────────────────────────────────────────────────────────
# Design matrix: intercept + age + age² + region dummies (drop Midwest) + iscustomer
region_dummies = pd.get_dummies(df["region"], drop_first=False, dtype=float).drop(columns=["Midwest"])
X_df = pd.concat(
    [
        pd.Series(1.0, index=df.index, name="const"),
        df[["age", "age2"]],
        region_dummies,
        df[["iscustomer"]].astype(float),
    ],
    axis=1,
)
X = X_df.to_numpy(dtype=float)
var_names = list(X_df.columns)


def poisson_regression_neg_loglik(beta: np.ndarray, Y: np.ndarray, X: np.ndarray) -> float:
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        eta = np.clip(X @ beta, -30.0, 30.0)
        lam = np.exp(eta)
        return float(-(Y * eta - lam - gammaln(Y + 1)).sum())


def poisson_regression_neg_grad(beta: np.ndarray, Y: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Analytical gradient: ∂(−log L)/∂β = −X' (Y − λ) with λ = exp(Xβ)."""
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        eta = np.clip(X @ beta, -30.0, 30.0)
        lam = np.exp(eta)
        return -X.T @ (Y - lam)


# Smart starting point: intercept at log(sample mean), other coefs at zero.
# Box constraints prevent the optimizer from exploring crazy regions of β space
# where X @ β overflows (age² ranges up to ~2500, so even β = 10 sends λ to inf).
beta0 = np.zeros(X.shape[1])
beta0[var_names.index("const")] = np.log(Y.mean())
bounds = [(-10.0, 10.0)] * X.shape[1]

opt = optimize.minimize(
    poisson_regression_neg_loglik,
    beta0,
    jac=poisson_regression_neg_grad,
    args=(Y, X),
    method="L-BFGS-B",
    bounds=bounds,
    options={"gtol": 1e-10, "maxiter": 2000, "ftol": 1e-12},
)
assert opt.success, f"L-BFGS-B did not converge: {opt.message}"
beta_hat = opt.x

# Standard errors from the analytical observed-information matrix
# (more accurate than BFGS's quasi-Newton hess_inv approximation):
#   H = X' diag(λ) X     →     Var(β̂) = H⁻¹.
with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
    lam_hat = np.exp(X @ beta_hat)
    info_matrix = X.T @ (X * lam_hat[:, None])
cov_hat = np.linalg.inv(info_matrix)
se_hat = np.sqrt(np.diag(cov_hat))

# Cross-check with statsmodels GLM
glm = sm.GLM(Y.astype(float), X, family=sm.families.Poisson()).fit()
glm_coef = np.asarray(glm.params)
glm_se = np.asarray(glm.bse)

coef_table = pd.DataFrame(
    {
        "variable": var_names,
        "mle_coef": beta_hat,
        "mle_se": se_hat,
        "glm_coef": glm_coef,
        "glm_se": glm_se,
    }
)
coef_table.to_csv(ASSETS / "coef-table.csv", index=False)

numbers["coef_table"] = coef_table.to_dict(orient="records")
numbers["mle_glm_max_coef_diff"] = float(np.abs(beta_hat - glm_coef).max())
numbers["mle_glm_max_se_diff"] = float(np.abs(se_hat - glm_se).max())
numbers["beta_customer"] = float(glm_coef[var_names.index("iscustomer")])
numbers["se_customer"] = float(glm_se[var_names.index("iscustomer")])
numbers["exp_beta_customer"] = float(np.exp(numbers["beta_customer"]))
numbers["loglik_full_model"] = float(glm.llf)

# Fig 5: coefficient forest plot (95% CI bars)
order = ["iscustomer", "age", "age2", "Northeast", "Northwest", "South", "Southwest", "const"]
pretty = {
    "iscustomer": "Is customer",
    "age": "Age",
    "age2": "Age²",
    "Northeast": "Northeast (vs Midwest)",
    "Northwest": "Northwest (vs Midwest)",
    "South": "South (vs Midwest)",
    "Southwest": "Southwest (vs Midwest)",
    "const": "Intercept",
}
ci_data = []
for v in order:
    i = var_names.index(v)
    ci_data.append(
        dict(
            variable=pretty[v],
            coef=float(glm_coef[i]),
            ci_low=float(glm_coef[i] - 1.96 * glm_se[i]),
            ci_high=float(glm_coef[i] + 1.96 * glm_se[i]),
            is_customer=(v == "iscustomer"),
        )
    )
fig5 = go.Figure()
for row in ci_data:
    color = COLOR_HIGHLIGHT if row["is_customer"] else COLOR_NEUTRAL
    fig5.add_trace(
        go.Scatter(
            x=[row["ci_low"], row["ci_high"]],
            y=[row["variable"], row["variable"]],
            mode="lines",
            line=dict(color=color, width=3),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig5.add_trace(
        go.Scatter(
            x=[row["coef"]],
            y=[row["variable"]],
            mode="markers",
            marker=dict(color=color, size=11, line=dict(color="#0D0D0C", width=1)),
            name=row["variable"],
            showlegend=False,
            hovertemplate=(
                f"{row['variable']}<br>"
                f"coef = {row['coef']:.4f}<br>"
                f"95% CI: [{row['ci_low']:.4f}, {row['ci_high']:.4f}]<extra></extra>"
            ),
        )
    )
fig5.add_vline(x=0, line=dict(color="rgba(150,150,150,0.5)", dash="dash", width=1))
fig5.update_xaxes(title_text="Coefficient (log scale on patent rate)")
fig5.update_yaxes(title_text="", autorange="reversed")
fig5 = apply_theme(fig5, height=460)
save_fig(fig5, "fig5-coef-forest")

# ──────────────────────────────────────────────────────────────────────
# Section 5: counterfactual ATE
# ──────────────────────────────────────────────────────────────────────
X0 = X_df.copy()
X0["iscustomer"] = 0.0
X1 = X_df.copy()
X1["iscustomer"] = 1.0
with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
    y0 = np.exp(X0.to_numpy(dtype=float) @ glm_coef)
    y1 = np.exp(X1.to_numpy(dtype=float) @ glm_coef)
delta = y1 - y0

numbers["mean_y0"] = float(y0.mean())
numbers["mean_y1"] = float(y1.mean())
numbers["ate"] = float(delta.mean())
numbers["ate_median"] = float(np.median(delta))
numbers["ate_p10"] = float(np.percentile(delta, 10))
numbers["ate_p90"] = float(np.percentile(delta, 90))

# Fig 6: distribution of per-firm counterfactual effects (ŷ1 - ŷ0)
fig6 = go.Figure()
fig6.add_trace(
    go.Histogram(
        x=delta,
        xbins=dict(start=0, end=2.0, size=0.05),
        marker_color=COLOR_CUST,
        opacity=0.9,
        name="Per-firm effect",
        hovertemplate="Effect: %{x:.2f}<br>Firms: %{y}<extra></extra>",
    )
)
fig6.add_vline(
    x=numbers["ate"],
    line=dict(color=COLOR_NON, dash="dot", width=2.5),
)
fig6.add_annotation(
    x=numbers["ate"],
    y=1.02,
    yref="paper",
    text=f"Average treatment effect = +{numbers['ate']:.3f} patents/firm",
    showarrow=False,
    font=dict(color=COLOR_NON, size=12),
    yanchor="bottom",
)
fig6.update_xaxes(title_text="Predicted patents if customer minus predicted if not, per firm")
fig6.update_yaxes(title_text="Number of firms")
fig6 = apply_theme(fig6, height=380)
fig6.update_layout(bargap=0.05)
save_fig(fig6, "fig6-counterfactual")

# ──────────────────────────────────────────────────────────────────────
# Dump every number cited in the prose so they can be cross-checked.
# ──────────────────────────────────────────────────────────────────────
with (ASSETS / "numbers.json").open("w") as f:
    json.dump(numbers, f, indent=2, default=float)

# ──────────────────────────────────────────────────────────────────────
# Console summary so a re-run is auditable.
# ──────────────────────────────────────────────────────────────────────
print("=" * 60)
print("ANCHOR NUMBERS")
print("=" * 60)
print(f"N total / customer / non-customer:  {numbers['n_total']} / {numbers['n_customer']} / {numbers['n_noncustomer']}")
print(f"Mean patents overall:               {numbers['patents_mean']:.4f}")
print(f"  non-customer:                     {numbers['mean_patents_noncustomer']:.4f}")
print(f"  customer:                         {numbers['mean_patents_customer']:.4f}")
print(f"  raw gap:                          {numbers['raw_gap']:.4f}")
print(f"Univariate MLE  vs  sample mean:    {numbers['mle_univariate']:.6f}  vs  {numbers['sample_mean']:.6f}")
print(f"  absolute diff:                    {numbers['mle_vs_mean_abs_diff']:.2e}")
print(f"Max |coef diff| MLE-vs-GLM:         {numbers['mle_glm_max_coef_diff']:.2e}")
print(f"Max |SE   diff| MLE-vs-GLM:         {numbers['mle_glm_max_se_diff']:.2e}")
print(f"β_customer:                         {numbers['beta_customer']:.4f}  (SE {numbers['se_customer']:.4f})")
print(f"exp(β_customer):                    {numbers['exp_beta_customer']:.4f}")
print(f"Counterfactual mean ŷ0 / ŷ1:        {numbers['mean_y0']:.4f} / {numbers['mean_y1']:.4f}")
print(f"Average treatment effect:           {numbers['ate']:.4f}  patents/firm over 5 years")
print(f"ATE p10 / median / p90:             {numbers['ate_p10']:.3f} / {numbers['ate_median']:.3f} / {numbers['ate_p90']:.3f}")
print("=" * 60)
print(f"Wrote 6 figure snippets + coef-table.csv + numbers.json to {ASSETS}")
