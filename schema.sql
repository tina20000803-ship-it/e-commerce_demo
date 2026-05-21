-- 1. 建立會員資料表
CREATE TABLE Members (
    MemberID INT IDENTITY(1,1) PRIMARY KEY, -- 自動遞增主鍵
    MemberName NVARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,      -- 確保 Email 不會重複註冊
    Phone VARCHAR(20) NULL,
    RegisterDate DATETIME DEFAULT GETDATE(), -- 預設為建立當下時間
    Status NVARCHAR(10) DEFAULT 'Active'     -- 帳號狀態：Active/Suspended
);

-- 2. 建立商品資料表
CREATE TABLE Products (
    ProductID INT IDENTITY(1,1) PRIMARY KEY,
    ProductName NVARCHAR(100) NOT NULL,
    Category NVARCHAR(50) NOT NULL,          -- 商品分類（如：3C、服飾、食品）
    Price DECIMAL(10, 2) NOT NULL,           -- 使用 DECIMAL 處理金額，避免浮點數精準度誤差
    Stock INT NOT NULL DEFAULT 0,            -- 目前庫存量
    IsAvailable BIT DEFAULT 1                -- 是否上架：1=上架, 0=下架
);

-- 3. 建立訂單主表
CREATE TABLE Orders (
    OrderID INT IDENTITY(10001,1) PRIMARY KEY, -- 從 10001 開始編號，看起來更像真實訂單
    MemberID INT NOT NULL,                     -- 誰買的
    OrderDate DATETIME DEFAULT GETDATE(),      -- 購買時間
    TotalAmount DECIMAL(10, 2) NOT NULL,       -- 訂單總金額
    ShippingAddress NVARCHAR(255) NOT NULL,
    OrderStatus NVARCHAR(20) DEFAULT 'Pending',-- 訂單狀態：Pending/Paid/Shipped/Cancelled
    -- 建立外鍵約束：如果會員被刪除，禁止刪除此訂單（保護歷史交易紀錄）
    CONSTRAINT FK_Orders_Members FOREIGN KEY (MemberID) REFERENCES Members(MemberID)
);

-- 4. 建立訂單明細表
CREATE TABLE OrderDetails (
    OrderDetailID INT IDENTITY(1,1) PRIMARY KEY,
    OrderID INT NOT NULL,                      -- 屬於哪筆訂單
    ProductID INT NOT NULL,                    -- 買了什麼商品
    Quantity INT NOT NULL CHECK (Quantity > 0),-- 購買數量，必須大於 0
    ActualUnitPrice DECIMAL(10, 2) NOT NULL,   -- 購買當下的實際單價（應對歷史價格變動）
    -- 建立外鍵約束
    CONSTRAINT FK_Details_Orders FOREIGN KEY (OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE, -- 訂單若被刪除，明細一併刪除
    CONSTRAINT FK_Details_Products FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);