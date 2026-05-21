import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

# 設定網頁標題與配置
st.set_page_config(page_title="電商 BI 管理後台", layout="wide")

# 1. 資料庫連線函式
def get_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=EC;"
        "UID=sa;"
        "PWD=YOUR_PASSWORD;"
    )
    return pyodbc.connect(conn_str)

st.title("📊 電商零售大數據分析系統")
st.markdown("本系統展示了從 10,000+ 筆原始訂單中提取的核心商業指標 (BI)。")

# 側邊欄：功能選擇
menu = st.sidebar.selectbox("切換報表", ["銷售總覽", "月營收成長分析", "客戶留存分析"])

# 2. 執行 SQL 並獲取數據
conn = get_connection()

if menu == "銷售總覽":
    st.subheader("🔥 熱銷商品排行榜 (Top 10)")
    # 使用你之前寫的 SQL 語法
    sql_query = """
    SELECT TOP 10 p.ProductName, SUM(od.Quantity) AS TotalQty, SUM(od.Quantity * od.ActualUnitPrice) AS Revenue
    FROM OrderDetails od
    JOIN Products p ON od.ProductID = p.ProductID
    GROUP BY p.ProductName ORDER BY Revenue DESC
    """
    df = pd.read_sql(sql_query, conn)
    
    # 顯示數據圖表
    fig = px.bar(df, x="ProductName", y="Revenue", color="Revenue", title="商品銷售額排名")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True)

elif menu == "月營收成長分析":
    st.subheader("📈 每月營收趨勢與 MoM 成長率")
    sql_query = """
    WITH Monthly AS (
        SELECT FORMAT(OrderDate, 'yyyy-MM') AS OrderMonth, SUM(TotalAmount) AS Revenue
        FROM Orders WHERE OrderStatus != 'Cancelled'
        GROUP BY FORMAT(OrderDate, 'yyyy-MM')
    )
    SELECT OrderMonth, Revenue, LAG(Revenue) OVER (ORDER BY OrderMonth) AS PrevRevenue
    FROM Monthly
    """
    df = pd.read_sql(sql_query, conn)
    df['MoM_Growth'] = (df['Revenue'] - df['PrevRevenue']) / df['PrevRevenue']
    
    fig = px.line(df, x="OrderMonth", y="Revenue", title="營收趨勢圖", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    st.write("營收成長數據細節：", df)

# 關閉連線
conn.close()

# 匯出按鈕範例
st.sidebar.download_button("匯出目前報表 (CSV)", df.to_csv(index=False), "report.csv", "text/csv")