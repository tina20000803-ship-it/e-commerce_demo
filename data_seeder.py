import pyodbc
import random
import datetime

# ==========================================
# 1. 資料庫連線設定 (請根據你的環境修改)
# ==========================================
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"          # 如果是本機就寫 localhost，或寫你的伺服器名稱
    "DATABASE=EC;"      # 你的資料庫名稱
    "UID=sa;"                    # 你的資料庫帳號
    "PWD=YOUR_PASSWORD;"             # 你的資料庫密碼
)

try:
    # 建立連線
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    # 🔥 精髓：開啟高效批次寫入模式，這行是效能暴增數百倍的關鍵！
    cursor.fast_executemany = True
    print("成功連線至資料庫！開始準備生成資料...")
except Exception as e:
    print(f"資料庫連線失敗，請檢查連線字串。錯誤訊息：\n{e}")
    exit()

# ==========================================
# 2. 生成基礎資料 (會員與商品)
# ==========================================
print("正在生成會員與商品基礎資料...")

# 模擬 100 位會員
members_data = []
first_names = ["張", "王", "李", "劉", "陳", "楊", "趙", "黃", "周", "吳"]
last_names = ["偉", "娟", "傑", "敏", "強", "磊", "洋", "勇", "軍", "麗", "婷", "宇", "豪"]

for i in range(1, 101):
    name = random.choice(first_names) + random.choice(last_names) + random.choice([random.choice(last_names), ""])
    email = f"user{i:03d}@example.com"
    phone = f"09{random.randint(10000000, 99999999)}"
    # 註冊時間分布在 2024 ~ 2025 年間
    reg_date = datetime.datetime(2024, 1, 1) + datetime.timedelta(days=random.randint(0, 500))
    members_data.append((name, email, phone, reg_date))

# 批次寫入會員
cursor.executemany(
    "INSERT INTO Members (MemberName, Email, Phone, RegisterDate) VALUES (?, ?, ?, ?)",
    members_data
)

# 模擬 20 項熱銷商品 (分類與價格區間)
products_pool = [
    ("iPhone 15 Pro", "3C", 36900.00), ("無線藍牙耳機", "3C", 2490.00), ("機械鍵盤", "3C", 3200.00),
    ("人體工學辦公椅", "家具", 5800.00), ("電動升降桌", "家具", 12000.00), ("北歐風立燈", "家具", 1500.00),
    ("純棉素色T恤", "服飾", 490.00), ("防風機能外套", "服飾", 2980.00), ("日系寬褲", "服飾", 890.00),
    ("綜合堅果禮盒", "食品", 550.00), ("精品手沖咖啡豆", "食品", 600.00), ("膠原蛋白飲", "食品", 1200.00),
    ("自動保濕精華", "美妝", 1850.00), ("霧面持久口紅", "美妝", 980.00), ("草本控油洗髮精", "美妝", 450.00),
    ("多功能料理鍋", "家電", 3280.00), ("負離子吹風機", "家電", 1980.00), ("智能掃地機器人", "家電", 14800.00),
    ("微波爐", "家電", 3990.00), ("保溫隨行杯", "生活百貨", 650.00)
]

products_data = [(p[0], p[1], p[2], random.randint(50, 500)) for p in products_pool]

# 批次寫入商品
cursor.executemany(
    "INSERT INTO Products (ProductName, Category, Price, Stock) VALUES (?, ?, ?, ?)",
    products_data
)
conn.commit() # 先提交前兩張表，確保後面的訂單能對應到 MemberID 與 ProductID

# ==========================================
# 3. 核心：生成 10,000 筆訂單與明細
# ==========================================
print("基礎資料完成。開始生成 10,000 筆訂單與其明細...")

orders_data = []
order_details_data = []

current_order_id = 10001  # 對應資料庫 IDENTITY(10001,1)
addresses = ["台北市信義路", "新北市板橋區", "台中市台灣大道", "高雄市中山路", "桃園市中正路", "新竹市科學園區路"]

# 模擬這 10,000 筆訂單分散在過去的一年半內（2024/11 到 2026/05）
start_date = datetime.datetime(2024, 11, 1)

for _ in range(10000):
    member_id = random.randint(1, 100)
    # 隨機生成訂單日期，刻意讓日期亂序或有集中趨勢
    order_date = start_date + datetime.timedelta(
        days=random.randint(0, 550), 
        hours=random.randint(0, 23), 
        minutes=random.randint(0, 59)
    )
    address = random.choice(addresses) + str(random.randint(1, 300)) + "號"
    status = random.choices(["Paid", "Shipped", "Pending", "Cancelled"], weights=[70, 20, 7, 3])[0]
    
    # 決定這筆訂單買幾項不同的商品 (1 ~ 4 項)
    num_items = random.randint(1, 4)
    chosen_products = random.sample(products_pool, num_items)
    
    order_total_amount = 0.0
    
    for prod in chosen_products:
        # 在 pool 裡找對應的 ProductID (陣列索引 + 1)
        prod_id = products_pool.index(prod) + 1
        quantity = random.randint(1, 3)
        actual_price = prod[2] # 歷史實際購買單價
        
        # 累加這筆訂單的總金額
        order_total_amount += actual_price * quantity
        
        # 暫存明細資料 (OrderID, ProductID, Quantity, ActualUnitPrice)
        order_details_data.append((current_order_id, prod_id, quantity, actual_price))
    
    # 暫存訂單主表資料 (MemberID, OrderDate, TotalAmount, ShippingAddress, OrderStatus)
    orders_data.append((member_id, order_date, order_total_amount, address, status))
    current_order_id += 1

# ==========================================
# 4. 高效批次灌入資料庫
# ==========================================
print("數據計算完畢，正在高速寫入資料庫...")

# 寫入訂單主表
cursor.executemany(
    "INSERT INTO Orders (MemberID, OrderDate, TotalAmount, ShippingAddress, OrderStatus) VALUES (?, ?, ?, ?, ?)",
    orders_data
)

# 寫入訂單明細表
cursor.executemany(
    "INSERT INTO OrderDetails (OrderID, ProductID, Quantity, ActualUnitPrice) VALUES (?, ?, ?, ?)",
    order_details_data
)

# 真正提交到資料庫儲存
conn.commit()

# 關閉連線
cursor.close()
conn.close()

print("🎉 大功告成！成功匯入 100 筆會員、20 項商品、10,000 筆訂單與數萬筆明細。資料庫現在非常充實了！")