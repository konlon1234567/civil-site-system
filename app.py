"""
土木工地日常行政與材料進出貨管理系統
技術架構：Python + Streamlit + SQLite
風格：簡潔明亮的台灣土木工程與預拌混凝土品質管理風格
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import database

# ==================== 頁面初始設定 ====================
st.set_page_config(
    page_title="土木工地日常行政與材料進出貨管理系統",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化資料庫與測試資料
database.init_db()

# ==================== 簡潔明亮的工程風格 CSS ====================
st.markdown("""
<style>
    /* 全域字體與背景基調 */
    .main {
        background-color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans TC", sans-serif;
    }
    
    /* 系統頂部主標題列 */
    .app-header {
        background: linear-gradient(135deg, #0f2b48 0%, #1a4971 100%);
        color: white;
        padding: 18px 24px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .app-header h1 {
        margin: 0;
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: #ffffff;
    }
    .app-header p {
        margin: 4px 0 0 0;
        font-size: 0.88rem;
        color: #93c5fd;
    }
    
    /* 醒目的安全庫存紅色警示橫幅 */
    .alert-banner {
        background-color: #fef2f2;
        border: 2px solid #ef4444;
        border-left: 8px solid #dc2626;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
        color: #991b1b;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.1);
    }
    .alert-banner h3 {
        margin: 0 0 6px 0;
        font-size: 1.15rem;
        font-weight: 700;
        color: #b91c1c;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* 正常狀態橫幅 */
    .safe-banner {
        background-color: #f0fdf4;
        border: 1px solid #86efac;
        border-left: 6px solid #16a34a;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
        color: #166534;
        font-weight: 500;
    }
    
    /* 工程數據卡片 (KPI Metric Cards) */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border-top: 4px solid #1a4971;
    }
    .metric-card.warning {
        border-top: 4px solid #dc2626;
    }
    .metric-card.success {
        border-top: 4px solid #16a34a;
    }
    .metric-card.amber {
        border-top: 4px solid #d97706;
    }
    .metric-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0f172a;
        margin: 4px 0;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #64748b;
    }
    
    /* 現代工程風格美觀表格容器 (支援無 pyarrow 環境) */
    .table-container {
        overflow-x: auto;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: white;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .civil-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.88rem;
        text-align: left;
        color: #1e293b;
    }
    .civil-table th {
        background-color: #f1f5f9;
        color: #334155;
        font-weight: 600;
        padding: 11px 14px;
        border-bottom: 2px solid #cbd5e1;
        white-space: nowrap;
    }
    .civil-table td {
        padding: 10px 14px;
        border-bottom: 1px solid #f1f5f9;
        vertical-align: middle;
    }
    .civil-table tr:hover {
        background-color: #f8fafc;
    }
    .civil-table tr:last-child td {
        border-bottom: none;
    }
    
    /* 標籤徽章 */
    .badge-borrowed {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .badge-returned {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

def render_civil_table(df: pd.DataFrame):
    """將 DataFrame 渲染為簡潔明亮的土木工程風格表格，零依賴 pyarrow"""
    if df.empty:
        st.info("尚無符合條件之資料。")
        return
    html_content = df.to_html(classes="civil-table", index=False, escape=False)
    st.markdown(f'<div class="table-container">{html_content}</div>', unsafe_allow_html=True)

# ==================== 頂部導覽列與工程標題 ====================
st.markdown("""
<div class="app-header">
    <div>
        <h1>🏗️ 土木工地日常行政與材料進出貨管理系統</h1>
        <p>工地現場材料進出動態 • 預拌混凝土品質管制配料 • 協力廠商名錄 • 行政零用金與機具租借管控</p>
    </div>
    <div style="text-align: right; font-size: 0.85rem; color: #e2e8f0;">
        <div>📍 工地位置：台北市中山區工區二標</div>
        <div>📅 系統基準日：{}</div>
    </div>
</div>
""".format(datetime.now().strftime("%Y年%m月%d日")), unsafe_allow_html=True)

# 建立四大主要分頁
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 材料進出貨與庫存看板",
    "🏢 協力廠商名錄與聯絡網",
    "📑 進貨單據與廠商對應查詢",
    "🛠️ 日常行政零用金與機具租借"
])

# =========================================================================
# 分頁一：材料進出貨與庫存看板
# =========================================================================
with tab1:
    st.subheader("📦 材料庫存即時水位與進出貨管理")
    
    # 1. 取得即時庫存統計
    inventory_data = database.get_materials_inventory()
    low_stock_items = [item for item in inventory_data if item["is_low_stock"]]
    
    # 2. 當任一材料低於安全警戒值時，在畫面最上方顯示醒目紅色警告橫幅 (亮紅燈提醒叫料)
    if low_stock_items:
        items_html = "".join([
            f"<li style='margin-top: 4px;'><strong>【{item['material_name']}】</strong>：目前庫存 <span style='font-size:1.1em; color:#b91c1c; font-weight:700;'>{item['current_stock']:.1f} {item['unit']}</span>（低於安全警戒值 <strong>{item['safety_stock']:.1f} {item['unit']}</strong>，短缺 <span style='color:#dc2626; font-weight:700;'>{item['safety_stock'] - item['current_stock']:.1f} {item['unit']}</span>）</li>"
            for item in low_stock_items
        ])
        st.markdown(f"""
        <div class="alert-banner">
            <h3>🚨 【安全庫存告急警戒】目前有 {len(low_stock_items)} 項材料低於安全庫存警戒線！請儘速安排叫料：</h3>
            <ul style="margin-bottom: 0; padding-left: 20px;">
                {items_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="safe-banner">
            ✅ 【庫存水位正常】所有土木材料與混凝土配料庫存量均維持在安全警戒值之上，現場供料無虞。
        </div>
        """, unsafe_allow_html=True)
        
    # 3. KPI 指標看板
    all_logs = database.get_all_material_logs()
    total_in_logs = sum(1 for x in all_logs if x["transaction_type"] == "進貨")
    total_out_logs = sum(1 for x in all_logs if x["transaction_type"] == "領料")
    
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown(f"""
        <div class="metric-card {'warning' if low_stock_items else 'success'}">
            <div class="metric-title">庫存警戒品項</div>
            <div class="metric-value" style="color: {'#dc2626' if low_stock_items else '#16a34a'};">{len(low_stock_items)} <span style="font-size:1rem; font-weight:normal;">項</span></div>
            <div class="metric-subtitle">需立即叫料補充之品項</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">監控工程材料品項</div>
            <div class="metric-value">{len(inventory_data)} <span style="font-size:1rem; font-weight:normal;">種</span></div>
            <div class="metric-subtitle">含混凝土膠結料、鋼筋、模板等</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">進貨累計單據數</div>
            <div class="metric-value">{total_in_logs} <span style="font-size:1rem; font-weight:normal;">筆</span></div>
            <div class="metric-subtitle">進料驗收登錄累計</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m4:
        st.markdown(f"""
        <div class="metric-card amber">
            <div class="metric-title">現場領料累計單據數</div>
            <div class="metric-value">{total_out_logs} <span style="font-size:1rem; font-weight:normal;">筆</span></div>
            <div class="metric-subtitle">工區配料出庫累計</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # 4. 材料庫存水位總覽表
    st.markdown("#### 📋 即時庫存水位清單（總進貨 - 總領料 = 目前庫存量）")
    if inventory_data:
        inv_rows = []
        for item in inventory_data:
            if item["is_low_stock"]:
                badge = f'<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:4px; font-weight:700;">🚨 偏低叫料 (缺 {item["safety_stock"] - item["current_stock"]:.1f})</span>'
                stock_str = f'<strong style="color:#dc2626; font-size:1.05em;">{item["current_stock"]:.1f}</strong>'
            else:
                badge = '<span style="background:#dcfce7; color:#166534; padding:2px 8px; border-radius:4px; font-weight:600;">✅ 庫存充足</span>'
                stock_str = f'<strong style="color:#0f172a;">{item["current_stock"]:.1f}</strong>'
                
            inv_rows.append({
                "材料名稱": f"<strong>{item['material_name']}</strong>",
                "目前庫存量": stock_str,
                "安全庫存警戒值": f"{item['safety_stock']:.1f}",
                "單位": item["unit"],
                "庫存狀態": badge,
                "總進貨量": f"{item['total_in']:.1f}",
                "總領料量": f"{item['total_out']:.1f}",
                "最後異動日期": item["last_updated"]
            })
        render_civil_table(pd.DataFrame(inv_rows))
    else:
        st.info("目前尚無材料庫存資料。")
        
    st.divider()
    
    # 5. 材料進出貨紀錄清單與篩選
    st.markdown("#### 📜 進出貨詳細紀錄清單")
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        mat_filter_choices = ["全部"] + sorted(list({x["material_name"] for x in all_logs})) if all_logs else ["全部"]
        selected_mat_filter = st.selectbox("材料品名篩選", mat_filter_choices, key="tab1_mat_filter")
    with f_col2:
        selected_type_filter = st.selectbox("異動類型篩選", ["全部", "進貨", "領料"], key="tab1_type_filter")
    with f_col3:
        st.write("")
        st.write("")
        st.caption("💡 提示：下方提供完整新增、修改與刪除 (CRUD) 表單。")
        
    filtered_logs = database.get_all_material_logs(
        material_name=selected_mat_filter if selected_mat_filter != "全部" else None,
        trans_type=selected_type_filter if selected_type_filter != "全部" else None
    )
    
    if filtered_logs:
        log_rows = []
        for l in filtered_logs:
            # 異動類型標籤
            t_badge = '<span style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-weight:600;">📥 進貨</span>' if l["transaction_type"] == "進貨" else '<span style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-weight:600;">📤 領料</span>'
            
            # 請款狀態標籤
            if l["billing_status"] == "已請款":
                b_badge = '<span style="background:#dcfce7; color:#166534; padding:2px 6px; border-radius:4px; font-weight:600;">已請款</span>'
            elif l["billing_status"] == "對帳中":
                b_badge = '<span style="background:#fef3c7; color:#92400e; padding:2px 6px; border-radius:4px; font-weight:600;">對帳中</span>'
            else:
                b_badge = '<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; font-weight:600;">未請款</span>'
                
            log_rows.append({
                "單據編號": f"<code>{l['log_id']}</code>",
                "日期": l["date"],
                "材料名稱": f"<strong>{l['material_name']}</strong>",
                "異動類型": t_badge,
                "數量": f"{l['quantity']:.1f}",
                "單位": l["unit"],
                "單價 (NTD)": f"NT$ {l['unit_price']:,.0f}",
                "總金額 (NTD)": f"NT$ {l['total_amount']:,.0f}",
                "關聯廠商": l["vendor_name"] or "<span style='color:#94a3b8;'>-</span>",
                "請款對帳狀態": b_badge,
                "設定警戒值": f"{l['safety_stock']:.1f}"
            })
        render_civil_table(pd.DataFrame(log_rows))
    else:
        st.info("無符合條件之進出貨紀錄。")
        
    st.write("")
    
    # 6. 進出貨紀錄 CRUD 表單（新增、修改、刪除）
    st.markdown("#### ⚙️ 進出貨紀錄資料管理 (CRUD)")
    c_tab1, c_tab2, c_tab3 = st.tabs(["➕ 新增進出貨紀錄", "✏️ 修改既有紀錄", "🗑️ 刪除單據紀錄"])
    
    # 協力廠商對應選單 (vendor_id -> name)
    vendors_list = database.get_all_vendors()
    vendor_options = {"無 (工地自用/內部調撥)": None}
    for v in vendors_list:
        vendor_options[f"{v['vendor_id']} - {v['name']} ({v['trade_type']})"] = v["vendor_id"]
        
    with c_tab1:
        st.caption("填寫表單以登記現場進料驗收或施工領料紀錄：")
        with st.form("form_add_material_log", clear_on_submit=True):
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                new_log_id = st.text_input("單據編號*", value=f"MAT-{datetime.now().strftime('%Y%m%d')}-{len(all_logs)+1:03d}")
                new_date = st.date_input("異動日期*", value=date.today())
                new_type = st.selectbox("異動類型*", ["進貨", "領料"])
            with col_a2:
                # 預設材料名稱選單
                default_materials = ["卜特蘭水泥", "鋼筋", "砂石", "模板", "爐石粉", "飛灰", "強塑劑"]
                mat_select_mode = st.radio("材料選擇模式", ["常用預設材料", "自訂新材料"], horizontal=True)
                if mat_select_mode == "常用預設材料":
                    new_mat_name = st.selectbox("材料名稱*", default_materials)
                else:
                    new_mat_name = st.text_input("自訂材料名稱*")
                    
                new_qty = st.number_input("數量*", min_value=0.1, value=10.0, step=1.0)
                new_unit = st.selectbox("單位*", ["包", "公噸", "m³", "片", "桶", "支", "組", "公斤"])
            with col_a3:
                new_price = st.number_input("單價 (NTD)*", min_value=0.0, value=250.0, step=10.0)
                new_vendor_label = st.selectbox("關聯協力廠商", list(vendor_options.keys()))
                new_billing = st.selectbox("請款對帳狀態*", ["未請款", "對帳中", "已請款"])
                new_safety = st.number_input("安全庫存警戒值*", min_value=0.0, value=50.0, step=5.0)
                
            submitted_add = st.form_submit_button("💾 新增單據紀錄", use_container_width=True)
            if submitted_add:
                if not new_log_id or not new_mat_name:
                    st.error("請填寫單據編號與材料名稱！")
                else:
                    try:
                        database.add_material_log({
                            "log_id": new_log_id.strip(),
                            "date": str(new_date),
                            "material_name": new_mat_name.strip(),
                            "transaction_type": new_type,
                            "quantity": new_qty,
                            "unit": new_unit,
                            "unit_price": new_price,
                            "vendor_id": vendor_options[new_vendor_label],
                            "billing_status": new_billing,
                            "safety_stock": new_safety
                        })
                        st.success(f"單據 {new_log_id} 已成功新增！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"新增失敗，原因：{e}")
                        
    with c_tab2:
        if all_logs:
            edit_log_choices = [f"{x['log_id']} | {x['date']} | {x['material_name']} ({x['transaction_type']})" for x in all_logs]
            selected_edit_label = st.selectbox("請選擇欲修改的單據編號", edit_log_choices, key="sel_edit_log")
            selected_log_id = selected_edit_label.split(" | ")[0]
            current_log = database.get_material_log_by_id(selected_log_id)
            
            if current_log:
                with st.form("form_edit_material_log"):
                    col_e1, col_e2, col_e3 = st.columns(3)
                    with col_e1:
                        st.text_input("單據編號 (不可修改)", value=current_log["log_id"], disabled=True)
                        edit_date = st.date_input("異動日期", value=datetime.strptime(current_log["date"], "%Y-%m-%d").date())
                        edit_type = st.selectbox("異動類型", ["進貨", "領料"], index=0 if current_log["transaction_type"] == "進貨" else 1)
                    with col_e2:
                        edit_mat_name = st.text_input("材料名稱", value=current_log["material_name"])
                        edit_qty = st.number_input("數量", min_value=0.1, value=float(current_log["quantity"]), step=1.0)
                        edit_unit = st.text_input("單位", value=current_log["unit"])
                    with col_e3:
                        edit_price = st.number_input("單價 (NTD)", min_value=0.0, value=float(current_log["unit_price"]), step=10.0)
                        
                        # 定位既有廠商索引
                        current_v_idx = 0
                        labels = list(vendor_options.keys())
                        for idx, l in enumerate(labels):
                            if vendor_options[l] == current_log["vendor_id"]:
                                current_v_idx = idx
                                break
                        edit_vendor_label = st.selectbox("關聯協力廠商", labels, index=current_v_idx)
                        
                        status_list = ["未請款", "對帳中", "已請款"]
                        b_idx = status_list.index(current_log["billing_status"]) if current_log["billing_status"] in status_list else 0
                        edit_billing = st.selectbox("請款對帳狀態", status_list, index=b_idx)
                        edit_safety = st.number_input("安全庫存警戒值", min_value=0.0, value=float(current_log["safety_stock"]), step=5.0)
                        
                    submitted_edit = st.form_submit_button("📝 儲存修改內容", use_container_width=True)
                    if submitted_edit:
                        try:
                            database.update_material_log(current_log["log_id"], {
                                "date": str(edit_date),
                                "material_name": edit_mat_name.strip(),
                                "transaction_type": edit_type,
                                "quantity": edit_qty,
                                "unit": edit_unit.strip(),
                                "unit_price": edit_price,
                                "vendor_id": vendor_options[edit_vendor_label],
                                "billing_status": edit_billing,
                                "safety_stock": edit_safety
                            })
                            st.success(f"單據 {current_log['log_id']} 已更新成功！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"更新失敗：{e}")
        else:
            st.info("尚無可修改之單據紀錄。")
            
    with c_tab3:
        if all_logs:
            del_log_choices = [f"{x['log_id']} | {x['date']} | {x['material_name']} ({x['transaction_type']}) - 數量: {x['quantity']} {x['unit']}" for x in all_logs]
            selected_del_label = st.selectbox("選擇欲刪除之單據編號", del_log_choices, key="sel_del_log")
            selected_del_id = selected_del_label.split(" | ")[0]
            
            st.warning(f"⚠️ 注意：刪除後將影響材料即時庫存統計量！確認要刪除單據「{selected_del_id}」？")
            if st.button("🗑️ 確認永久刪除此筆單據", type="primary"):
                database.delete_material_log(selected_del_id)
                st.success(f"單據 {selected_del_id} 已成功刪除！")
                st.rerun()
        else:
            st.info("尚無可刪除之單據紀錄。")


# =========================================================================
# 分頁二：協力廠商名錄與聯絡網
# =========================================================================
with tab2:
    st.subheader("🏢 工地協力廠商名錄與專案聯絡網")
    st.caption("管理混凝土預拌廠、鋼構、機電水電、泥作及五金材料供應商資料，支援完整 CRUD 操作。")
    
    # 1. 篩選與搜尋列
    v_col1, v_col2 = st.columns([1, 2])
    with v_col1:
        trade_categories = ["全部", "混凝土廠", "水電", "泥作", "鋼構", "五金材料"]
        selected_trade = st.selectbox("工種分類篩選", trade_categories, key="v_trade_filter")
    with v_col2:
        search_kw = st.text_input("🔍 關鍵字搜尋（廠商名稱 / 聯絡人 / 電話 / 統一編號）", placeholder="輸入關鍵字如：國產、台泥、林建國、0912...", key="v_keyword")
        
    vendors_data = database.get_all_vendors(
        trade_type=selected_trade if selected_trade != "全部" else None,
        keyword=search_kw
    )
    
    # 2. 統計指標
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("符合廠商數", f"{len(vendors_data)} 家")
    with c2:
        concrete_count = sum(1 for v in vendors_data if v["trade_type"] == "混凝土廠")
        st.metric("混凝土供應廠", f"{concrete_count} 家")
    with c3:
        high_rated_count = sum(1 for v in vendors_data if v["rating"] >= 5)
        st.metric("5星特優合作廠商", f"{high_rated_count} 家")
    with c4:
        hardware_count = sum(1 for v in vendors_data if v["trade_type"] in ["五金材料", "鋼構"])
        st.metric("鋼構與材料商", f"{hardware_count} 家")
        
    st.write("")
    
    # 3. 廠商資料表展示
    if vendors_data:
        v_rows = []
        for v in vendors_data:
            rating_stars = "⭐" * int(v["rating"])
            v_rows.append({
                "廠商編號": f"<code>{v['vendor_id']}</code>",
                "廠商名稱": f"<strong>{v['name']}</strong>",
                "工種分類": f"<span style='background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-weight:600;'>{v['trade_type']}</span>",
                "聯絡人": v["contact_person"] or "-",
                "電話": f"<a href='tel:{v['phone']}' style='color:#2563eb; text-decoration:none;'>📞 {v['phone']}</a>" if v["phone"] else "-",
                "統一編號": f"<code>{v['tax_id']}</code>" if v["tax_id"] else "-",
                "配合評價": f"<span style='font-size:1.1em;'>{rating_stars}</span>"
            })
        render_civil_table(pd.DataFrame(v_rows))
    else:
        st.warning("查無符合條件之協力廠商資料。")
        
    st.divider()
    
    # 4. 協力廠商 CRUD 管理表單
    st.markdown("#### ⚙️ 協力廠商資料管理 (CRUD)")
    v_tab1, v_tab2, v_tab3 = st.tabs(["➕ 新增協力廠商", "✏️ 編輯廠商資料", "🗑️ 刪除協力廠商"])
    
    with v_tab1:
        with st.form("form_add_vendor", clear_on_submit=True):
            col_v1, col_v2 = st.columns(2)
            all_v_raw = database.get_all_vendors()
            next_vid = f"V{len(all_v_raw)+1:03d}"
            
            with col_v1:
                new_v_id = st.text_input("廠商編號*", value=next_vid)
                new_v_name = st.text_input("廠商名稱* (如：台灣水泥、亞東預拌)")
                new_v_trade = st.selectbox("工種分類*", ["混凝土廠", "水電", "泥作", "鋼構", "五金材料"])
                new_v_contact = st.text_input("聯絡人姓名與職稱 (如：陳主任)")
            with col_v2:
                new_v_phone = st.text_input("聯絡電話* (手機或市話)")
                new_v_tax = st.text_input("統一編號 (8碼統編)")
                new_v_rating = st.slider("配合評價 (1~5星)*", min_value=1, max_value=5, value=5)
                
            submitted_v_add = st.form_submit_button("💾 新增廠商資料", use_container_width=True)
            if submitted_v_add:
                if not new_v_id or not new_v_name or not new_v_phone:
                    st.error("請確認填寫廠商編號、廠商名稱與聯絡電話！")
                else:
                    try:
                        database.add_vendor({
                            "vendor_id": new_v_id.strip(),
                            "name": new_v_name.strip(),
                            "trade_type": new_v_trade,
                            "contact_person": new_v_contact.strip(),
                            "phone": new_v_phone.strip(),
                            "tax_id": new_v_tax.strip(),
                            "rating": new_v_rating
                        })
                        st.success(f"協力廠商 {new_v_name} 已成功建檔！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"新增廠商失敗：{e}")
                        
    with v_tab2:
        all_vendors_list = database.get_all_vendors()
        if all_vendors_list:
            v_edit_choices = [f"{v['vendor_id']} - {v['name']} ({v['trade_type']})" for v in all_vendors_list]
            sel_v_edit_label = st.selectbox("選擇欲編輯之廠商", v_edit_choices, key="sel_v_edit")
            sel_v_id = sel_v_edit_label.split(" - ")[0]
            current_v = database.get_vendor_by_id(sel_v_id)
            
            if current_v:
                with st.form("form_edit_vendor"):
                    col_ev1, col_ev2 = st.columns(2)
                    with col_ev1:
                        st.text_input("廠商編號 (主鍵不可修改)", value=current_v["vendor_id"], disabled=True)
                        edit_v_name = st.text_input("廠商名稱", value=current_v["name"])
                        trades = ["混凝土廠", "水電", "泥作", "鋼構", "五金材料"]
                        t_idx = trades.index(current_v["trade_type"]) if current_v["trade_type"] in trades else 0
                        edit_v_trade = st.selectbox("工種分類", trades, index=t_idx)
                        edit_v_contact = st.text_input("聯絡人", value=current_v["contact_person"] or "")
                    with col_ev2:
                        edit_v_phone = st.text_input("電話", value=current_v["phone"] or "")
                        edit_v_tax = st.text_input("統一編號", value=current_v["tax_id"] or "")
                        edit_v_rating = st.slider("配合評價", min_value=1, max_value=5, value=int(current_v["rating"]))
                        
                    submitted_v_edit = st.form_submit_button("📝 儲存廠商修改", use_container_width=True)
                    if submitted_v_edit:
                        try:
                            database.update_vendor(current_v["vendor_id"], {
                                "name": edit_v_name.strip(),
                                "trade_type": edit_v_trade,
                                "contact_person": edit_v_contact.strip(),
                                "phone": edit_v_phone.strip(),
                                "tax_id": edit_v_tax.strip(),
                                "rating": edit_v_rating
                            })
                            st.success(f"廠商 {current_v['vendor_id']} 資料已更新！")
                            st.rerun()
                        except Exception as e:
                            st.error(f"更新廠商資料失敗：{e}")
        else:
            st.info("尚無廠商資料可供編輯。")
            
    with v_tab3:
        if all_vendors_list:
            v_del_choices = [f"{v['vendor_id']} - {v['name']} ({v['trade_type']})" for v in all_vendors_list]
            sel_v_del_label = st.selectbox("選擇欲刪除之廠商", v_del_choices, key="sel_v_del")
            sel_v_del_id = sel_v_del_label.split(" - ")[0]
            
            st.warning(f"⚠️ 注意：若刪除廠商「{sel_v_del_label}」，關聯的進出貨紀錄其廠商欄位將被清空。確認刪除？")
            if st.button("🗑️ 確認永久刪除廠商資料", type="primary", key="btn_del_vendor"):
                database.delete_vendor(sel_v_del_id)
                st.success(f"廠商 {sel_v_del_id} 已成功刪除！")
                st.rerun()
        else:
            st.info("尚無廠商資料。")


# =========================================================================
# 分頁三：進貨單據與廠商對應查詢
# =========================================================================
with tab3:
    st.subheader("📑 進貨單據與供應廠商詳細對照查詢")
    st.caption("檢視所有現場材料進料單據，點選任一單據即可自動關聯供貨廠商聯絡資訊與對帳總額，並可直接更新請款對帳狀態。")
    
    # 1. 請款對帳篩選與搜尋
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        bill_filter = st.selectbox("請款對帳狀態篩選", ["全部", "未請款", "對帳中", "已請款"], key="tab3_bill_filter")
    with col_p2:
        search_purchase = st.text_input("🔍 搜尋進貨單（單據編號 / 材料名稱 / 廠商名稱 / 聯絡人）", key="tab3_kw")
        
    purchases = database.get_purchase_logs_with_vendor(
        billing_status=bill_filter if bill_filter != "全部" else None,
        keyword=search_purchase
    )
    
    # 2. 總覽數據
    total_purchase_amount = sum(p["total_amount"] for p in purchases)
    unbilled_count = sum(1 for p in purchases if p["billing_status"] == "未請款")
    reconciling_count = sum(1 for p in purchases if p["billing_status"] == "對帳中")
    billed_count = sum(1 for p in purchases if p["billing_status"] == "已請款")
    
    pa_col1, pa_col2, pa_col3, pa_col4 = st.columns(4)
    with pa_col1:
        st.metric("進貨單據總數", f"{len(purchases)} 筆")
    with pa_col2:
        st.metric("採購累計總金額", f"NT$ {total_purchase_amount:,.0f}")
    with pa_col3:
        st.metric("未請款單據數", f"{unbilled_count} 筆", delta=f"{unbilled_count} 筆待辦" if unbilled_count else None, delta_color="inverse")
    with pa_col4:
        st.metric("對帳中單據數", f"{reconciling_count} 筆")
        
    st.write("")
    
    # 3. 進貨單據清單
    if purchases:
        p_rows = []
        for p in purchases:
            if p["billing_status"] == "已請款":
                stat_badge = '<span style="background:#dcfce7; color:#166534; padding:2px 6px; border-radius:4px; font-weight:600;">已請款</span>'
            elif p["billing_status"] == "對帳中":
                stat_badge = '<span style="background:#fef3c7; color:#92400e; padding:2px 6px; border-radius:4px; font-weight:600;">對帳中</span>'
            else:
                stat_badge = '<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; font-weight:600;">未請款</span>'
                
            p_rows.append({
                "單據編號": f"<code>{p['log_id']}</code>",
                "進貨日期": p["date"],
                "進貨材料": f"<strong>{p['material_name']}</strong>",
                "數量": f"{p['quantity']:.1f}",
                "單位": p["unit"],
                "單價 (NTD)": f"NT$ {p['unit_price']:,.0f}",
                "採購總額 (NTD)": f"<strong style='color:#1e40af;'>NT$ {p['total_amount']:,.0f}</strong>",
                "供貨廠商": p["vendor_name"] or "<span style='color:#94a3b8;'>-</span>",
                "請款對帳狀態": stat_badge,
                "廠商電話": p["phone"] or "-"
            })
        render_civil_table(pd.DataFrame(p_rows))
    else:
        st.info("查無進貨紀錄。")
        
    st.divider()
    
    # 4. 點選單據進行廠商詳細關聯帶出與即時切換更新請款狀態
    st.markdown("#### 🔍 單據關聯廠商詳細卡片與對帳狀態切換")
    
    if purchases:
        purchase_choices = [
            f"{p['log_id']} | {p['date']} | {p['material_name']} | 供貨商: {p['vendor_name'] or '未指定'} | NT$ {p['total_amount']:,.0f} [{p['billing_status']}]"
            for p in purchases
        ]
        selected_p_label = st.selectbox("👇 請選擇任一筆進貨單據展開檢視：", purchase_choices, key="tab3_p_select")
        sel_log_id = selected_p_label.split(" | ")[0]
        
        # 取得被選中單據的完整資訊
        selected_record = next((p for p in purchases if p["log_id"] == sel_log_id), None)
        
        if selected_record:
            st.markdown(f"##### 📦 單據編號：`{selected_record['log_id']}` 詳細資訊與廠商關聯卡")
            
            c_card1, c_card2 = st.columns([1.1, 1.2])
            
            with c_card1:
                st.markdown("""
                <div style="background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <h4 style="margin-top:0; color:#1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">📋 單據採購明細</h4>
                    <p style="margin: 6px 0;"><strong>進貨日期：</strong> {date}</p>
                    <p style="margin: 6px 0;"><strong>材料名稱：</strong> <span style="font-size:1.1em; color:#0f172a; font-weight:600;">{mat}</span></p>
                    <p style="margin: 6px 0;"><strong>進貨數量：</strong> {qty:.1f} {unit}</p>
                    <p style="margin: 6px 0;"><strong>採購單價：</strong> NT$ {price:,.1f} / {unit}</p>
                    <div style="background: #f1f5f9; padding: 10px; border-radius: 6px; margin: 12px 0;">
                        <span style="color:#475569; font-weight:600;">採購總金額：</span>
                        <span style="font-size:1.35em; color:#1e40af; font-weight:700;">NT$ {total:,.0f} 元</span>
                    </div>
                    <p style="margin: 6px 0;"><strong>目前請款狀態：</strong> <span style="padding: 2px 8px; border-radius: 4px; font-weight:700; background:{status_bg}; color:{status_color};">{status}</span></p>
                </div>
                """.format(
                    date=selected_record["date"],
                    mat=selected_record["material_name"],
                    qty=selected_record["quantity"],
                    unit=selected_record["unit"],
                    price=selected_record["unit_price"],
                    total=selected_record["total_amount"],
                    status=selected_record["billing_status"],
                    status_bg="#dcfce7" if selected_record["billing_status"] == "已請款" else ("#fef3c7" if selected_record["billing_status"] == "對帳中" else "#fee2e2"),
                    status_color="#166534" if selected_record["billing_status"] == "已請款" else ("#92400e" if selected_record["billing_status"] == "對帳中" else "#991b1b")
                ), unsafe_allow_html=True)
                
                st.write("")
                st.markdown("##### ⚡ 直接切換請款對帳狀態")
                with st.form("form_update_billing"):
                    status_opts = ["未請款", "對帳中", "已請款"]
                    curr_idx = status_opts.index(selected_record["billing_status"]) if selected_record["billing_status"] in status_opts else 0
                    new_b_status = st.radio("更新請款狀態為：", status_opts, index=curr_idx, horizontal=True)
                    submitted_b_update = st.form_submit_button("💾 確認更新對帳狀態", type="primary", use_container_width=True)
                    if submitted_b_update:
                        database.update_billing_status(selected_record["log_id"], new_b_status)
                        st.toast(f"單據 {selected_record['log_id']} 請款狀態已更新為「{new_b_status}」！", icon="✅")
                        st.success(f"單據 {selected_record['log_id']} 狀態已成功更新為：{new_b_status}")
                        st.rerun()
                        
            with c_card2:
                v_name = selected_record["vendor_name"] or "未關聯廠商"
                v_trade = selected_record["trade_type"] or "無"
                v_tax = selected_record["tax_id"] or "無統編"
                v_contact = selected_record["contact_person"] or "無聯絡人"
                v_phone = selected_record["phone"] or "無聯絡電話"
                v_rating_stars = "⭐" * int(selected_record["rating"] or 5)
                
                st.markdown(f"""
                <div style="background: white; border: 1px solid #cbd5e1; border-radius: 8px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 6px solid #2563eb;">
                    <h4 style="margin-top:0; color:#1e3a8a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">🏢 供應廠商聯絡與對帳資訊</h4>
                    <p style="margin: 8px 0; font-size:1.15em; font-weight:700; color:#0f172a;">{v_name}</p>
                    <p style="margin: 6px 0;"><strong>工種分類：</strong> <span style="background:#e0f2fe; color:#0369a1; padding: 2px 6px; border-radius:4px; font-weight:600;">{v_trade}</span></p>
                    <p style="margin: 6px 0;"><strong>統一編號：</strong> <code style="font-size:1em; color:#334155;">{v_tax}</code></p>
                    <p style="margin: 6px 0;"><strong>廠商窗口聯絡人：</strong> <span style="color:#0f172a; font-weight:600;">{v_contact}</span></p>
                    <p style="margin: 6px 0;"><strong>業務聯繫電話：</strong> <a href="tel:{v_phone}" style="color:#2563eb; font-weight:600; text-decoration:none;">📞 {v_phone}</a></p>
                    <p style="margin: 6px 0;"><strong>配合品質評價：</strong> <span style="font-size:1.1em;">{v_rating_stars}</span></p>
                    <div style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 6px; font-size: 0.85rem; color: #64748b; border: 1px dashed #cbd5e1;">
                        💡 <strong>品管對帳備忘：</strong> 請依台灣公共工程驗收規範，核對預拌混凝土抗壓試驗報告（7天與28天報告）、質保單與出廠發票，確認合規後即可變更為「已請款」。
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("尚無進貨單據資料。")


# =========================================================================
# 分頁四：日常行政零用金與機具租借
# =========================================================================
with tab4:
    st.subheader("🛠️ 工地日常行政零用金與機具儀器借還管制")
    st.caption("分開控管工地日常行政零用金支出，以及坍度試驗組、抗壓試體模具、夯實機等重要施工試驗機具租借管制。")
    
    # 1. 數據指標
    total_petty = database.get_petty_cash_total()
    borrowed_tools = database.get_borrowed_equipment()
    all_admin = database.get_all_admin_records()
    total_tools_count = sum(1 for a in all_admin if a["category"] == "機具租借")
    returned_tools_count = sum(1 for a in all_admin if a["category"] == "機具租借" and a["status"] in ["已歸還", "歸還"])
    
    ad_m1, ad_m2, ad_m3, ad_m4 = st.columns(4)
    with ad_m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">零用金累計支出總額</div>
            <div class="metric-value">NT$ {total_petty:,.0f}</div>
            <div class="metric-subtitle">工地便當、水電五金急用雜支</div>
        </div>
        """, unsafe_allow_html=True)
    with ad_m2:
        st.markdown(f"""
        <div class="metric-card {'warning' if borrowed_tools else 'success'}">
            <div class="metric-title">目前借出中未歸還機具</div>
            <div class="metric-value" style="color: {'#dc2626' if borrowed_tools else '#16a34a'};">{len(borrowed_tools)} <span style="font-size:1rem; font-weight:normal;">件</span></div>
            <div class="metric-subtitle">{'⚠️ 現場尚有机具儀器未歸還' if borrowed_tools else '✅ 所有儀器機具均已入庫'}</div>
        </div>
        """, unsafe_allow_html=True)
    with ad_m3:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="metric-title">機具歷史已歸還紀錄</div>
            <div class="metric-value">{returned_tools_count} <span style="font-size:1rem; font-weight:normal;">次</span></div>
            <div class="metric-subtitle">試驗儀器與工具如期歸還</div>
        </div>
        """, unsafe_allow_html=True)
    with ad_m4:
        petty_records_count = sum(1 for a in all_admin if a["category"] == "行政零用金")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">行政零用金登錄筆數</div>
            <div class="metric-value">{petty_records_count} <span style="font-size:1rem; font-weight:normal;">筆</span></div>
            <div class="metric-subtitle">發票與收據登記憑證</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # 2. 專題區塊：目前「借出中未歸還」機具清單與一鍵快速歸還功能
    st.markdown("#### 🚨 現場「借出中未歸還」機具與試驗儀器管制清單（支援一鍵歸還）")
    
    if borrowed_tools:
        st.markdown(f"""
        <div style="background-color: #fffbeb; border: 1px solid #fcd34d; border-left: 6px solid #f59e0b; padding: 12px 16px; border-radius: 6px; margin-bottom: 14px; color: #92400e;">
            <strong>⚠️ 借出機具儀器提醒：</strong> 目前共有 <strong>{len(borrowed_tools)}</strong> 件施工機具或品管試驗儀器登記為借出中，請落實清點與儀器保養：
        </div>
        """, unsafe_allow_html=True)
        
        # 逐筆卡片呈現，並提供一鍵歸還按鈕
        for tool in borrowed_tools:
            t_col1, t_col2, t_col3 = st.columns([3, 2, 1.2])
            with t_col1:
                st.markdown(f"**🛠️ {tool['item_name']}** (`{tool['record_id']}`)")
                p_text = f"出借人員：**{tool['person_name']}** | " if tool.get("person_name") else ""
                st.caption(f"{p_text}借用日期：{tool['date']} | 備註說明：{tool['notes'] or '無備註'}")
            with t_col2:
                st.markdown(f"**支出金額或出借數量：** `{tool['amount_or_borrower']}`")
                st.markdown(f'<span class="badge-borrowed">{tool["status"]}</span>', unsafe_allow_html=True)
            with t_col3:
                st.write("")
                if st.button("✅ 一鍵變更歸還", key=f"quick_return_{tool['record_id']}", use_container_width=True):
                    database.quick_return_equipment(tool["record_id"])
                    st.toast(f"{tool['item_name']} 已成功登記為「歸還」！", icon="🎉")
                    st.success(f"{tool['item_name']} 已歸還！")
                    st.rerun()
            st.divider()
    else:
        st.success("🎉 太棒了！目前現場所有機具、坍度試驗組、試體模具皆已歸還儀器室，無任何未歸還物件。")
        
    st.write("")
    
    # 3. 日常行政與機具全部紀錄清單與篩選
    st.markdown("#### 📋 日常行政零用金與機具租借總表")
    ad_f1, ad_f2, ad_f3 = st.columns([1.5, 1.5, 2])
    with ad_f1:
        sel_admin_cat = st.selectbox("類別篩選", ["全部", "機具租借", "行政零用金"], key="sel_ad_cat")
    with ad_f2:
        sel_admin_status = st.selectbox("狀態篩選", ["全部", "借出", "歸還", "未核銷", "已核銷"], key="sel_ad_stat")
    with ad_f3:
        ad_kw = st.text_input("🔍 關鍵字搜尋（編號/項目/金額/借用人/備註）", key="ad_kw")
        
    filtered_admin = database.get_all_admin_records(
        category=sel_admin_cat if sel_admin_cat != "全部" else None,
        status=sel_admin_status if sel_admin_status != "全部" else None,
        keyword=ad_kw
    )
    
    if filtered_admin:
        ad_rows = []
        for a in filtered_admin:
            if a["status"] in ["已核銷", "已歸還", "歸還"]:
                s_badge = f'<span style="background:#dcfce7; color:#166534; padding:2px 8px; border-radius:4px; font-weight:600;">{a["status"]}</span>'
            elif a["status"] in ["借出中", "借出"]:
                s_badge = f'<span style="background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:4px; font-weight:600;">{a["status"]}</span>'
            else:
                s_badge = f'<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:4px; font-weight:600;">{a["status"]}</span>'
                
            cat_badge = '<span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:600;">💰 零用金</span>' if a["category"] == "行政零用金" else '<span style="background:#f1f5f9; color:#334155; padding:2px 6px; border-radius:4px; font-weight:600;">🔧 機具</span>'
            
            ad_rows.append({
                "紀錄編號": f"<code>{a['record_id']}</code>",
                "登記日期": a["date"],
                "類別": cat_badge,
                "項目名稱": f"<strong>{a['item_name']}</strong>",
                "支出或出借人員": f"<strong>{a['person_name']}</strong>" if a.get("person_name") else "<span style='color:#94a3b8;'>-</span>",
                "支出金額或出借數量": a["amount_or_borrower"],
                "核銷狀態": s_badge,
                "備註說明": a["notes"] or "-"
            })
        render_civil_table(pd.DataFrame(ad_rows))
    else:
        st.info("查無符合條件之行政與機具紀錄。")
        
    st.divider()
    
    # 4. 行政與機具紀錄 CRUD 管理表單
    st.markdown("#### ⚙️ 日常行政與機具登記管理 (CRUD)")
    ad_tab1, ad_tab2, ad_tab3 = st.tabs(["➕ 新增登記紀錄", "✏️ 編輯既有紀錄", "🗑️ 刪除登記紀錄"])
    
    with ad_tab1:
        st.caption("填寫表單以登記現場機具租借管制或行政零用金收支：")
        all_ad_raw = database.get_all_admin_records()
        next_ad_id = f"ADM-{datetime.now().strftime('%Y%m%d')}-{len(all_ad_raw)+1:03d}"
        
        col_ad1, col_ad2 = st.columns(2)
        with col_ad1:
            new_ad_id = st.text_input("紀錄編號*", value=next_ad_id, key="tab4_new_ad_id")
            new_ad_date = st.date_input("登記日期*", value=date.today(), key="tab4_new_ad_date")
            new_ad_cat = st.selectbox("登記類別*", ["機具租借", "行政零用金"], key="tab4_new_ad_cat")
            
            # 依登記類別動態切換項目名稱選單
            if new_ad_cat == "機具租借":
                preset_items = ["夯實機", "抗壓試體模具組", "坍度試驗組", "發電機", "高壓清洗機", "雷射水準儀", "沉水式抽水馬達", "自訂其他機具"]
            else:
                preset_items = ["工地便當費", "五金耗材", "勞安防護用具", "臨時工資", "飲用水與茶水費", "油資雜支", "自訂其他費用"]
                
            selected_preset = st.selectbox("項目名稱*", preset_items, key=f"tab4_new_ad_item_{new_ad_cat}")
            if "自訂" in selected_preset:
                custom_item_name = st.text_input("請輸入自訂項目名稱*", placeholder="如：水質檢測儀器", key="tab4_custom_item")
                final_item_name = custom_item_name.strip()
            else:
                final_item_name = selected_preset
                
        with col_ad2:
            new_ad_person = st.text_input(
                "支出或出借人員姓名*",
                placeholder="如：林品管師 (品管組)、陳工頭 (土方組)、張會計",
                key="tab4_new_ad_person"
            )
            new_ad_ab = st.text_input(
                "支出金額或出借數量*", 
                placeholder="如：1 台 / 2 組 (出借數量) 或 3600 (支出金額)", 
                key="tab4_new_ad_ab"
            )
            
            # 核銷狀態：增加「借出」、「歸還」
            if new_ad_cat == "機具租借":
                status_choices = ["借出", "歸還", "未核銷", "已核銷"]
            else:
                status_choices = ["未核銷", "已核銷", "借出", "歸還"]
                
            new_ad_status = st.selectbox("核銷狀態*", status_choices, key=f"tab4_new_ad_status_{new_ad_cat}")
            new_ad_notes = st.text_area("備註說明 (工程用途、借用人姓名與組別、試體編號、發票號碼等)", key="tab4_new_ad_notes")
            
        st.write("")
        if st.button("💾 新增登記資料", type="primary", use_container_width=True, key="btn_add_admin_rec"):
            if not new_ad_id or not final_item_name or not new_ad_ab:
                st.error("請確認填寫紀錄編號、項目名稱以及「支出金額或出借數量」！")
            else:
                try:
                    database.add_admin_record({
                        "record_id": new_ad_id.strip(),
                        "date": str(new_ad_date),
                        "category": new_ad_cat,
                        "item_name": final_item_name.strip(),
                        "person_name": new_ad_person.strip(),
                        "amount_or_borrower": new_ad_ab.strip(),
                        "status": new_ad_status,
                        "notes": new_ad_notes.strip()
                    })
                    st.success(f"登記紀錄 {new_ad_id}（{final_item_name}）已成功建檔！")
                    st.rerun()
                except Exception as e:
                    st.error(f"新增登記失敗：{e}")
                        
    with ad_tab2:
        if all_admin:
            ad_edit_choices = [f"{a['record_id']} | {a['category']} | {a['item_name']} ({a['status']})" for a in all_admin]
            sel_ad_edit_label = st.selectbox("選擇欲修改之紀錄", ad_edit_choices, key="sel_ad_edit")
            sel_ad_id = sel_ad_edit_label.split(" | ")[0]
            curr_ad = next((a for a in all_admin if a["record_id"] == sel_ad_id), None)
            
            if curr_ad:
                col_ead1, col_ead2 = st.columns(2)
                with col_ead1:
                    st.text_input("紀錄編號 (不可修改)", value=curr_ad["record_id"], disabled=True)
                    edit_ad_date = st.date_input("登記日期", value=datetime.strptime(curr_ad["date"], "%Y-%m-%d").date(), key="edit_ad_date")
                    cats = ["機具租借", "行政零用金"]
                    c_idx = cats.index(curr_ad["category"]) if curr_ad["category"] in cats else 0
                    edit_ad_cat = st.selectbox("類別", cats, index=c_idx, key="edit_ad_cat")
                    edit_ad_item = st.text_input("項目名稱", value=curr_ad["item_name"], key="edit_ad_item")
                with col_ead2:
                    edit_ad_person = st.text_input("支出或出借人員姓名", value=curr_ad.get("person_name", "") or "", key="edit_ad_person")
                    edit_ad_ab = st.text_input("支出金額或出借數量", value=curr_ad["amount_or_borrower"], key="edit_ad_ab")
                    statuses = ["借出", "歸還", "未核銷", "已核銷", "借出中", "已歸還"]
                    s_idx = statuses.index(curr_ad["status"]) if curr_ad["status"] in statuses else 0
                    edit_ad_status = st.selectbox("核銷狀態", statuses, index=s_idx, key="edit_ad_status")
                    edit_ad_notes = st.text_area("備註說明", value=curr_ad["notes"] or "", key="edit_ad_notes")
                    
                st.write("")
                if st.button("📝 儲存登記修改", type="primary", use_container_width=True, key="btn_edit_admin_rec"):
                    try:
                        database.update_admin_record(curr_ad["record_id"], {
                            "date": str(edit_ad_date),
                            "category": edit_ad_cat,
                            "item_name": edit_ad_item.strip(),
                            "person_name": edit_ad_person.strip(),
                            "amount_or_borrower": edit_ad_ab.strip(),
                            "status": edit_ad_status,
                            "notes": edit_ad_notes.strip()
                        })
                        st.success(f"紀錄 {curr_ad['record_id']} 資料已更新！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"更新失敗：{e}")
        else:
            st.info("尚無紀錄可供修改。")
            
    with ad_tab3:
        if all_admin:
            ad_del_choices = [f"{a['record_id']} | {a['category']} | {a['item_name']} | {a['amount_or_borrower']} ({a['status']})" for a in all_admin]
            sel_ad_del_label = st.selectbox("選擇欲刪除之登記紀錄", ad_del_choices, key="sel_ad_del")
            sel_ad_del_id = sel_ad_del_label.split(" | ")[0]
            
            st.warning(f"⚠️ 確認要刪除登記紀錄「{sel_ad_del_label}」？")
            if st.button("🗑️ 確認永久刪除此筆紀錄", type="primary", key="btn_del_ad"):
                database.delete_admin_record(sel_ad_del_id)
                st.success(f"紀錄 {sel_ad_del_id} 已成功刪除！")
                st.rerun()
        else:
            st.info("尚無登記紀錄。")
