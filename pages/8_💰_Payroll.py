import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth_utils import require_login, check_role, render_sidebar
from services.payroll_service import PayrollService
import io

# Page Config
st.set_page_config(page_title="Payroll", page_icon="💰", layout="wide")
require_login()
render_sidebar()
check_role(['Admin', 'Manager'])

st.title("💰 Payroll Estimator")

payroll_service = PayrollService()

st.subheader("Payroll Period")
# Date selection moved to main page
current_year = datetime.now().year
years = list(range(current_year - 2, current_year + 3))

months = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}

c1, c2, c3 = st.columns([1, 1, 2])
with c1:
    selected_year = st.selectbox("Year", years, index=2)
with c2:
    selected_month_idx = st.selectbox("Month", options=list(months.keys()), format_func=lambda x: months[x], index=datetime.now().month - 1)
with c3:
    st.write("") # Spacer
    st.write("") 
    generate_btn = st.button("Generate Payroll", type="primary", use_container_width=True)

if generate_btn:
    with st.spinner("Calculating..."):
        data = payroll_service.generate_payroll(selected_year, selected_month_idx)
        st.session_state.payroll_data = data
        st.session_state.payroll_generated = True

if 'payroll_generated' in st.session_state and st.session_state.payroll_generated:
    data = st.session_state.payroll_data
    
    if data:
        df = pd.DataFrame(data)
        
        # Summary Metrics
        total_payout = df['Net Pay'].sum()
        total_hours = df['Regular Hours'].sum() + df['Overtime Hours'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Net Payout", f"${total_payout:,.2f}")
        c2.metric("Total Hours Worked", f"{total_hours:,.1f}")
        c3.metric("Employees Processed", len(df))
        
        st.dataframe(df, use_container_width=True)
        
        # Export
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Payroll')
            
        st.download_button(
            label="📥 Download Payroll Summary (Excel)",
            data=excel_buffer.getvalue(),
            file_name=f"Payroll_{months[selected_month_idx]}_{selected_year}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # --- Budget Analysis ---
        st.divider()
        st.subheader("💼 Department Budget Analysis")
        
        # Calculate actual spend per department
        # df has 'Department' and 'Gross Pay' (cost to company is closer to Gross, or Gross + Tax? Usually Gross is cost)
        dept_spend = df.groupby('Department')['Gross Pay'].sum().reset_index()
        dept_spend.columns = ['name', 'actual_spend']
        
        # Get Budgets
        from database.db_manager import DBManager
        db = DBManager()
        depts_db = db.execute_query("SELECT name, budget FROM departments", fetch_all=True)
        if depts_db:
            df_budgets = pd.DataFrame(depts_db)
            df_budgets['budget'] = df_budgets['budget'].fillna(0)
            
            # Merge
            merged = pd.merge(df_budgets, dept_spend, on='name', how='left').fillna(0)
            merged['status'] = merged.apply(lambda x: 'Over Budget 🚨' if x['actual_spend'] > x['budget'] else 'Within Budget ✅', axis=1)
            merged['utilization'] = (merged['actual_spend'] / merged['budget'] * 100).fillna(0)
            
            # Display
            c1, c2 = st.columns([2, 1])
            with c1:
                st.dataframe(merged[['name', 'budget', 'actual_spend', 'status', 'utilization']], use_container_width=True)
            with c2:
                 # Simple Bar comparison
                 import plotly.graph_objects as go
                 fig = go.Figure(data=[
                     go.Bar(name='Budget', x=merged['name'], y=merged['budget']),
                     go.Bar(name='Actual', x=merged['name'], y=merged['actual_spend'])
                 ])
                 fig.update_layout(barmode='group', title="Budget vs Actual")
                 st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No department budgets set.")

        st.divider()
        
        st.divider()
        st.subheader("📄 Individual Payslips")
        
        # Display as a list of actions
        for i, row in df.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{row['Name']}** - {row['Department']}")
            with col2:
                # Generate PDF (Create new instance per doc to avoid 'closed document' error)
                from services.pdf_service import PDFService
                pdf = PDFService() # Fresh instance
                
                pdf_bytes = pdf.generate_payslip(
                    None, 
                    row.to_dict(),
                    f"{months[selected_month_idx]} {selected_year}"
                )
                
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name=f"Payslip_{row['Employee ID']}_{selected_month_idx}_{selected_year}.pdf",
                    mime="application/pdf",
                    key=f"btn_pdf_{row['Employee ID']}"
                )
            st.divider()
    else:
        st.info("No active employees found.")
