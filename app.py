import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
import json
import uuid
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
if not API_URL.startswith("http"):
    API_URL = f"https://{API_URL}"

st.set_page_config(page_title="BI Assistant", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<div class="custom-query-popover">
    <div class="query-icon" title="How to ask questions">❔</div>
    <div class="query-tooltip">
        <strong>How this works</strong><br/><br/>
        You can ask questions like:<br/>
        &bull; <i>Who is JAMES?</i><br/>
        &bull; <i>What's the total Revenue?</i><br/>
        &bull; <i>Number of customers?</i>
    </div>
</div>
""", unsafe_allow_html=True)


import streamlit.components.v1 as components
components.html(
    """
    <script src="https://unpkg.com/lenis@1.1.18/dist/lenis.min.js"></script>
    <script>
        const doc = window.parent.document;
        const win = window.parent;
        
        // Clean up previous observer if it exists to prevent duplicate/dead listeners
        if (win.customTooltipObserver) {
            win.customTooltipObserver.disconnect();
        }
        // Clean up previous interval if it exists
        if (win.customSidebarInterval) {
            clearInterval(win.customSidebarInterval);
        }

        // Start new observer for hiding Streamlit tooltips
        win.customTooltipObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.querySelector) {
                        const tooltip = node.matches('[data-testid="stTooltipContent"]') ? node : node.querySelector('[data-testid="stTooltipContent"]');
                        if (tooltip && tooltip.textContent.toLowerCase().includes('sidebar')) {
                            let wrapper = tooltip.closest('.stTooltip');
                            if (wrapper) wrapper.style.display = 'none';
                            tooltip.style.display = 'none';
                        }
                    }
                });
            });
        });
        win.customTooltipObserver.observe(doc.body, { childList: true, subtree: true });

        // Start new interval for sidebar icon replacement
        function replaceSidebarIcons() {
            const buttons = doc.querySelectorAll('button');
            buttons.forEach(btn => {
                const text = btn.textContent.toLowerCase();
                
                // Match the button that OPENS the sidebar
                if (text.includes('chevron_right') || text.includes('double_arrow_right') || text.includes('keyboard_double_arrow_right') || text === 'menu') {
                    if (!btn.classList.contains('custom-sidebar-open-btn')) {
                        if (btn.hasAttribute('title')) btn.removeAttribute('title');
                        btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>`;
                        btn.classList.add('custom-sidebar-open-btn');
                    }
                }
                
                // Match the button that CLOSES the sidebar
                if (text.includes('close') || text.includes('chevron_left') || text.includes('arrow_left') || text.includes('double_arrow_left') || text.includes('keyboard_double_arrow_left')) {
                    if (!btn.classList.contains('custom-sidebar-close-btn') && (btn.closest('[data-testid="stSidebar"]') || btn.closest('[data-testid="stSidebarHeader"]') || btn.closest('header'))) {
                        if (btn.hasAttribute('title')) btn.removeAttribute('title');
                        btn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>`;
                        btn.classList.add('custom-sidebar-close-btn');
                    }
                }
            });
        }
        win.customSidebarInterval = setInterval(replaceSidebarIcons, 100);
        replaceSidebarIcons(); // Run once immediately

        // Lenis Smooth Scroll Initialization (once per parent lifecycle)
        if (!win.lenisInitialized) {
            const lenis = new Lenis({
                wrapper: win,
                content: doc.body,
                duration: 1.2,
                easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), 
                smooth: true,
                smoothTouch: false,
            });
            
            function raf(time) {
                lenis.raf(time);
                win.requestAnimationFrame(raf);
            }
            
            win.requestAnimationFrame(raf);
            win.lenisInitialized = true;
        }
    </script>
    """,
    height=0,
)

@st.cache_data(ttl=60)
def fetch_data(endpoint, params=None):
    with st.spinner("Fetching data..."):
        try:
            response = requests.get(f"{API_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Error fetching data from backend: {e}")
            return None

def apply_plotly_styling(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        colorway=["#f97316", "#3b82f6", "#10b981", "#8b5cf6"],
        font=dict(family="Inter, sans-serif", color="#0f172a"),
        title=dict(x=0.5, font=dict(size=18, color="#0f172a")), # Centered and bold title
        margin=dict(l=40, r=40, t=60, b=40), # Generous margins
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            font_color="#0f172a",
            bordercolor="rgba(0, 0, 0, 0.1)"
        ),
        modebar=dict(
            bgcolor='rgba(255, 255, 255, 0.7)',
            color='#334155',
            activecolor='#3b82f6'
        )
    )
    # Remove redundant axis titles (e.g. 'product_name') as they are obvious from chart title, and enable automargin
    fig.update_xaxes(title_text="", showgrid=False, gridcolor='rgba(0,0,0,0.05)', zerolinecolor='rgba(0,0,0,0.05)', tickfont=dict(color="#0f172a"), automargin=True)
    fig.update_yaxes(title_text="", showgrid=True, gridcolor='rgba(0,0,0,0.05)', zerolinecolor='rgba(0,0,0,0.05)', tickfont=dict(color="#0f172a"), automargin=True)
    return fig

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    CHATS_FILE = "chat_history.json"
    def load_chats():
        if os.path.exists(CHATS_FILE):
            try:
                with open(CHATS_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_chats(chats):
        with open(CHATS_FILE, "w") as f:
            json.dump(chats, f)
            
    chats_db = load_chats()

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    if "page" not in st.session_state:
        st.session_state.page = "AI Chat"
        
    page = st.session_state.page

    with st.sidebar:
        if st.button("AI Chat", use_container_width=True, key="nav_ai_chat"):
            st.session_state.page = "AI Chat"
            st.rerun()
            
        if page == "AI Chat":
            spacer, content = st.columns([0.15, 0.85])
            with content:
                if st.button("✎ New chat", use_container_width=True, key="new_chat_btn"):
                    st.session_state.current_chat_id = None
                    st.rerun()
                
                st.markdown("<div style='margin-top: 15px; margin-bottom: 5px; color: #9b9b9b; font-size: 13px; font-weight: 600;'>Recents</div>", unsafe_allow_html=True)
                for chat_id, chat_data in reversed(list(chats_db.items())):
                    title = chat_data.get("title", "New Conversation")
                    if st.button(title, key=chat_id, use_container_width=True):
                        st.session_state.current_chat_id = chat_id
                        st.rerun()

        if st.button("Overview", use_container_width=True, key="nav_overview"):
            st.session_state.page = "Overview"
            st.rerun()
            
        if st.button("Sales Analysis", use_container_width=True, key="nav_sales_analysis"):
            st.session_state.page = "Sales Analysis"
            st.rerun()
            
        if st.button("Customers", use_container_width=True, key="nav_customers"):
            st.session_state.page = "Customers"
            st.rerun()


if page == "Overview":
    col_title, col_btn = st.columns([0.8, 0.2])
    with col_title:
        st.title("Business Overview")
    with col_btn:
        st.write("") # spacer
        if st.button("Generate PDF Report", use_container_width=True):
            with st.status("Generating Report..."):
                try:
                    resp = requests.get(f"{API_URL}/report/generate")
                    if resp.status_code == 200:
                        st.download_button(
                            label="Download PDF",
                            data=resp.content,
                            file_name="bi_report.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("Failed to generate report.")
                except Exception as e:
                    st.error(f"Error: {e}")
    summary = fetch_data("/sales/summary")
    if summary:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Revenue", f"${float(summary['total_revenue']):,.2f}", help="Total revenue generated from all sales orders.")
        col2.metric("Total Orders", summary['total_orders'], help="Total number of sales orders placed.")
        col3.metric("Total Customers", summary['total_customers'], help="Total number of unique customers who have placed an order.")
        col4.metric("Best Product", summary['best_selling_product'], help="The product with the highest total quantity sold.")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    by_product = fetch_data("/sales/by-product")
    if by_product:
        df_prod = pd.DataFrame(by_product)
        fig_prod = px.bar(df_prod, x="product_name", y="revenue", title="Revenue by Product")
        fig_prod = apply_plotly_styling(fig_prod)
        col1.plotly_chart(fig_prod, use_container_width=True, theme=None)
        
    by_month = fetch_data("/sales/by-month")
    if by_month:
        df_month = pd.DataFrame(by_month)
        fig_month = px.line(df_month, x="month", y="revenue", title="Monthly Sales")
        fig_month = apply_plotly_styling(fig_month)
        col2.plotly_chart(fig_month, use_container_width=True, theme=None)

elif page == "Sales Analysis":
    st.title("Sales Analysis")
    
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date", value=pd.to_datetime("2023-01-01"))
    end_date = col2.date_input("End Date", value=pd.to_datetime("2024-12-31"))
    
    params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
    
    col_chart1, col_chart2 = st.columns(2)
    
    by_region = fetch_data("/sales/by-region", params)
    if by_region:
        df_region = pd.DataFrame(by_region)
        fig_region = px.bar(df_region, x="region", y="revenue", title="Revenue by Region")
        fig_region = apply_plotly_styling(fig_region)
        col_chart1.plotly_chart(fig_region, use_container_width=True, theme=None)
        
    by_product = fetch_data("/sales/by-product", params)
    if by_product:
        df_prod = pd.DataFrame(by_product).head(10)
        df_prod = df_prod.sort_values(by="revenue", ascending=True)
        fig_top_prod = px.bar(df_prod, x="revenue", y="product_name", orientation='h', title="Top 10 Products by Revenue")
        fig_top_prod = apply_plotly_styling(fig_top_prod)
        col_chart2.plotly_chart(fig_top_prod, use_container_width=True, theme=None)

elif page == "Customers":
    st.title("Customers")
    
    col1, col2 = st.columns(2)
    
    customers = fetch_data("/customers")
    df_cust = pd.DataFrame(customers) if customers else pd.DataFrame()
    
    search_term = st.text_input("Search Customers by Name or Country")
    
    if not df_cust.empty:
        if search_term:
            search_term = search_term.lower()
            df_cust = df_cust[
                df_cust['first_name'].str.lower().str.contains(search_term) |
                df_cust['last_name'].str.lower().str.contains(search_term) |
                df_cust['country'].str.lower().str.contains(search_term)
            ]
            
        col1.subheader("Customer Directory")
        col1.dataframe(df_cust, use_container_width=True)
        
        df_country = df_cust.groupby("country").size().reset_index(name="count")
        fig_country = px.pie(df_country, values="count", names="country", title="Customers by Country")
        fig_country = apply_plotly_styling(fig_country)
        col2.plotly_chart(fig_country, use_container_width=True, theme=None)

elif page == "AI Chat":
    # 1. Inject Dark Mode Scoped CSS
    st.markdown("""
    <style>
    /* Aggressive overrides for Dark Mode strictly on this page */
    .stApp {
        background: #0f111a !important;
        background-color: #0f111a !important;
    }
    
    /* Top Header override */
    [data-testid="stHeader"], .stHeader, header {
        background: #0f111a !important;
        background-color: #0f111a !important;
    }
    
    /* Bottom Chat Area override */
    [data-testid="stBottom"], .stChatInputContainer, [data-testid="stBottom"] > div {
        background: #0f111a !important;
        background-color: #0f111a !important;
        background-image: none !important;
    }
    
    /* Override global font colors */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp span, .stApp div, .stApp label, .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Chat Input Styling */
    .stChatInputContainer > div {
        background: #1a1d27 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
    }
    .stChatInputContainer input, .stChatInputContainer textarea {
        color: #e2e8f0 !important;
    }
    

    /* Hide chat avatars completely and clear their grid spaces */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="stChatMessageAvatar"],
    .stChatMessageAvatar,
    [data-testid="chatAvatarIcon-user"],
    [data-testid="chatAvatarIcon-assistant"],
    div[data-testid="stChatMessage"] > div:first-child:not([data-testid="stChatMessageContent"]) {
        display: none !important;
    }

    /* User Message Bubble (Right-aligned, auto-expanding width) */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        display: block !important;
        background-color: #2f2f2f !important;
        color: #f3f4f6 !important;
        border-radius: 20px !important;
        padding: 8px 18px !important;
        width: fit-content !important;
        max-width: 70% !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        margin-bottom: 1.5rem !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Clear inner content margins and background for User */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"],
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        color: #f3f4f6 !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* Assistant Message Wrapper (Left-aligned, transparent) */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]),
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        display: block !important;
        background-color: transparent !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-left: 0 !important;
        margin-right: auto !important;
        margin-bottom: 1.5rem !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* Clear inner content margins and background for Assistant */
    div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"],
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
        background-color: transparent !important;
        color: #e2e8f0 !important;
        padding: 0 !important;
        margin: 0 !important;
        width: 100% !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Expander Chevron Custom Fix (Aggressively hide any icon/text formats inside summary) */
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpander"] summary svg,
    [data-testid="stExpander"] summary [data-testid="stIconMaterial"],
    [data-testid="stExpander"] summary span.material-symbols-rounded,
    [data-testid="stExpander"] summary span.material-icons {
        display: none !important;
    }
    
    [data-testid="stExpander"] summary::before {
        content: "▶  " !important;
        font-size: 11px !important;
        color: #94a3b8 !important;
        margin-right: 8px !important;
        display: inline-block !important;
        transition: transform 0.2s ease !important;
    }
    [data-testid="stExpander"] details[open] summary::before {
        content: "▼  " !important;
    }
    
    /* Glowing Orb Element */
    .ai-orb {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, #e8d0e8, #9da2d8, #4e5bc5);
        box-shadow: 0 0 50px rgba(157, 162, 216, 0.4), inset -15px -15px 30px rgba(0,0,0,0.5);
        margin: 60px auto 30px auto;
        animation: float 6s ease-in-out infinite;
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
        100% { transform: translateY(0px); }
    }
    
    /* Greeting Text */
    .ai-greeting {
        text-align: center;
        font-size: 32px;
        font-weight: 400;
        letter-spacing: -0.5px;
        margin-bottom: 60px;
        color: #ffffff;
    }
    
    /* Custom Action Cards container */
    .action-card-container {
        display: flex;
        gap: 15px;
        justify-content: center;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }
    .action-card {
        background: #1a1d27;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px;
        flex: 1;
        min-width: 200px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .action-card:hover {
        background: #232736;
        border-color: rgba(255,255,255,0.1);
        transform: translateY(-2px);
    }
    .action-card h4 {
        margin-top: 0;
        margin-bottom: 8px;
        font-size: 16px;
        font-weight: 500;
        color: #ffffff !important;
    }
    .action-card p {
        margin: 0;
        font-size: 13px;
        color: #94a3b8 !important;
        line-height: 1.4;
    }
    
    /* Darken Nav Pill for this page */
    .stRadio > div[role="radiogroup"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    

    if st.session_state.current_chat_id and st.session_state.current_chat_id in chats_db:
        curr_chat = chats_db[st.session_state.current_chat_id]
        api_history = curr_chat.get("api_history", [])
        ui_history = curr_chat.get("ui_history", [])
    else:
        api_history = []
        ui_history = []

    # Center the chat content
    colA, colB, colC = st.columns([1, 8, 1])
    
    with colB:
        if not ui_history:
            # Empty State
            st.markdown('<div class="ai-orb"></div>', unsafe_allow_html=True)
            st.markdown('<div class="ai-greeting">Hi! I\'m your Data Assistant.<br>What would you like to analyze today?</div>', unsafe_allow_html=True)
        else:
            for msg in ui_history:
                with st.chat_message(msg["role"]):
                    if msg["role"] == "user":
                        st.markdown(msg["content"])
                    else:
                        st.success(msg["explanation"])
                        with st.expander("View SQL"):
                            st.code(msg["sql_query"], language="sql")
                        if msg["results"]:
                            st.dataframe(pd.DataFrame(msg["results"]), use_container_width=True)
                        else:
                            st.info("No results found.")
    
    if question := st.chat_input("Ask anything about your business data..."):
        if st.session_state.current_chat_id is None:
            st.session_state.current_chat_id = str(uuid.uuid4())
            title = " ".join(question.split()[:4]) + "..."
            chats_db[st.session_state.current_chat_id] = {"title": title, "api_history": [], "ui_history": []}
            api_history = []
            ui_history = []
            
        ui_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(
                        f"{os.getenv('BACKEND_URL', 'http://backend:8000')}/ai/query",
                        json={"question": question, "history": api_history}
                    )
                    
                    if not response.ok:
                        try:
                            error_msg = response.json().get("detail", response.text)
                        except:
                            error_msg = response.text
                        st.error(f"Backend Error (Status {response.status_code}): {error_msg}")
                        ui_history.pop() # remove user message if failed
                    else:
                        data = response.json()
                        api_history = data["history"]
                        
                        explanation = data["explanation"]
                        sql = data["sql_query"]
                        results = data["results"]
                        
                        st.success(explanation)
                        with st.expander("View SQL"):
                            st.code(sql, language="sql")
                        if results:
                            df = pd.DataFrame(results)
                            st.dataframe(df, use_container_width=True)
                        else:
                            st.info("No results found.")
                            
                        ui_history.append({
                            "role": "assistant", 
                            "explanation": explanation, 
                            "sql_query": sql, 
                            "results": results
                        })
                        
                        # Save to persistent storage
                        chats_db[st.session_state.current_chat_id]["api_history"] = api_history
                        chats_db[st.session_state.current_chat_id]["ui_history"] = ui_history
                        save_chats(chats_db)
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
                    ui_history.pop()
