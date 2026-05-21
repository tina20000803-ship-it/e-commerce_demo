# 📊 端到端電商數據工程與商業智慧 (BI) 分析系統

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![SQL Server](https://img.shields.io/badge/SQL_Server-2019+-red.svg)](https://www.microsoft.com/sql-server)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-ff4b4b.svg)](https://streamlit.io)

這是一個專為電商零售場景設計的**端到端（End-to-End）數據處理解決方案**。
本專案從零開始設計符合第三正規化 (3NF) 的關聯式資料庫，利用 Python 高效灌入 **10,000 筆以上**具備商業邏輯的模擬數據，並撰寫進階 SQL 視窗函數進行核心商業指標（BI）分析，最終透過 Streamlit 打造出供決策者操作的動態圖表後台。

---

## 🚀 專案核心亮點 (Key Highlights)

* **百萬級寫入優化**：利用 Python `pyodbc` 的 `fast_executemany` 特性，將萬筆資料寫入速度提升 **50x - 100x**，有效解決傳統單筆 Insert 的 I/O 瓶頸。
* **真實商業邏輯模擬**：數據非隨機亂碼，而是透過機率權重（如 3% 取消率、歷史價格變動攔截）模擬真實電商生態，使分析結果具備實務參考價值。
* **進階 SQL 視窗函數應用**：活用 `LAG()` 進行時間序列月成長率 (MoM) 計算，並使用 `SUM() OVER()` 實現無縮減的營收佔比分析。
* **資安防護意識**：全專案敏感資訊（如資料庫密碼、連線字串）皆透過環境變數隔離，嚴禁寫死（Hard-coded）於代碼中。

---

## 📐 資料庫架構設計 (Schema Design)

本系統核心由 4 張資料表組成，嚴格遵循 **第三正規化 (3NF)** 設計，確保資料完整性並避免冗餘：



* `Members` (會員資料表)：儲存基本資訊與註冊時間。
* `Products` (商品資料表)：記錄品類、目前庫存與基準售價。
* `Orders` (訂單主表)：記錄買方、下單時間、總金額與訂單狀態（Paid/Shipped/Pending/Cancelled）。
* `OrderDetails` (訂單明細表)：**核心細節**。內含 `ActualUnitPrice`（實際購買單價），用以攔截因未來商品調價而導致歷史財務報表失真的「歷史價格陷阱」。

---

## 📊 核心 BI 數據分析邏輯 (SQL Snippets)

### 1. 每月營收與月成長率 (MoM)
展示如何活用 `LAG()` 函數將「上月營收」拉至同行，並透過 `CASE WHEN` 防範除以零的潰。
```sql
WITH MonthlyRevenue AS (
    SELECT FORMAT(OrderDate, 'yyyy-MM') AS OrderMonth, SUM(TotalAmount) AS CurrentMonthRevenue
    FROM Orders WHERE OrderStatus IN ('Paid', 'Shipped')
    GROUP BY FORMAT(OrderDate, 'yyyy-MM')
)
SELECT OrderMonth, CurrentMonthRevenue,
       LAG(CurrentMonthRevenue, 1) OVER (ORDER BY OrderMonth) AS PreviousMonthRevenue
FROM MonthlyRevenue;
