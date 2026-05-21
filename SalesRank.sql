WITH ProductSales AS (
    -- 先加總每樣商品的總銷售額與銷量
    SELECT 
        p.ProductID,
        p.ProductName,
        p.Category,
        SUM(od.Quantity) AS TotalQty,
        SUM(od.Quantity * od.ActualUnitPrice) AS TotalRevenue
    FROM OrderDetails od
    JOIN Products p ON od.ProductID = p.ProductID
    JOIN Orders o ON od.OrderID = o.OrderID
    WHERE o.OrderStatus IN ('Paid', 'Shipped') -- 排除未付款與已取消的訂單
    GROUP BY p.ProductID, p.ProductName, p.Category
)
SELECT 
    RANK() OVER (ORDER BY TotalRevenue DESC) AS SalesRank, -- 依營業額排名
    ProductName,
    Category,
    TotalQty,
    TotalRevenue,
    -- 精髓：計算這項商品佔全公司總營業額的百分比
    ROUND((TotalRevenue / SUM(TotalRevenue) OVER()) * 100, 2) AS RevenueSharePercent
FROM ProductSales;