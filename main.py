from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from typing import List, Optional
from datetime import date, datetime
import os
import re
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from fastapi.responses import StreamingResponse
import re

import models
import schemas
from database import engine, get_db, get_readonly_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BI Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=schemas.HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return {"status": "error", "database": "disconnected"}

@app.get("/sales", response_model=List[schemas.SaleOrderResponse])
def get_sales(db: Session = Depends(get_db)):
    orders = db.query(models.SalesOrder).order_by(desc(models.SalesOrder.total_amount)).limit(10).all()
    result = []
    for o in orders:
        result.append({
            "id": o.id,
            "customer_name": f"{o.customer.first_name} {o.customer.last_name}",
            "total_amount": o.total_amount
        })
    return result

@app.get("/products", response_model=List[schemas.ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()

@app.get("/customers", response_model=List[schemas.CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    return db.query(models.Customer).all()

@app.get("/sales/summary", response_model=schemas.SalesSummaryResponse)
def get_sales_summary(db: Session = Depends(get_db)):
    total_revenue = db.query(func.sum(models.SalesOrder.total_amount)).filter(models.SalesOrder.status != 'Cancelled').scalar() or 0
    total_orders = db.query(func.count(models.SalesOrder.id)).filter(models.SalesOrder.status != 'Cancelled').scalar() or 0
    total_customers = db.query(func.count(models.Customer.id)).scalar() or 0
    
    best_product = db.query(
        models.Product.name,
        func.sum(models.SalesOrderItem.quantity).label('total_qty')
    ).join(models.SalesOrderItem).join(models.SalesOrder).filter(models.SalesOrder.status != 'Cancelled').group_by(models.Product.name).order_by(desc('total_qty')).first()
    
    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "total_customers": total_customers,
        "best_selling_product": best_product[0] if best_product else None
    }

@app.get("/sales/by-product", response_model=List[schemas.RevenueByProductResponse])
def get_sales_by_product(start_date: Optional[date] = None, end_date: Optional[date] = None, db: Session = Depends(get_db)):
    query = db.query(
        models.Product.name,
        func.sum(models.SalesOrderItem.line_total).label('revenue')
    ).join(models.SalesOrderItem).join(models.SalesOrder).filter(models.SalesOrder.status != 'Cancelled')
    
    if start_date:
        query = query.filter(models.SalesOrder.order_date >= start_date)
    if end_date:
        query = query.filter(models.SalesOrder.order_date <= end_date)
        
    results = query.group_by(models.Product.name).order_by(desc('revenue')).all()
    return [{"product_name": r[0], "revenue": r[1]} for r in results]

@app.get("/sales/by-month", response_model=List[schemas.RevenueByMonthResponse])
def get_sales_by_month(db: Session = Depends(get_db)):
    # PostgreSQL specific func.to_char
    results = db.query(
        func.to_char(models.SalesOrder.order_date, 'YYYY-MM').label('month'),
        func.sum(models.SalesOrder.total_amount).label('revenue')
    ).filter(models.SalesOrder.status != 'Cancelled').group_by('month').order_by('month').all()
    
    return [{"month": r[0], "revenue": r[1]} for r in results]

@app.get("/sales/by-region", response_model=List[schemas.RevenueByRegionResponse])
def get_sales_by_region(start_date: Optional[date] = None, end_date: Optional[date] = None, db: Session = Depends(get_db)):
    query = db.query(
        models.Territory.region,
        func.sum(models.SalesOrder.total_amount).label('revenue')
    ).join(models.SalesOrder).filter(models.SalesOrder.status != 'Cancelled')
    
    if start_date:
        query = query.filter(models.SalesOrder.order_date >= start_date)
    if end_date:
        query = query.filter(models.SalesOrder.order_date <= end_date)
        
    results = query.group_by(models.Territory.region).order_by(desc('revenue')).all()
    return [{"region": r[0], "revenue": r[1]} for r in results]

@app.get("/sales/top-customers", response_model=List[schemas.TopCustomerResponse])
def get_top_customers(db: Session = Depends(get_db)):
    results = db.query(
        models.Customer.first_name,
        models.Customer.last_name,
        func.sum(models.SalesOrder.total_amount).label('total_spend')
    ).join(models.SalesOrder).filter(models.SalesOrder.status != 'Cancelled').group_by(models.Customer.id).order_by(desc('total_spend')).limit(10).all()
    
    return [{"customer_name": f"{r[0]} {r[1]}", "total_spend": r[2]} for r in results]

@app.post("/ai/query", response_model=schemas.AIQueryResponse)
def ai_query(request: schemas.AIQueryRequest, db: Session = Depends(get_readonly_db)):

    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.messages import HumanMessage, AIMessage
        
    from langchain_community.chat_models import ChatOllama
    
    # Connect to the local Ollama daemon running on the host machine
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        temperature=0,
        base_url="http://host.docker.internal:11434"
    )
    # Fetch all customers to 'train' the AI on exact names and places
    customers_data = db.query(models.Customer.first_name, models.Customer.last_name, models.Customer.city, models.Customer.country).all()
    customer_list_str = "\n".join([f"- {c[0]} {c[1]} (from {c[2]}, {c[3]})" for c in customers_data])
    
    schema_context = f"""
    Database Schema:
    - territories(id, name, region, country_group)
    - customers(id, first_name, last_name, email, country, city, segment)
    - products(id, name, category, subcategory, list_price, standard_cost)
    - sales_orders(id, customer_id, order_date, status, total_amount, territory) -> customer_id references customers(id), territory references territories(id)
    - sales_order_items(id, order_id, product_id, quantity, unit_price, line_total) -> order_id references sales_orders(id), product_id references products(id)
    
    Data Samples & Guidelines (IMPORTANT):
    - customers.segment only contains: 'Consumer', 'Corporate', 'Home Office'.
    - If asked "who is [name]", use ILIKE on first_name and last_name (e.g. WHERE first_name ILIKE '%karen%' OR last_name ILIKE '%karen%').
    
    Known Customers in Database (Use this to understand who they are and where they are from):
    {customer_list_str}
    """
    
    history_msgs = []
    # Only keep the last 6 messages to save context limits
    for msg in request.history[-6:]:
        if msg.get("role") == "user":
            history_msgs.append(HumanMessage(content=msg.get("content")))
        elif msg.get("role") == "assistant":
            history_msgs.append(AIMessage(content=msg.get("content")))
    
    sql_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert PostgreSQL SQL developer. Return ONLY valid PostgreSQL SQL for the user's question. Do not wrap it in markdown block. Do not add any explanation. Use the schema below:\n{schema}"),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{question}")
    ])
    
    chain = sql_prompt | llm
    sql_response = chain.invoke({"schema": schema_context, "history": history_msgs, "question": request.question})
    sql_query = sql_response.content.strip().strip("`").removeprefix("sql").strip()
    
    sql_match = re.search(r"(SELECT\s+.*?(?:;|$))", sql_query, re.IGNORECASE | re.DOTALL)
    if not sql_match:
        # The AI decided to answer directly without writing SQL
        # We append the AI's answer to the history
        history_msgs.append({"role": "assistant", "content": sql_query})
        return schemas.AIQueryResponse(
            explanation=sql_query,
            sql_query="-- No SQL query was needed. The AI answered directly from its context.",
            results=[],
            history=history_msgs
        )
        
    sql_query = sql_match.group(1).strip()
    forbidden_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    upper_query = sql_query.upper()
    for kw in forbidden_keywords:
        if re.search(rf"\b{kw}\b", upper_query):
            raise HTTPException(status_code=400, detail=f"Query contains forbidden keyword: {kw}")
            
    try:
        result_proxy = db.execute(text(sql_query))
        rows = result_proxy.mappings().all()
        results = [dict(row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error executing query: {str(e)}")
        
    explanation_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful business intelligence assistant. Based on the user's question, the SQL query used, and the JSON results, provide a concise, plain English explanation of the findings. Do not show the SQL again."),
        MessagesPlaceholder(variable_name="history"),
        ("user", "Question: {question}\nSQL: {sql}\nResults: {results}")
    ])
    explain_chain = explanation_prompt | llm
    explanation_response = explain_chain.invoke({
        "history": history_msgs,
        "question": request.question,
        "sql": sql_query,
        "results": str(results[:50])
    })
    
    new_history = request.history.copy() if request.history else []
    new_history.append({"role": "user", "content": request.question})
    # Embed the SQL in the assistant memory so future turns understand what was queried
    new_history.append({"role": "assistant", "content": f"{explanation_response.content}\n\nSQL Used:\n{sql_query}"})
    
    return {
        "explanation": explanation_response.content,
        "sql_query": sql_query,
        "results": results,
        "history": new_history
    }

@app.get("/report/generate")
def generate_report(db: Session = Depends(get_readonly_db)):
    total_revenue = db.query(func.sum(models.SalesOrder.total_amount)).filter(models.SalesOrder.status != 'Cancelled').scalar() or 0
    total_orders = db.query(func.count(models.SalesOrder.id)).filter(models.SalesOrder.status != 'Cancelled').scalar() or 0
    total_customers = db.query(func.count(func.distinct(models.SalesOrder.customer_id))).filter(models.SalesOrder.status != 'Cancelled').scalar() or 0
    best_product = db.query(
        models.Product.name,
        func.sum(models.SalesOrderItem.quantity).label('total_qty')
    ).join(models.SalesOrderItem).join(models.SalesOrder).filter(models.SalesOrder.status != 'Cancelled').group_by(models.Product.name).order_by(desc('total_qty')).first()
    best_product_name = best_product[0] if best_product else "None"
    
    by_product = db.query(
        models.Product.name,
        func.sum(models.SalesOrderItem.line_total).label('revenue')
    ).join(models.SalesOrderItem).join(models.SalesOrder).filter(models.SalesOrder.status != 'Cancelled').group_by(models.Product.name).order_by(desc('revenue')).limit(10).all()
    
    by_month = db.query(
        func.to_char(models.SalesOrder.order_date, 'YYYY-MM').label('month'),
        func.sum(models.SalesOrder.total_amount).label('revenue')
    ).group_by('month').order_by('month').all()
    
    top_customers = db.query(
        models.Customer.first_name,
        models.Customer.last_name,
        func.sum(models.SalesOrder.total_amount).label('total_spend')
    ).join(models.SalesOrder).group_by(models.Customer.id).order_by(desc('total_spend')).limit(10).all()

    ai_summary = "AI summary generation failed."
    try:
        from langchain_community.chat_models import ChatOllama
        from langchain_core.prompts import ChatPromptTemplate
        
        llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            temperature=0,
            base_url="http://host.docker.internal:11434"
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert business analyst. Write a 3-4 sentence plain English executive summary based on the following KPIs. Do not use markdown."),
            ("user", "Total Revenue: ${revenue:,.2f}\nTotal Orders: {orders}\nTotal Customers: {customers}\nBest Selling Product: {best_product}")
        ])
        chain = prompt | llm
        summary_resp = chain.invoke({
            "revenue": float(total_revenue),
            "orders": total_orders,
            "customers": total_customers,
            "best_product": best_product_name
        })
        ai_summary = summary_resp.content.strip()
    except Exception as e:
        ai_summary = f"Could not generate AI summary: {e}"

    prod_names = [r[0][:15] + '...' if len(r[0])>15 else r[0] for r in by_product]
    prod_revs = [float(r[1]) for r in by_product]
    plt.figure(figsize=(6, 4))
    plt.barh(prod_names, prod_revs, color='skyblue')
    plt.title('Top 10 Products by Revenue')
    plt.xlabel('Revenue ($)')
    plt.tight_layout()
    prod_chart_buf = io.BytesIO()
    plt.savefig(prod_chart_buf, format='png')
    prod_chart_buf.seek(0)
    plt.close()
    
    months = [r[0] for r in by_month]
    month_revs = [float(r[1]) for r in by_month]
    plt.figure(figsize=(6, 4))
    plt.plot(months, month_revs, marker='o', color='coral')
    plt.title('Monthly Sales')
    plt.xlabel('Month')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    month_chart_buf = io.BytesIO()
    plt.savefig(month_chart_buf, format='png')
    month_chart_buf.seek(0)
    plt.close()
    
    pdf_buf = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("Business Intelligence Report", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(ai_summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Key Performance Indicators", styles['Heading2']))
    kpi_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"${float(total_revenue):,.2f}"],
        ["Total Orders", str(total_orders)],
        ["Total Customers", str(total_customers)],
        ["Best Product", best_product_name]
    ]
    t = Table(kpi_data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Visualizations", styles['Heading2']))
    story.append(Image(prod_chart_buf, width=400, height=260))
    story.append(Spacer(1, 12))
    story.append(Image(month_chart_buf, width=400, height=260))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Top 10 Customers", styles['Heading2']))
    cust_data = [["Name", "Total Spend"]]
    for r in top_customers:
        cust_data.append([f"{r[0]} {r[1]}", f"${float(r[2]):,.2f}"])
        
    t_cust = Table(cust_data, colWidths=[200, 200])
    t_cust.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(t_cust)
    
    doc.build(story)
    pdf_buf.seek(0)
    
    return StreamingResponse(pdf_buf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=bi_report.pdf"})
