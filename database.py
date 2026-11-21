"""
土木工地日常行政與材料進出貨管理系統 - 資料庫模組
檔名固定命名為 site_management.db
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_management.db")

def get_connection() -> sqlite3.Connection:
    """建立並取得 SQLite 資料庫連線，設定 row_factory 為 sqlite3.Row 以便以欄位名稱存取"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """初始化資料表，若無資料則自動寫入貼近台灣土木工程與預拌混凝土品質管理實務的模擬測試資料"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. 協力廠商表 (vendors)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            trade_type TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            tax_id TEXT,
            rating INTEGER CHECK(rating BETWEEN 1 AND 5) DEFAULT 5
        );
        """)
        
        # 2. 材料進出貨紀錄表 (materials_log)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials_log (
            log_id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            material_name TEXT NOT NULL,
            transaction_type TEXT NOT NULL CHECK(transaction_type IN ('進貨', '領料')),
            quantity REAL NOT NULL CHECK(quantity > 0),
            unit TEXT NOT NULL,
            unit_price REAL NOT NULL DEFAULT 0,
            vendor_id TEXT,
            billing_status TEXT NOT NULL CHECK(billing_status IN ('未請款', '對帳中', '已請款')),
            safety_stock REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (vendor_id) REFERENCES vendors (vendor_id) ON DELETE SET NULL
        );
        """)
        
        # 3. 零用金與機具登記表 (admin_records)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_records (
            record_id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('行政零用金', '機具租借')),
            item_name TEXT NOT NULL,
            person_name TEXT DEFAULT '',
            amount_or_borrower TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('已核銷', '未核銷', '借出中', '已歸還', '借出', '歸還')),
            notes TEXT
        );
        """)
        
        # 自動相容升級：確保 person_name 欄位存在
        cursor.execute("PRAGMA table_info(admin_records)")
        cols = [c[1] for c in cursor.fetchall()]
        if "person_name" not in cols:
            cursor.execute("ALTER TABLE admin_records ADD COLUMN person_name TEXT DEFAULT ''")
        
        conn.commit()

        # 檢查是否需要自動寫入初始測試資料
        cursor.execute("SELECT COUNT(*) FROM vendors")
        vendor_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM materials_log")
        materials_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM admin_records")
        admin_count = cursor.fetchone()[0]

        if vendor_count == 0 and materials_count == 0 and admin_count == 0:
            seed_initial_data(conn)

def seed_initial_data(conn: sqlite3.Connection):
    """寫入台灣土木工程與預拌混凝土品質管理模擬測試資料"""
    cursor = conn.cursor()
    
    # 寫入 7 筆貼近台灣工程實務的協力廠商資料
    initial_vendors = [
        ("V001", "國產實業預拌混凝土廠", "混凝土廠", "林建國 廠長", "0912-345-678", "23456781", 5),
        ("V002", "台灣水泥（台泥大肚廠）", "混凝土廠", "郭振興 課長", "0928-888-123", "11953406", 5),
        ("V003", "豐興鋼鐵建材行", "鋼構", "陳志遠 業務專員", "04-2639-5566", "52410889", 4),
        ("V004", "嘉新砂石建材行", "泥作", "王德福 負責人", "0933-776-901", "86452130", 4),
        ("V005", "欣榮機電水電工程行", "水電", "蔡明宏 工務主任", "0955-432-109", "90234178", 5),
        ("V006", "永固五金建材機械行", "五金材料", "洪富山 老闆", "02-2987-6543", "34561289", 4),
        ("V007", "萬寶特用化學品行（強塑劑與外加劑）", "五金材料", "張美玲 經理", "0970-112-233", "77890124", 5),
    ]
    cursor.executemany("""
    INSERT INTO vendors (vendor_id, name, trade_type, contact_person, phone, tax_id, rating)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, initial_vendors)

    # 寫入 10 筆材料進出貨紀錄（含混凝土重要配比材料、鋼筋、模板等，並設計低於安全庫存情境）
    initial_materials = [
        ("MAT-20261101-001", "2026-11-01", "卜特蘭水泥", "進貨", 500, "包", 220, "V002", "已請款", 100),
        ("MAT-20261103-002", "2026-11-03", "鋼筋", "進貨", 60, "公噸", 23500, "V003", "已請款", 15),
        ("MAT-20261105-003", "2026-11-05", "砂石", "進貨", 120, "m³", 650, "V004", "對帳中", 30),
        ("MAT-20261108-004", "2026-11-08", "模板", "進貨", 800, "片", 380, "V006", "對帳中", 200),
        ("MAT-20261110-005", "2026-11-10", "爐石粉", "進貨", 40, "公噸", 2100, "V001", "未請款", 10),
        ("MAT-20261112-006", "2026-11-12", "飛灰", "進貨", 30, "公噸", 1850, "V001", "未請款", 8),
        ("MAT-20261114-007", "2026-11-14", "強塑劑", "進貨", 30, "桶", 3200, "V007", "未請款", 10),
        ("MAT-20261115-008", "2026-11-15", "卜特蘭水泥", "領料", 450, "包", 220, "V002", "已請款", 100),
        ("MAT-20261116-009", "2026-11-16", "鋼筋", "領料", 20, "公噸", 23500, "V003", "已請款", 15),
        ("MAT-20261118-010", "2026-11-18", "強塑劑", "領料", 25, "桶", 3200, "V007", "未請款", 10),
    ]
    cursor.executemany("""
    INSERT INTO materials_log (log_id, date, material_name, transaction_type, quantity, unit, unit_price, vendor_id, billing_status, safety_stock)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, initial_materials)

    # 寫入 8 筆行政零用金與機具租借登記資料（包含品管試驗儀器）
    initial_admin_records = [
        ("ADM-20261102-001", "2026-11-02", "行政零用金", "工地便當費", "3600", "已核銷", "大底連續壁澆置作業30人加班晚餐與夜點"),
        ("ADM-20261104-002", "2026-11-04", "機具租借", "坍度試驗組", "林品管師 (品管組)", "已歸還", "混凝土澆置前坍度試驗，已清潔入庫儀器室"),
        ("ADM-20261106-003", "2026-11-06", "行政零用金", "五金耗材", "2450", "已核銷", "採購防汛沙包與夜間反光警示帶"),
        ("ADM-20261109-004", "2026-11-09", "機具租借", "抗壓試體模具", "郭工程師 (品質課)", "借出中", "圓柱試體模12組，製作7天與28天抗壓試體"),
        ("ADM-20261112-005", "2026-11-12", "機具租借", "夯實機", "陳工頭 (土方組)", "借出中", "跳躍式土壤夯實機，開挖回填第2層夯實作業"),
        ("ADM-20261115-006", "2026-11-15", "行政零用金", "五金耗材", "1850", "已核銷", "工地急用水準管與鋼索固定夾"),
        ("ADM-20261117-007", "2026-11-17", "機具租借", "發電機", "張領班 (機電維護)", "借出中", "60kVA柴油靜音發電機，連續壁夜間抽水備用"),
        ("ADM-20261119-008", "2026-11-19", "行政零用金", "五金耗材", "4200", "已核銷", "新進勞工勞安工程安全帽與反光背心"),
    ]
    cursor.executemany("""
    INSERT INTO admin_records (record_id, date, category, item_name, amount_or_borrower, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, initial_admin_records)

    conn.commit()

# ==================== 協力廠商 (Vendors) CRUD ====================

def get_all_vendors(trade_type: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """查詢協力廠商清單，支援工種篩選與關鍵字搜尋"""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM vendors WHERE 1=1"
        params = []
        
        if trade_type and trade_type != "全部":
            query += " AND trade_type = ?"
            params.append(trade_type)
            
        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            query += " AND (vendor_id LIKE ? OR name LIKE ? OR contact_person LIKE ? OR phone LIKE ? OR tax_id LIKE ?)"
            params.extend([kw, kw, kw, kw, kw])
            
        query += " ORDER BY vendor_id ASC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_vendor_by_id(vendor_id: str) -> Optional[Dict[str, Any]]:
    """根據廠商編號取得單一廠商資料"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE vendor_id = ?", (vendor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_vendor(data: Dict[str, Any]) -> bool:
    """新增協力廠商"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO vendors (vendor_id, name, trade_type, contact_person, phone, tax_id, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["vendor_id"],
            data["name"],
            data["trade_type"],
            data.get("contact_person", ""),
            data.get("phone", ""),
            data.get("tax_id", ""),
            int(data.get("rating", 5))
        ))
        conn.commit()
        return True

def update_vendor(vendor_id: str, data: Dict[str, Any]) -> bool:
    """更新協力廠商資料"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE vendors 
        SET name = ?, trade_type = ?, contact_person = ?, phone = ?, tax_id = ?, rating = ?
        WHERE vendor_id = ?
        """, (
            data["name"],
            data["trade_type"],
            data.get("contact_person", ""),
            data.get("phone", ""),
            data.get("tax_id", ""),
            int(data.get("rating", 5)),
            vendor_id
        ))
        conn.commit()
        return True

def delete_vendor(vendor_id: str) -> bool:
    """刪除協力廠商"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendors WHERE vendor_id = ?", (vendor_id,))
        conn.commit()
        return True

# ==================== 材料紀錄與庫存看板 (Materials Log) ====================

def get_materials_inventory() -> List[Dict[str, Any]]:
    """
    計算即時材料庫存：
    分組計算各材料之 總進貨 - 總領料 = 目前庫存量，並對比最新設定之安全庫存警戒值。
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # 取得各材料的總進貨、總領料及最新單位與安全庫存
        cursor.execute("""
        SELECT 
            m.material_name,
            COALESCE(SUM(CASE WHEN m.transaction_type = '進貨' THEN m.quantity ELSE 0 END), 0) AS total_in,
            COALESCE(SUM(CASE WHEN m.transaction_type = '領料' THEN m.quantity ELSE 0 END), 0) AS total_out,
            (COALESCE(SUM(CASE WHEN m.transaction_type = '進貨' THEN m.quantity ELSE 0 END), 0) -
             COALESCE(SUM(CASE WHEN m.transaction_type = '領料' THEN m.quantity ELSE 0 END), 0)) AS current_stock,
            (SELECT safety_stock FROM materials_log WHERE material_name = m.material_name ORDER BY date DESC, log_id DESC LIMIT 1) AS safety_stock,
            (SELECT unit FROM materials_log WHERE material_name = m.material_name ORDER BY date DESC, log_id DESC LIMIT 1) AS unit,
            MAX(m.date) AS last_updated
        FROM materials_log m
        GROUP BY m.material_name
        ORDER BY m.material_name ASC
        """)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["is_low_stock"] = d["current_stock"] < d["safety_stock"]
            result.append(d)
        return result

def get_all_material_logs(material_name: Optional[str] = None, trans_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """取得材料進出貨紀錄清單，含關聯廠商名稱"""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
        SELECT m.*, v.name AS vendor_name, (m.quantity * m.unit_price) AS total_amount
        FROM materials_log m
        LEFT JOIN vendors v ON m.vendor_id = v.vendor_id
        WHERE 1=1
        """
        params = []
        if material_name and material_name != "全部":
            query += " AND m.material_name = ?"
            params.append(material_name)
        if trans_type and trans_type != "全部":
            query += " AND m.transaction_type = ?"
            params.append(trans_type)
        query += " ORDER BY m.date DESC, m.log_id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_material_log_by_id(log_id: str) -> Optional[Dict[str, Any]]:
    """取得特定單據編號之材料紀錄"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT m.*, v.name AS vendor_name, v.trade_type, v.contact_person, v.phone, v.tax_id, v.rating,
               (m.quantity * m.unit_price) AS total_amount
        FROM materials_log m
        LEFT JOIN vendors v ON m.vendor_id = v.vendor_id
        WHERE m.log_id = ?
        """, (log_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def add_material_log(data: Dict[str, Any]) -> bool:
    """新增進出貨紀錄"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO materials_log (log_id, date, material_name, transaction_type, quantity, unit, unit_price, vendor_id, billing_status, safety_stock)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["log_id"],
            data["date"],
            data["material_name"],
            data["transaction_type"],
            float(data["quantity"]),
            data["unit"],
            float(data.get("unit_price", 0.0)),
            data.get("vendor_id"),
            data.get("billing_status", "未請款"),
            float(data.get("safety_stock", 0.0))
        ))
        conn.commit()
        return True

def update_material_log(log_id: str, data: Dict[str, Any]) -> bool:
    """更新進出貨紀錄"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE materials_log
        SET date = ?, material_name = ?, transaction_type = ?, quantity = ?, unit = ?,
            unit_price = ?, vendor_id = ?, billing_status = ?, safety_stock = ?
        WHERE log_id = ?
        """, (
            data["date"],
            data["material_name"],
            data["transaction_type"],
            float(data["quantity"]),
            data["unit"],
            float(data.get("unit_price", 0.0)),
            data.get("vendor_id"),
            data.get("billing_status", "未請款"),
            float(data.get("safety_stock", 0.0)),
            log_id
        ))
        conn.commit()
        return True

def delete_material_log(log_id: str) -> bool:
    """刪除材料進出貨紀錄"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM materials_log WHERE log_id = ?", (log_id,))
        conn.commit()
        return True

def update_billing_status(log_id: str, new_status: str) -> bool:
    """直接更新請款對帳狀態 (未請款 / 對帳中 / 已請款)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE materials_log
        SET billing_status = ?
        WHERE log_id = ?
        """, (new_status, log_id))
        conn.commit()
        return True

def get_purchase_logs_with_vendor(billing_status: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """查詢所有「進貨」紀錄，並關聯供貨廠商資料"""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
        SELECT 
            m.log_id, m.date, m.material_name, m.quantity, m.unit, m.unit_price, 
            (m.quantity * m.unit_price) AS total_amount,
            m.billing_status, m.safety_stock,
            m.vendor_id, v.name AS vendor_name, v.trade_type, v.contact_person, v.phone, v.tax_id, v.rating
        FROM materials_log m
        LEFT JOIN vendors v ON m.vendor_id = v.vendor_id
        WHERE m.transaction_type = '進貨'
        """
        params = []
        if billing_status and billing_status != "全部":
            query += " AND m.billing_status = ?"
            params.append(billing_status)
        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            query += " AND (m.log_id LIKE ? OR m.material_name LIKE ? OR v.name LIKE ? OR v.contact_person LIKE ?)"
            params.extend([kw, kw, kw, kw])
            
        query += " ORDER BY m.date DESC, m.log_id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

# ==================== 行政零用金與機具租借 (Admin Records) ====================

def get_all_admin_records(category: Optional[str] = None, status: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """查詢日常行政與機具登記表"""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM admin_records WHERE 1=1"
        params = []
        if category and category != "全部":
            query += " AND category = ?"
            params.append(category)
        if status and status != "全部":
            if status in ["借出", "借出中"]:
                query += " AND status IN ('借出', '借出中')"
            elif status in ["歸還", "已歸還"]:
                query += " AND status IN ('歸還', '已歸還')"
            else:
                query += " AND status = ?"
                params.append(status)
        if keyword and keyword.strip():
            kw = f"%{keyword.strip()}%"
            query += " AND (record_id LIKE ? OR item_name LIKE ? OR person_name LIKE ? OR amount_or_borrower LIKE ? OR notes LIKE ?)"
            params.extend([kw, kw, kw, kw, kw])
            
        query += " ORDER BY date DESC, record_id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_borrowed_equipment() -> List[Dict[str, Any]]:
    """取得目前「借出中 / 借出」未歸還的機具清單"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM admin_records
        WHERE category = '機具租借' AND status IN ('借出中', '借出')
        ORDER BY date ASC, record_id ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

def get_petty_cash_total() -> float:
    """計算行政零用金支出總額"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT amount_or_borrower FROM admin_records WHERE category = '行政零用金'")
        rows = cursor.fetchall()
        total = 0.0
        for r in rows:
            val = str(r[0]).replace(",", "").replace("$", "").strip()
            try:
                total += float(val)
            except ValueError:
                pass
        return total

def add_admin_record(data: Dict[str, Any]) -> bool:
    """新增行政零用金或機具紀錄"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO admin_records (record_id, date, category, item_name, person_name, amount_or_borrower, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["record_id"],
            data["date"],
            data["category"],
            data["item_name"],
            str(data.get("person_name", "")).strip(),
            str(data["amount_or_borrower"]).strip(),
            data["status"],
            data.get("notes", "")
        ))
        conn.commit()
        return True

def update_admin_record(record_id: str, data: Dict[str, Any]) -> bool:
    """更新行政零用金或機具紀錄"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE admin_records
        SET date = ?, category = ?, item_name = ?, person_name = ?, amount_or_borrower = ?, status = ?, notes = ?
        WHERE record_id = ?
        """, (
            data["date"],
            data["category"],
            data["item_name"],
            str(data.get("person_name", "")).strip(),
            str(data["amount_or_borrower"]).strip(),
            data["status"],
            data.get("notes", ""),
            record_id
        ))
        conn.commit()
        return True

def delete_admin_record(record_id: str) -> bool:
    """刪除行政零用金或機具紀錄"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admin_records WHERE record_id = ?", (record_id,))
        conn.commit()
        return True

def quick_return_equipment(record_id: str) -> bool:
    """一鍵變更機具為「歸還」狀態"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE admin_records
        SET status = '歸還'
        WHERE record_id = ? AND category = '機具租借'
        """, (record_id,))
        conn.commit()
        return True
