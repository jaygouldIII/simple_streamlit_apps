import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="YourForeverCost", page_icon="🏠", layout="wide")

# ---------------------------------------------------------------------------
# Custom CSS for fun vibes
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .main-header h1 {
        font-size: 3rem;
        background: linear-gradient(90deg, #ff6b6b, #ffa36b, #ffd56b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header p {
        font-size: 1.2rem;
        color: #888;
    }
    .big-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff6b6b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>YourForeverCost</h1>
        <p>Because nothing says "forever" like a 30-year mortgage. Let's see the damage.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar – Mortgage inputs
# ---------------------------------------------------------------------------
st.sidebar.header("Your Mortgage Details")

home_price = st.sidebar.number_input(
    "Home Price ($)", min_value=10_000, max_value=10_000_000, value=350_000, step=5_000
)
down_payment_pct = st.sidebar.slider(
    "Down Payment (%)", min_value=0, max_value=100, value=20
)
loan_term = st.sidebar.selectbox("Loan Term (years)", [10, 15, 20, 25, 30], index=4)
interest_rate = st.sidebar.slider(
    "Interest Rate (%)", min_value=0.5, max_value=12.0, value=6.5, step=0.1
)
property_tax_rate = st.sidebar.slider(
    "Annual Property Tax (%)", min_value=0.0, max_value=5.0, value=1.2, step=0.1
)
home_insurance = st.sidebar.number_input(
    "Annual Home Insurance ($)", min_value=0, max_value=20_000, value=1_200, step=100
)

# ---------------------------------------------------------------------------
# Core calculations
# ---------------------------------------------------------------------------
down_payment = home_price * down_payment_pct / 100
loan_amount = home_price - down_payment
monthly_rate = (interest_rate / 100) / 12
n_payments = loan_term * 12

if monthly_rate > 0:
    monthly_mortgage = loan_amount * (
        monthly_rate * (1 + monthly_rate) ** n_payments
    ) / ((1 + monthly_rate) ** n_payments - 1)
else:
    monthly_mortgage = loan_amount / n_payments

monthly_tax = (home_price * property_tax_rate / 100) / 12
monthly_insurance = home_insurance / 12
total_monthly = monthly_mortgage + monthly_tax + monthly_insurance

total_paid = monthly_mortgage * n_payments
total_interest = total_paid - loan_amount
total_forever_cost = total_paid + (monthly_tax + monthly_insurance) * n_payments

# ---------------------------------------------------------------------------
# Key metrics
# ---------------------------------------------------------------------------
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Monthly Payment", f"${total_monthly:,.0f}")
col2.metric("Principal & Interest", f"${monthly_mortgage:,.0f}")
col3.metric("Total Interest Paid", f"${total_interest:,.0f}")
col4.metric(
    "Your Forever Cost",
    f"${total_forever_cost:,.0f}",
    help="Total of all payments over the life of the loan (principal + interest + tax + insurance)",
)

st.caption(
    f"That's **${total_monthly:,.0f}/mo** for **{loan_term} years**. "
    f"You'll pay **${total_interest:,.0f}** just in interest. You're welcome."
)

# ---------------------------------------------------------------------------
# Amortization schedule
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("The Slow Painful Journey (Amortization Schedule)")

balance = loan_amount
schedule_rows = []
cumulative_interest = 0.0
cumulative_principal = 0.0

for month in range(1, n_payments + 1):
    interest_payment = balance * monthly_rate
    principal_payment = monthly_mortgage - interest_payment
    balance -= principal_payment
    if balance < 0:
        balance = 0
    cumulative_interest += interest_payment
    cumulative_principal += principal_payment
    schedule_rows.append(
        {
            "Month": month,
            "Year": (month - 1) // 12 + 1,
            "Payment": monthly_mortgage,
            "Principal": principal_payment,
            "Interest": interest_payment,
            "Balance": balance,
            "Cumulative Interest": cumulative_interest,
            "Cumulative Principal": cumulative_principal,
        }
    )

df = pd.DataFrame(schedule_rows)

# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### Where Your Money Goes Each Month")
    # Aggregate by year for cleaner chart
    yearly = df.groupby("Year").agg({"Principal": "sum", "Interest": "sum"}).reset_index()
    fig1 = go.Figure()
    fig1.add_trace(
        go.Bar(x=yearly["Year"], y=yearly["Principal"], name="Principal", marker_color="#4ecdc4")
    )
    fig1.add_trace(
        go.Bar(x=yearly["Year"], y=yearly["Interest"], name="Interest", marker_color="#ff6b6b")
    )
    fig1.update_layout(
        barmode="stack",
        xaxis_title="Year",
        yaxis_title="Amount ($)",
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    st.markdown("#### Remaining Balance Over Time")
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=df["Month"],
            y=df["Balance"],
            mode="lines",
            fill="tozeroy",
            line=dict(color="#ffa36b", width=2),
            fillcolor="rgba(255,163,107,0.3)",
        )
    )
    fig2.update_layout(
        xaxis_title="Month",
        yaxis_title="Balance ($)",
        template="plotly_white",
        height=400,
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------------------------------------------------------
# Cost breakdown pie
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("The Full Picture")
pie_col1, pie_col2 = st.columns([1, 2])

with pie_col1:
    fig3 = go.Figure(
        go.Pie(
            labels=["Principal", "Interest", "Property Tax", "Insurance"],
            values=[
                loan_amount,
                total_interest,
                monthly_tax * n_payments,
                monthly_insurance * n_payments,
            ],
            hole=0.45,
            marker=dict(colors=["#4ecdc4", "#ff6b6b", "#ffd56b", "#a36bff"]),
        )
    )
    fig3.update_layout(height=350, margin=dict(t=20, b=20))
    st.plotly_chart(fig3, use_container_width=True)

with pie_col2:
    st.markdown("#### Cost Breakdown Over Loan Life")
    st.markdown(
        f"""
        | Category | Total | Monthly |
        |----------|------:|--------:|
        | **Principal** | ${loan_amount:,.0f} | ${loan_amount / n_payments:,.0f} |
        | **Interest** | ${total_interest:,.0f} | ${total_interest / n_payments:,.0f} |
        | **Property Tax** | ${monthly_tax * n_payments:,.0f} | ${monthly_tax:,.0f} |
        | **Insurance** | ${monthly_insurance * n_payments:,.0f} | ${monthly_insurance:,.0f} |
        | **TOTAL** | **${total_forever_cost:,.0f}** | **${total_monthly:,.0f}** |
        """
    )

# ---------------------------------------------------------------------------
# Lender comparison
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Find Your Lender (or least painful option)")

st.markdown(
    "Here's how different rates stack up. Because that 0.25% difference? "
    "It's a used car over 30 years."
)

rate_comparison = []
for delta in [-1.0, -0.5, -0.25, 0, 0.25, 0.5, 1.0]:
    comp_rate = interest_rate + delta
    if comp_rate <= 0:
        continue
    comp_monthly_rate = (comp_rate / 100) / 12
    comp_payment = loan_amount * (
        comp_monthly_rate * (1 + comp_monthly_rate) ** n_payments
    ) / ((1 + comp_monthly_rate) ** n_payments - 1)
    comp_total_interest = comp_payment * n_payments - loan_amount
    rate_comparison.append(
        {
            "Rate (%)": f"{comp_rate:.2f}%",
            "Monthly P&I": f"${comp_payment:,.0f}",
            "Total Interest": f"${comp_total_interest:,.0f}",
            "vs. Yours": f"${comp_total_interest - total_interest:+,.0f}"
            if delta != 0
            else "** Your Rate **",
        }
    )

st.dataframe(
    pd.DataFrame(rate_comparison),
    use_container_width=True,
    hide_index=True,
)

# ---------------------------------------------------------------------------
# Lender directory
# ---------------------------------------------------------------------------
st.markdown("#### Popular Mortgage Lenders to Compare")
st.markdown(
    """
    | Lender | Known For | Best If You... |
    |--------|-----------|----------------|
    | **Rocket Mortgage** | Speed & tech | Want a fully online experience |
    | **Chase** | Big bank reliability | Already bank with Chase |
    | **Wells Fargo** | Wide branch network | Prefer in-person service |
    | **Better.com** | Low fees | Want to minimize closing costs |
    | **loanDepot** | Variety of products | Have a unique financial situation |
    | **Local Credit Union** | Member rates | Want the best rates possible |

    *Always shop at least 3 lenders. Your future self (still paying this mortgage) will thank you.*
    """
)

# ---------------------------------------------------------------------------
# Fun footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; padding:2rem 0;'>"
    "<b>YourForeverCost</b> &mdash; Making you question homeownership since 2026.<br>"
    "Built with Streamlit. Tears not included."
    "</div>",
    unsafe_allow_html=True,
)
