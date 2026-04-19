import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import datetime
import hashlib

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Sales Intelligence Hub",
    page_icon="📊",
    layout="wide"
)

# ============================================
# DATABASE CONNECTION
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Shalu0.34',  
    'database': 'sales_intelligence_hub'
}

def get_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# ============================================
# AUTHENTICATION
# ============================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(username, password):
    conn = get_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        hashed_pwd = hash_password(password)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND password = %s",
            (username, hashed_pwd)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    return None

# ============================================
# DATABASE OPERATIONS
# ============================================
def get_branches():
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM branches", conn)
        conn.close()
        return df
    return pd.DataFrame()

def get_sales(branch_id=None):
    conn = get_connection()
    if conn:
        query = """
            SELECT cs.sale_id, b.branch_name, cs.date, cs.name, 
                   cs.mobile_number, cs.product_name, cs.gross_sales,
                   cs.received_amount, cs.pending_amount, cs.status
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
        """
        if branch_id:
            query += f" WHERE cs.branch_id = {branch_id}"
        query += " ORDER BY cs.date DESC"
        
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    return pd.DataFrame()

def add_sale(branch_id, date, name, mobile, product, gross_sales):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT IFNULL(MAX(sale_id), 0) + 1 FROM customer_sales")
        new_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO customer_sales (sale_id, branch_id, date, name, mobile_number, product_name, gross_sales, received_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, 'Open')
        """, (new_id, branch_id, date, name, mobile, product, gross_sales))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    return False

def add_payment(sale_id, payment_date, amount, method):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT IFNULL(MAX(payment_id), 0) + 1 FROM payment_splits")
        new_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT INTO payment_splits (payment_id, sale_id, payment_date, amount_paid, payment_method)
            VALUES (%s, %s, %s, %s, %s)
        """, (new_id, sale_id, payment_date, amount, method))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    return False

def run_query(query):
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except:
            conn.close()
            return None
    return None

# ============================================
# LOGIN PAGE
# ============================================
def login_page():
    st.markdown("<h1 style='text-align: center;'>📊 Sales Intelligence Hub</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Login to Access Dashboard</h3>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)
        
        if submitted:
            user = authenticate_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.session_state.role = user['role']
                st.session_state.branch_id = user['branch_id']
                st.rerun()
            else:
                st.error("Invalid username or password!")

# ============================================
# MAIN DASHBOARD
# ============================================
def show_dashboard():
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, {st.session_state.user['username']}")
        st.markdown(f"**Role:** {st.session_state.role}")
        st.markdown("---")
        
        page = st.radio("Navigation", [
            "🏠 Dashboard", "➕ Add Sale", "💰 Add Payment", "📋 Sales Report", "🔍 SQL Queries"
        ])
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    
    if page == "🏠 Dashboard":
        show_overview()
    elif page == "➕ Add Sale":
        show_add_sale()
    elif page == "💰 Add Payment":
        show_add_payment()
    elif page == "📋 Sales Report":
        show_sales_report()
    elif page == "🔍 SQL Queries":
        show_sql_queries()

def show_overview():
    st.title("🏠 Dashboard Overview")
    
    if st.session_state.role == "Super Admin":
        sales_df = get_sales()
    else:
        sales_df = get_sales(st.session_state.branch_id)
    
    if not sales_df.empty:
        total_gross = sales_df['gross_sales'].sum()
        total_received = sales_df['received_amount'].sum()
        total_pending = sales_df['pending_amount'].sum()
        collection_rate = (total_received / total_gross * 100) if total_gross > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Total Gross Sales", f"₹{total_gross:,.2f}")
        col2.metric("✅ Total Received", f"₹{total_received:,.2f}")
        col3.metric("⏳ Total Pending", f"₹{total_pending:,.2f}")
        col4.metric("📊 Collection Rate", f"{collection_rate:.1f}%")
        
        # Show ALL sales (not just recent)
        st.subheader(f"📅 All Sales Records ({len(sales_df)} records)")
        st.dataframe(sales_df, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            status_counts = sales_df['status'].value_counts()
            st.bar_chart(status_counts)
        with col2:
            product_sales = sales_df.groupby('product_name')['gross_sales'].sum()
            st.bar_chart(product_sales)
    else:
        st.info("No sales data available")

def show_add_sale():
    st.title("➕ Add New Sale")
    
    branches_df = get_branches()
    if st.session_state.role == "Admin":
        branches_df = branches_df[branches_df['branch_id'] == st.session_state.branch_id]
    
    with st.form("add_sale_form"):
        col1, col2 = st.columns(2)
        with col1:
            branch_id = st.selectbox("Branch", branches_df['branch_id'].tolist(), 
                                    format_func=lambda x: branches_df[branches_df['branch_id']==x]['branch_name'].iloc[0])
            date = st.date_input("Sale Date", datetime.now())
            name = st.text_input("Customer Name")
        with col2:
            mobile = st.text_input("Mobile Number")
            product = st.selectbox("Product", ["DS", "DA", "BA", "FSD", "AI", "ML", "BI", "SQL"])
            gross_sales = st.number_input("Gross Sales (₹)", min_value=0.0, step=1000.0)
        
        if st.form_submit_button("Add Sale", use_container_width=True):
            if add_sale(branch_id, date, name, mobile, product, gross_sales):
                st.success("✅ Sale added successfully!")
                st.rerun()

def show_add_payment():
    st.title("💰 Add Payment to Sale")
    
    if st.session_state.role == "Super Admin":
        sales_df = get_sales()
    else:
        sales_df = get_sales(st.session_state.branch_id)
    
    open_sales = sales_df[sales_df['status'] == 'Open']
    
    if not open_sales.empty:
        with st.form("add_payment_form"):
            sale_options = {row['sale_id']: f"{row['name']} - {row['branch_name']} - Pending: ₹{row['pending_amount']:,.2f}" 
                          for _, row in open_sales.iterrows()}
            sale_id = st.selectbox("Select Sale", list(sale_options.keys()), format_func=lambda x: sale_options[x])
            
            selected = open_sales[open_sales['sale_id'] == sale_id].iloc[0]
            pending_amount = float(selected['pending_amount'])
            
            st.info(f"💰 Gross: ₹{selected['gross_sales']:,.2f} | ✅ Received: ₹{selected['received_amount']:,.2f} | ⏳ Pending: ₹{pending_amount:,.2f}")
            
            col1, col2 = st.columns(2)
            with col1:
                payment_date = st.date_input("Payment Date", datetime.now())
                amount = st.number_input(
                    "Amount Paid (₹)", 
                    min_value=0.0, 
                    step=500.0,
                    help=f"Maximum allowed: ₹{pending_amount:,.2f}"
                )
            with col2:
                method = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])
            
            submitted = st.form_submit_button("Add Payment", use_container_width=True)
            
            if submitted:
                if amount <= 0:
                    st.error("❌ Please enter a valid amount greater than 0!")
                elif amount > pending_amount:
                    st.error(f"❌ Amount cannot exceed pending amount of ₹{pending_amount:,.2f}!")
                else:
                    if add_payment(sale_id, payment_date, amount, method):
                        st.success(f"✅ Payment of ₹{amount:,.2f} added successfully!")
                        st.rerun()
    else:
        st.info("No open sales found")

def show_sales_report():
    st.title("📋 Sales Report")
    
    branches_df = get_branches()
    
    if st.session_state.role == "Super Admin":
        sales_df = get_sales()
        branch_options = ["All"] + branches_df['branch_name'].tolist()
        selected_branch = st.selectbox("Branch", branch_options)
        if selected_branch != "All":
            sales_df = sales_df[sales_df['branch_name'] == selected_branch]
    else:
        sales_df = get_sales(st.session_state.branch_id)
    
    status_filter = st.selectbox("Status", ["All", "Open", "Close"])
    if status_filter != "All":
        sales_df = sales_df[sales_df['status'] == status_filter]
    
    if not sales_df.empty:
        st.dataframe(sales_df, use_container_width=True)
        st.download_button("📥 Download CSV", sales_df.to_csv(index=False), "sales_report.csv", "text/csv")
        
        st.subheader("📊 Report Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sales", len(sales_df))
        col2.metric("Total Revenue", f"₹{sales_df['gross_sales'].sum():,.2f}")
        col3.metric("Total Pending", f"₹{sales_df['pending_amount'].sum():,.2f}")
    else:
        st.info("No sales data available")

def show_sql_queries():
    st.title("🔍 SQL Queries")
    
    # ALL 20 SQL QUERIES
    queries = {
        # Basic Queries (1-5)
        "1. All Customer Sales": "SELECT * FROM customer_sales;",
        "2. All Branches": "SELECT * FROM branches;",
        "3. All Payment Splits": "SELECT * FROM payment_splits;",
        "4. Open Sales": "SELECT * FROM customer_sales WHERE status = 'Open';",
        "5. Chennai Branch Sales": """
            SELECT cs.*, b.branch_name 
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            WHERE b.branch_name = 'Chennai';
        """,
        
        # Aggregation Queries (6-10)
        "6. Total Gross Sales": "SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales;",
        "7. Total Received Amount": "SELECT SUM(received_amount) AS total_received_amount FROM customer_sales;",
        "8. Total Pending Amount": "SELECT SUM(pending_amount) AS total_pending_amount FROM customer_sales;",
        "9. Sales Count Per Branch": """
            SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales
            FROM branches b
            LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
            GROUP BY b.branch_name;
        """,
        "10. Average Gross Sales": "SELECT AVG(gross_sales) AS avg_gross_sales FROM customer_sales;",
        
        # Join-Based Queries (11-15)
        "11. Sales with Branch Name": """
            SELECT cs.sale_id, b.branch_name, cs.date, cs.name, 
                   cs.product_name, cs.gross_sales, cs.status
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            LIMIT 20;
        """,
        "12. Sales with Payment Totals": """
            SELECT cs.sale_id, cs.name, cs.gross_sales, 
                   COALESCE(SUM(ps.amount_paid), 0) AS total_paid
            FROM customer_sales cs
            LEFT JOIN payment_splits ps ON cs.sale_id = ps.sale_id
            GROUP BY cs.sale_id, cs.name, cs.gross_sales
            LIMIT 20;
        """,
        "13. Branch-wise Gross Sales": """
            SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
            FROM branches b
            JOIN customer_sales cs ON b.branch_id = cs.branch_id
            GROUP BY b.branch_name
            ORDER BY total_gross_sales DESC;
        """,
        "14. Sales with Payment Method": """
            SELECT cs.sale_id, cs.name, ps.payment_method, ps.amount_paid
            FROM customer_sales cs
            JOIN payment_splits ps ON cs.sale_id = ps.sale_id
            LIMIT 20;
        """,
        "15. Sales with Branch Admin Name": """
            SELECT cs.sale_id, cs.name, b.branch_name, b.branch_admin_name
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            LIMIT 20;
        """,
        
        # Financial Tracking Queries (16-20)
        "16. Pending Amount > ₹5000": """
            SELECT cs.sale_id, cs.name, cs.gross_sales, cs.pending_amount, b.branch_name
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            WHERE cs.pending_amount > 5000
            LIMIT 20;
        """,
        "17. Top 3 Highest Sales": """
            SELECT cs.sale_id, cs.name, cs.gross_sales, b.branch_name
            FROM customer_sales cs
            JOIN branches b ON cs.branch_id = b.branch_id
            ORDER BY cs.gross_sales DESC
            LIMIT 3;
        """,
        "18. Branch with Highest Sales": """
            SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross_sales
            FROM branches b
            JOIN customer_sales cs ON b.branch_id = b.branch_id
            GROUP BY b.branch_name
            ORDER BY total_gross_sales DESC
            LIMIT 1;
        """,
        "19. Monthly Sales Summary": """
            SELECT DATE_FORMAT(date, '%Y-%M') as month, 
                   COUNT(*) as total_sales,
                   SUM(gross_sales) as total_revenue
            FROM customer_sales
            GROUP BY DATE_FORMAT(date, '%Y-%M')
            ORDER BY MIN(date) DESC;
        """,
        "20. Payment Method Collection": """
            SELECT payment_method, SUM(amount_paid) as total_collection
            FROM payment_splits
            GROUP BY payment_method
            ORDER BY total_collection DESC;
        """
    }
    
    selected = st.selectbox("Select Query", list(queries.keys()))
    query = queries[selected]
    
    st.code(query, language="sql")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        execute_btn = st.button("▶️ Execute Query", type="primary", use_container_width=True)
    
    if execute_btn:
        with st.spinner("Executing query..."):
            result = run_query(query)
            if result is not None and not result.empty:
                st.subheader("📊 Results:")
                st.dataframe(result, use_container_width=True)
                
                # Download button
                csv = result.to_csv(index=False)
                st.download_button(
                    "📥 Download Results as CSV",
                    csv,
                    "query_results.csv",
                    "text/csv"
                )
            elif result is not None:
                st.info("Query executed successfully but returned no data.")
            else:
                st.error("Error executing query.")

# ============================================
# MAIN APP
# ============================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_page()
else:
    show_dashboard()