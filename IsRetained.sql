WITH CustomerOrderCounts AS (
    -- 1. 計算每個會員分別消費了幾次
    SELECT 
        MemberID,
        COUNT(OrderID) AS OrderCount
    FROM Orders
    WHERE OrderStatus IN ('Paid', 'Shipped')
    GROUP BY MemberID
),
CustomerSegments AS (
    -- 2. 幫客戶分類：只買 1 次叫新客，2 次以上叫老客（複購客戶）
    SELECT 
        MemberID,
        CASE WHEN OrderCount >= 2 THEN 1 ELSE 0 END AS IsRetained
    FROM CustomerOrderCounts
)
-- 3. 計算全站總複購率
SELECT 
    COUNT(*) AS [總消費會員數],
    SUM(IsRetained) AS [複購會員數（消費2次以上）],
    -- 計算百分比
    FORMAT(CAST(SUM(IsRetained) AS FLOAT) / COUNT(*), 'P') AS [整體會員複購率]
FROM CustomerSegments;