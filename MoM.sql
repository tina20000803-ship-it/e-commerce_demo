WITH MonthlyRevenue AS (
    -- 1. 先按月份將訂單金額加總
    SELECT 
        FORMAT(OrderDate, 'yyyy-MM') AS OrderMonth,
        SUM(TotalAmount) AS CurrentMonthRevenue
    FROM Orders
    WHERE OrderStatus IN ('Paid', 'Shipped')
    GROUP BY FORMAT(OrderDate, 'yyyy-MM')
),
CompareRevenue AS (
    -- 2. 利用 LAG 函數，把「上個月的營業額」拉到同一行對齊
    SELECT 
        OrderMonth,
        CurrentMonthRevenue,
        LAG(CurrentMonthRevenue, 1) OVER (ORDER BY OrderMonth) AS PreviousMonthRevenue
    FROM MonthlyRevenue
)
-- 3. 計算月成長率 (MoM)
SELECT 
    OrderMonth,
    CurrentMonthRevenue AS [本月營收],
    ISNULL(PreviousMonthRevenue, 0) AS [上月營收],
    CASE 
        WHEN PreviousMonthRevenue IS NULL THEN '0.00%'
        ELSE FORMAT((CurrentMonthRevenue - PreviousMonthRevenue) / PreviousMonthRevenue, 'P') 
    END AS [月成長率 (MoM)]
FROM CompareRevenue
ORDER BY OrderMonth;