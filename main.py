import streamlit as st
import pandas as pd
import json
import base64
import uuid
from datetime import datetime, timezone, timedelta
import os
import gspread
from google.oauth2.service_account import Credentials

# 設定台灣時區
TAIWAN_TZ = timezone(timedelta(hours=8))

# Google Sheets 設定
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheets_client():
    """取得 Google Sheets 客戶端"""
    try:
        # 從 Streamlit secrets 讀取服務帳號資訊
        service_account_info = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        credentials = Credentials.from_service_account_info(
            service_account_info, scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"無法連接到 Google Sheets: {e}")
        return None

def get_google_sheet():
    """取得指定的 Google Sheet"""
    try:
        client = get_google_sheets_client()
        if not client:
            return None
        
        # 從 secrets 取得 spreadsheet URL
        spreadsheet_url = st.secrets["spreadsheet"]
        # 從 URL 中提取 spreadsheet ID
        spreadsheet_id = spreadsheet_url.split('/d/')[1].split('/')[0]
        
        # 開啟 spreadsheet
        sheet = client.open_by_key(spreadsheet_id)
        return sheet
    except Exception as e:
        st.error(f"無法取得 Google Sheet: {e}")
        return None

def get_taiwan_time():
    """取得台灣時間"""
    return datetime.now(TAIWAN_TZ)

# 添加快取裝飾器
@st.cache_data
def get_material_options(materials_dict):
    """快取材料選項列表，避免重複計算"""
    return list(materials_dict.keys())

# 載入自訂類別
def load_custom_categories():
    if os.path.exists('custom_categories.json'):
        try:
            with open('custom_categories.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"載入自訂類別時發生錯誤：{e}")
            return ["食材", "設備", "包裝", "運輸", "食譜", "其他"]
    return ["食材", "設備", "包裝", "運輸", "食譜", "其他"]

# 設定頁面配置
st.set_page_config(
    page_title="🩵MEAT BOBO💙",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# # 奶油色主題（全區塊無白色）
# st.markdown("""
# <style>
#     body, .stApp {
#         background: #f6edd9 !important;
#     }
#     .main-header {
#         color: #a67c52;
#         text-align: center;
#         margin-bottom: 1.5rem;
#     }
#     .main-header h1 {
#         color: #a67c52;
#         font-size: 2rem;
#         font-weight: 700;
#         margin-bottom: 0.2rem;
#     }
#     .main-header p {
#         color: #bfa77a;
#         font-size: 1.1rem;
#         margin-bottom: 0.5rem;
#     }
#     .stButton > button {
#         background: #d4a574 !important;
#         color: white !important;
#         border-radius: 16px !important;
#         font-weight: 600 !important;
#         border: none !important;
#     }
#     .stButton > button:hover {
#         background: #c19a6b !important;
#     }
#     .stTextInput > div > div > input,
#     .stNumberInput > div > div > input,
#     .stSelectbox > div > div {
#         background: #f3e9ce !important;
#         border-radius: 10px !important;
#         border: 1.5px solid #e6d7c3 !important;
#         color: #7c6846 !important;
#     }
#     .stDataFrame, .stForm, .stMetric, .stExpander, .stAlert, .stMarkdown, .stContainer, .stColumn {
#         background: #f3e9ce !important;
#         border-radius: 10px !important;
#         color: #7c6846 !important;
#     }
# </style>
# """, unsafe_allow_html=True)




# 初始化 session state
if 'saved_materials' not in st.session_state:
    st.session_state.saved_materials = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "成本計算"
if 'saved_recipes' not in st.session_state:
    st.session_state.saved_recipes = {}
if 'selected_materials' not in st.session_state:
    st.session_state.selected_materials = []
if 'material_weights' not in st.session_state:
    st.session_state.material_weights = {}
if 'material_yield_rates' not in st.session_state:
    st.session_state.material_yield_rates = {}
if 'show_save_success' not in st.session_state:
    st.session_state.show_save_success = False
if 'saved_recipe_name' not in st.session_state:
    st.session_state.saved_recipe_name = ""
if 'accounting_records' not in st.session_state:
    st.session_state.accounting_records = []
if 'watermark_position' not in st.session_state:
    st.session_state.watermark_position = "bottom-right"
if 'materials_expander_expanded' not in st.session_state:
    st.session_state.materials_expander_expanded = False
if 'custom_categories' not in st.session_state:
    st.session_state.custom_categories = load_custom_categories()
if 'show_clear_confirm' not in st.session_state:
    st.session_state.show_clear_confirm = False
if 'editing_material' not in st.session_state:
    st.session_state.editing_material = None
if 'editing_price' not in st.session_state:
    st.session_state.editing_price = None
if 'material_input_key' not in st.session_state:
    st.session_state.material_input_key = 0
if 'price_input_key' not in st.session_state:
    st.session_state.price_input_key = 0
if 'starred_materials' not in st.session_state:
    st.session_state.starred_materials = set()
if 'accounting_form_key' not in st.session_state:
    st.session_state.accounting_form_key = 0
if 'editing_record' not in st.session_state:
    st.session_state.editing_record = None

if 'recipe_expander_states' not in st.session_state:
    st.session_state.recipe_expander_states = {}

# 載入已儲存的材料資料
def load_saved_materials():
    try:
        # 嘗試從 Google Sheets 載入
        sheet = get_google_sheet()
        if sheet:
            # 嘗試取得材料工作表
            try:
                worksheet = sheet.worksheet("材料")
            except:
                # 如果不存在，創建新的
                worksheet = sheet.add_worksheet(title="材料", rows=1000, cols=10)
                # 寫入標題
                worksheet.append_row(['材料名稱', '單價', '更新時間'])
            
            # 讀取資料
            data = worksheet.get_all_records()
            materials = {}
            
            for row in data:
                if row.get('材料名稱') and row.get('單價') is not None:
                    try:
                        price = float(row['單價'])
                        materials[row['材料名稱']] = price
                    except ValueError:
                        continue
            
            return materials
    except Exception as e:
        st.error(f"從 Google Sheets 載入材料資料時發生錯誤：{e}")
    
    # 如果 Google Sheets 失敗，嘗試從本地檔案載入
    if os.path.exists('saved_materials.json'):
        try:
            with open('saved_materials.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 檢查是否為舊格式的 base64 編碼
                if isinstance(data, dict) and 'encoded_data' in data:
                    try:
                        encoded_str = data['encoded_data']
                        decoded_bytes = base64.b64decode(encoded_str)
                        decoded_str = decoded_bytes.decode('utf-8')
                        return json.loads(decoded_str)
                    except:
                        # 如果解碼失敗，刪除檔案重新開始
                        os.remove('saved_materials.json')
                        return {}
                # 直接返回資料（新格式）
                return data
        except Exception as e:
            st.error(f"載入材料資料時發生錯誤：{e}")
            try:
                os.remove('saved_materials.json')
            except:
                pass
            return {}
    return {}


# 儲存材料資料
def save_materials_data():
    try:
        # 嘗試儲存到 Google Sheets
        sheet = get_google_sheet()
        if sheet:
            # 嘗試取得材料工作表
            try:
                worksheet = sheet.worksheet("材料")
            except:
                # 如果不存在，創建新的
                worksheet = sheet.add_worksheet(title="材料", rows=1000, cols=10)
                # 寫入標題
                worksheet.append_row(['材料名稱', '單價', '更新時間'])
            
            # 清空現有資料
            worksheet.clear()
            
            # 寫入標題
            worksheet.append_row(['材料名稱', '單價', '更新時間'])
            
            # 寫入資料
            for material, price in st.session_state.saved_materials.items():
                worksheet.append_row([
                    material, 
                    price, 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
            
            st.success("✅ 資料已同步到 Google Sheets")
            return
    except Exception as e:
        st.error(f"儲存到 Google Sheets 時發生錯誤：{e}")
    
    # 如果 Google Sheets 失敗，儲存到本地檔案
    try:
        with open('saved_materials.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.saved_materials, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存材料資料時發生錯誤：{e}")

 
# 載入已儲存的食譜資料
def load_saved_recipes():
    try:
        # 嘗試從 Google Sheets 載入
        sheet = get_google_sheet()
        if sheet:
            # 嘗試取得食譜工作表
            try:
                worksheet = sheet.worksheet("食譜")
            except:
                # 如果不存在，創建新的
                worksheet = sheet.add_worksheet(title="食譜", rows=1000, cols=20)
                # 寫入標題
                worksheet.append_row(['食譜名稱', '材料', '總成本', '創建時間'])
            
            # 讀取資料
            data = worksheet.get_all_records()
            recipes = {}
            
            for row in data:
                if row.get('食譜名稱'):
                    recipe_name = row['食譜名稱']
                    try:
                        # 解析材料資料（假設存儲為 JSON 字串）
                        materials_str = row.get('材料', '{}')
                        materials = json.loads(materials_str) if materials_str else {}
                        
                        recipes[recipe_name] = {
                            "materials": materials,
                            "total_cost": float(row.get('總成本', 0)),
                            "created_at": row.get('創建時間', datetime.now().isoformat())
                        }
                    except Exception as e:
                        st.warning(f"解析食譜 {recipe_name} 時發生錯誤：{e}")
                        continue
            
            return recipes
    except Exception as e:
        st.error(f"從 Google Sheets 載入食譜資料時發生錯誤：{e}")
    
    # 如果 Google Sheets 失敗，嘗試從本地檔案載入
    if os.path.exists('saved_recipes.json'):
        try:
            with open('saved_recipes.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"載入食譜資料時發生錯誤：{e}")
            try:
                os.remove('saved_recipes.json')
            except:
                pass
            return {}
    return {}


# 儲存食譜資料
def save_recipes_data():
    try:
        # 嘗試儲存到 Google Sheets
        sheet = get_google_sheet()
        if sheet:
            # 嘗試取得食譜工作表
            try:
                worksheet = sheet.worksheet("食譜")
            except:
                # 如果不存在，創建新的
                worksheet = sheet.add_worksheet(title="食譜", rows=1000, cols=20)
                # 寫入標題
                worksheet.append_row(['食譜名稱', '材料', '總成本', '創建時間'])
            
            # 清空現有資料
            worksheet.clear()
            
            # 寫入標題
            worksheet.append_row(['食譜名稱', '材料', '總成本', '創建時間'])
            
            # 寫入資料
            for recipe_name, recipe_data in st.session_state.saved_recipes.items():
                worksheet.append_row([
                    recipe_name,
                    json.dumps(recipe_data['materials'], ensure_ascii=False),
                    recipe_data['total_cost'],
                    recipe_data['created_at']
                ])
            
            st.success("✅ 食譜資料已同步到 Google Sheets")
            return
    except Exception as e:
        st.error(f"儲存食譜到 Google Sheets 時發生錯誤：{e}")
    
    # 如果 Google Sheets 失敗，儲存到本地檔案
    try:
        with open('saved_recipes.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.saved_recipes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存食譜資料時發生錯誤：{e}")


# 載入記帳資料
def load_accounting_data():
    try:
        # 嘗試從 Google Sheets 載入
        sheet = get_google_sheet()
        if sheet:
            # 嘗試取得記帳工作表
            try:
                worksheet = sheet.worksheet("記帳")
            except:
                # 如果不存在，創建新的
                worksheet = sheet.add_worksheet(title="記帳", rows=1000, cols=15)
                # 寫入標題
                worksheet.append_row([
                    'ID', '日期', '類型', '類別', '細項', '金額', 
                    '地點', '購買人', '產品', '備註', '創建時間'
                ])
            
            # 讀取資料
            data = worksheet.get_all_records()
            records = []
            
            for row in data:
                if row.get('ID'):
                    try:
                        record = {
                            "id": row['ID'],
                            "date": row.get('日期', ''),
                            "type": row.get('類型', ''),
                            "category": row.get('類別', ''),
                            "description": row.get('細項', ''),
                            "amount": float(row.get('金額', 0)),
                            "location": row.get('地點', ''),
                            "buyer": row.get('購買人', ''),
                            "product": row.get('產品', ''),
                            "remark": row.get('備註', ''),
                            "created_at": row.get('創建時間', datetime.now().isoformat())
                        }
                        records.append(record)
                    except Exception as e:
                        st.warning(f"解析記帳記錄時發生錯誤：{e}")
                        continue
            
            return records
    except Exception as e:
        st.error(f"從 Google Sheets 載入記帳資料時發生錯誤：{e}")
    
    # 如果 Google Sheets 失敗，嘗試從本地檔案載入
    if os.path.exists('accounting_records.json'):
        try:
            with open('accounting_records.json', 'r', encoding='utf-8') as f:
                records = json.load(f)
                # 為舊記錄添加ID
                for record in records:
                    if 'id' not in record:
                        record['id'] = str(uuid.uuid4())
                return records
        except Exception as e:
            st.error(f"載入記帳資料時發生錯誤：{e}")
            try:
                os.remove('accounting_records.json')
            except:
                pass
            return []
    return []


# 儲存記帳資料
def save_accounting_data():
    try:
        # 嘗試儲存到 Google Sheets
        sheet = get_google_sheet()
        if sheet:
            # 嘗試取得記帳工作表
            try:
                worksheet = sheet.worksheet("記帳")
            except:
                # 如果不存在，創建新的
                worksheet = sheet.add_worksheet(title="記帳", rows=1000, cols=15)
                # 寫入標題
                worksheet.append_row([
                    'ID', '日期', '類型', '類別', '細項', '金額', 
                    '地點', '購買人', '產品', '備註', '創建時間'
                ])
            
            # 清空現有資料
            worksheet.clear()
            
            # 寫入標題
            worksheet.append_row([
                'ID', '日期', '類型', '類別', '細項', '金額', 
                '地點', '購買人', '產品', '備註', '創建時間'
            ])
            
            # 寫入資料
            for record in st.session_state.accounting_records:
                worksheet.append_row([
                    record.get('id', ''),
                    record.get('date', ''),
                    record.get('type', ''),
                    record.get('category', ''),
                    record.get('description', ''),
                    record.get('amount', 0),
                    record.get('location', ''),
                    record.get('buyer', ''),
                    record.get('product', ''),
                    record.get('remark', ''),
                    record.get('created_at', '')
                ])
            
            st.success("✅ 記帳資料已同步到 Google Sheets")
            return
    except Exception as e:
        st.error(f"儲存記帳資料到 Google Sheets 時發生錯誤：{e}")
    
    # 如果 Google Sheets 失敗，儲存到本地檔案
    try:
        with open('accounting_records.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.accounting_records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存記帳資料時發生錯誤：{e}")

# 儲存自訂類別
def save_custom_categories():
    try:
        # 嘗試儲存到 Google Sheets
        sheet = get_google_sheet()
        if sheet:
            # 嘗試取得設定工作表
            try:
                worksheet = sheet.worksheet("設定")
            except:
                # 如果不存在，創建新的
                worksheet = sheet.add_worksheet(title="設定", rows=100, cols=10)
                # 寫入標題
                worksheet.append_row(['類別名稱'])
            
            # 清空現有資料
            worksheet.clear()
            
            # 寫入標題
            worksheet.append_row(['類別名稱'])
            
            # 寫入類別
            for category in st.session_state.custom_categories:
                worksheet.append_row([category])
            
            st.success("✅ 類別設定已同步到 Google Sheets")
            return
    except Exception as e:
        st.error(f"儲存類別設定到 Google Sheets 時發生錯誤：{e}")
    
    # 如果 Google Sheets 失敗，儲存到本地檔案
    try:
        with open('custom_categories.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.custom_categories, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存自訂類別時發生錯誤：{e}")


# 載入已儲存的材料
if not st.session_state.saved_materials:
    st.session_state.saved_materials = load_saved_materials()


# 載入已儲存的食譜
if not st.session_state.saved_recipes:
    st.session_state.saved_recipes = load_saved_recipes()

# 載入記帳資料
if not st.session_state.accounting_records:
    st.session_state.accounting_records = load_accounting_data()

# 標題
st.markdown("""
<div class="main-header">
    <h1>🩵MEAT BOBO💙</h1>
</div>
""", unsafe_allow_html=True)

# 主要容器
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 側邊欄 - 功能選單
with st.sidebar:
    st.markdown('<div class="sidebar-container">', unsafe_allow_html=True)
    st.markdown("### 功能選單")
    
    # 直接顯示功能按鈕
    if st.button("💰 成本計算", use_container_width=True, type="primary" if st.session_state.current_page == "成本計算" else "secondary"):
        st.session_state.current_page = "成本計算"
        st.rerun()
    
    if st.button("📦 材料管理", use_container_width=True, type="primary" if st.session_state.current_page == "材料管理" else "secondary"):
        st.session_state.current_page = "材料管理"
        st.rerun()
    
    if st.button("📖 食譜區", use_container_width=True, type="primary" if st.session_state.current_page == "食譜區" else "secondary"):
        st.session_state.current_page = "食譜區"
        st.rerun()
    
    if st.button("📊 記帳區", use_container_width=True, type="primary" if st.session_state.current_page == "記帳區" else "secondary"):
        st.session_state.current_page = "記帳區"
        st.rerun()
    
    st.markdown("---")
    
    # 資料匯出功能
    st.markdown("### 📤 資料匯出")
    if st.button("📥 下載所有資料", key="download_btn", use_container_width=True):
        # 準備下載資料
        download_data = {
            "materials": st.session_state.saved_materials,
            "recipes": st.session_state.saved_recipes,
            "accounting": st.session_state.accounting_records
        }
        
        # 轉換為 JSON 字串
        import json
        json_str = json.dumps(download_data, ensure_ascii=False, indent=2)
        
        # 提供下載
        st.download_button(
            label="💾 下載資料檔案",
            data=json_str,
            file_name="streamlit_data_backup.json",
            mime="application/json"
        )
    
    # 資料匯入功能
    st.markdown("### 📥 資料匯入")
    uploaded_file = st.file_uploader(
        "選擇要匯入的資料檔案",
        type=['json'],
        key="upload_data"
    )
    
    if uploaded_file is not None:
        try:
            # 讀取上傳的檔案
            import json
            uploaded_data = json.load(uploaded_file)
            
            # 更新 session state
            if 'materials' in uploaded_data:
                st.session_state.saved_materials = uploaded_data['materials']
                save_materials_data()
            
            if 'recipes' in uploaded_data:
                st.session_state.saved_recipes = uploaded_data['recipes']
                save_recipes_data()
            
            if 'accounting' in uploaded_data:
                st.session_state.accounting_records = uploaded_data['accounting']
                save_accounting_data()
            
            st.success("✅ 資料匯入成功！")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ 匯入失敗：{e}")
    
    # Google Sheets 同步功能
    st.markdown("---")
    st.markdown("### 🔄 Google Sheets 同步")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📤 上傳到 Google Sheets", use_container_width=True):
            try:
                save_materials_data()
                save_recipes_data()
                save_accounting_data()
                save_custom_categories()
                st.success("✅ 所有資料已同步到 Google Sheets")
            except Exception as e:
                st.error(f"同步失敗：{e}")
    
    with col2:
        if st.button("📥 從 Google Sheets 載入", use_container_width=True):
            try:
                st.session_state.saved_materials = load_saved_materials()
                st.session_state.saved_recipes = load_saved_recipes()
                st.session_state.accounting_records = load_accounting_data()
                st.session_state.custom_categories = load_custom_categories()
                st.success("✅ 已從 Google Sheets 載入所有資料")
                st.rerun()
            except Exception as e:
                st.error(f"載入失敗：{e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 根據選擇的頁面顯示不同內容
if st.session_state.current_page == "成本計算":
    # 成本計算頁面
    st.markdown("### 成本計算", help="選擇多個材料並計算總成本")
    
    # 多材料選擇介面
    if st.session_state.saved_materials:
        # 預先計算材料列表，避免重複計算
        material_options = get_material_options(st.session_state.saved_materials)
        
        st.markdown("#### 選擇材料（可多選）")
        
        # 使用複選框選擇材料
        selected_materials = []
        
        # 創建兩列佈局來顯示材料選項
        col1, col2 = st.columns(2)
        
        for i, material in enumerate(material_options):
            # 交替分配到兩列
            with col1 if i % 2 == 0 else col2:
                # 檢查是否已選中
                is_selected = material in st.session_state.selected_materials

                # 使用複選框
                price_display = st.session_state.saved_materials[material]
                if price_display is not None and price_display == int(price_display):
                    price_display = int(price_display)

                # 使用安全的key，避免特殊符號問題
                safe_key = f"checkbox_{hash(material) % 1000000}"
                # 安全地顯示材料名稱，避免特殊符號問題
                import html
                import re
                # 使用更安全的字符串處理，特別處理 $ 符號
                safe_material_name = material.replace('$', '＄')  # 使用全形美元符號
                safe_material_name = html.escape(safe_material_name)
                if st.checkbox(
                    f"{safe_material_name} (NT$ {price_display}/g)",
                    value=is_selected,
                    key=safe_key
                ):
                    selected_materials.append(material)

        # 更新session state
        st.session_state.selected_materials = selected_materials

        # 快速操作按鈕
        if material_options:
            st.markdown("---")
            col_select_all, col_clear_all, col_selected_count = st.columns(3)

            with col_select_all:
                if st.button("全選", use_container_width=True, key="select_all_btn"):
                    if st.session_state.selected_materials == material_options:
                        st.info("✅ 已經是全選狀態")
                    else:
                        st.session_state.selected_materials = material_options.copy()
                        st.success("✅ 已全選所有材料")
                        st.rerun()

            with col_clear_all:
                # 檢查是否在確認清除狀態
                if st.session_state.get('show_clear_confirm', False):
                    st.warning("⚠️ 確定要清除所有選擇嗎？")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("確認清除", key="confirm_clear_all", use_container_width=True):
                            st.session_state.selected_materials = []
                            st.session_state.show_clear_confirm = False
                            st.success("✅ 已清除所有選擇")
                            st.rerun()
                    with col_cancel:
                        if st.button("取消", key="cancel_clear_all", use_container_width=True):
                            st.session_state.show_clear_confirm = False
                            st.info("❌ 已取消清除操作")
                            st.rerun()
                else:
                    if st.button("清除選擇", use_container_width=True, key="clear_all_btn"):
                        if not st.session_state.selected_materials:
                            st.info("✅ 已經沒有選擇任何材料")
                        else:
                            st.session_state.show_clear_confirm = True
                            st.rerun()

        if selected_materials:
            st.markdown("---")
            st.markdown("#### 材料重量輸入")

            # 為每個選中的材料創建重量輸入
            total_cost = 0
            recipe_materials = {}

            # 根據材料數量決定列數
            if len(selected_materials) <= 2:
                cols = st.columns(len(selected_materials))
            else:
                cols = st.columns(3)  # 最多3列
            
            for i, material in enumerate(selected_materials):
                price = st.session_state.saved_materials[material]
                col_index = i % len(cols)
                
                with cols[col_index]:
                    # 創建材料卡片
                    price_display = price
                    if price_display is not None and price_display == int(price_display):
                        price_display = int(price_display)
                    
                    # 安全地顯示材料名稱
                    import html
                    # 使用更安全的字符串處理，特別處理 $ 符號
                    safe_material_name = material.replace('$', '＄')  # 使用全形美元符號
                    safe_material_name = html.escape(safe_material_name)
                    
                    # 檢查是否為標記的材料，如果是則加上星號
                    is_starred = material in st.session_state.starred_materials
                    star_prefix = "⭐ " if is_starred else ""
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{star_prefix}{safe_material_name}</h4>
                        <p><strong>單價：</strong>NT$ {price_display} / 1g</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # 輸入克數
                    current_weight = st.session_state.material_weights.get(material, 0.0)
                    # 使用安全的key，避免特殊符號問題
                    safe_weight_key = f"weight_{hash(material) % 1000000}"
                    safe_yield_key = f"yield_rate_{hash(material) % 1000000}"
                    
                    weight = st.text_input(
                        f"{safe_material_name} 克數 (g)", 
                        value=str(current_weight) if current_weight > 0 else "",
                        key=safe_weight_key,
                        help=f"請輸入 {safe_material_name} 的重量（克）",
                        label_visibility="collapsed",
                        placeholder="克數"
                    )
                    
                    # 熟成率勾選（固定0.8）
                    current_yield_enabled = st.session_state.material_yield_rates.get(
                        material, False
                    )
                    yield_enabled = st.checkbox(
                        " 使用熟成率 (0.8)",
                        value=current_yield_enabled,
                        key=safe_yield_key,
                        help=f"勾選後 {safe_material_name} 將使用 0.8 的熟成率計算"
                    )
                    
                    # 轉換為數字
                    try:
                        weight = float(weight) if weight else 0.0
                    except ValueError:
                        weight = 0.0
                    
                    # 只在重量改變時更新session state
                    if weight != current_weight:
                        st.session_state.material_weights[material] = weight
                    
                    # 只在熟成率勾選狀態改變時更新session state
                    if yield_enabled != current_yield_enabled:
                        st.session_state.material_yield_rates[material] = yield_enabled
                    
                    # 計算單個材料成本（考慮熟成率）
                    if yield_enabled:
                        # 使用固定熟成率0.8計算：重量 / 0.8 * 單價
                        adjusted_weight = weight / 0.8
                        material_cost = adjusted_weight * price
                        yield_rate = 0.8
                    else:
                        # 原本的計算：重量 * 單價
                        material_cost = weight * price
                        yield_rate = None
                    
                    total_cost += material_cost
                    recipe_materials[material] = {
                        "weight": weight,
                        "price": price,
                        "cost": material_cost,
                        "yield_rate": yield_rate,
                        "adjusted_weight": weight / yield_rate if yield_rate is not None and yield_rate > 0 else weight
                    }



            # 檢查是否有輸入克數
            has_weight_input = any(st.session_state.material_weights.get(material, 0.0) > 0 for material in selected_materials)

            if not has_weight_input:
                st.error("⚠️ 請至少為一個材料輸入克數！")

            # 計算按鈕和食譜保存
            if st.button("計算總成本", type="primary", use_container_width=True):
                # 重新檢查是否有輸入克數（因為用戶可能在點擊按鈕前才輸入）
                current_has_weight = any(st.session_state.material_weights.get(material, 0.0) > 0 for material in selected_materials)
                if not current_has_weight:
                    st.error("⚠️ 請至少為一個材料輸入克數！")
                else:
                    st.success("✅ 開始計算總成本...")
                    # 顯示計算結果
                    st.markdown("---")
                    st.markdown("### 計算結果")
                    
                    # 顯示每個材料的詳細資訊
                    st.markdown("""
                    <style>
                    .small-metric {
                        font-size: 0.9em;
                    }
                    .small-metric .stMetric {
                        font-size: 0.9em;
                    }
                    .small-metric .stMetric [data-testid="metric-container"] {
                        font-size: 0.9em;
                    }
                    .small-metric .stMetric [data-testid="metric-container"] label {
                        font-size: 0.8em;
                    }
                    .small-metric .stMetric [data-testid="metric-container"] [data-testid="metric-value"] {
                        font-size: 0.9em;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
                    with st.container():
                        st.markdown('<div class="small-metric">', unsafe_allow_html=True)
                        for material, data in recipe_materials.items():
                            # 安全地顯示材料名稱
                            import html
                            # 使用更安全的字符串處理，特別處理 $ 符號
                            safe_material_name = material.replace('$', '＄')  # 使用全形美元符號
                            safe_material_name = html.escape(safe_material_name)
                            
                            # 檢查是否為標記的材料，如果是則加上星號
                            is_starred = material in st.session_state.starred_materials
                            star_prefix = "⭐ " if is_starred else ""
                            
                            # 如果有熟成率，顯示更多資訊
                            if data['yield_rate'] is not None and data['yield_rate'] > 0:
                                col1_result, col2_result, col3_result, col4_result, col5_result = st.columns(5)
                                with col1_result:
                                    st.metric("材料", f"{star_prefix}{safe_material_name}")
                                with col2_result:
                                    st.metric("重量", f"{data['weight']:.1f} g")
                                with col3_result:
                                    st.metric("熟成率", f"{data['yield_rate']:.2f}")
                                with col4_result:
                                    price_display = data['price']
                                    if price_display == int(price_display):
                                        price_display = int(price_display)
                                    st.metric("單價", f"NT$ {price_display}")
                                with col5_result:
                                    cost_display = data['cost']
                                    if cost_display == int(cost_display):
                                        cost_display = int(cost_display)
                                    else:
                                        cost_display = f"{data['cost']:.2f}"
                                    st.metric("成本", f"NT$ {cost_display}")
                                
                                # 顯示調整後的重量
                                st.markdown(f"**{star_prefix}{safe_material_name}** 調整後重量：{data['adjusted_weight']:.1f} g (原重量 ÷ 熟成率)")
                            else:
                                col1_result, col2_result, col3_result, col4_result = st.columns(4)
                                with col1_result:
                                    st.metric("材料", f"{star_prefix}{safe_material_name}")
                                with col2_result:
                                    st.metric("重量", f"{data['weight']:.1f} g")
                                with col3_result:
                                    price_display = data['price']
                                    if price_display == int(price_display):
                                        price_display = int(price_display)
                                    st.metric("單價", f"NT$ {price_display}")
                                with col4_result:
                                    cost_display = data['cost']
                                    if cost_display == int(cost_display):
                                        cost_display = int(cost_display)
                                    else:
                                        cost_display = f"{data['cost']:.2f}"
                                    st.metric("成本", f"NT$ {cost_display}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    total_cost_display = total_cost
                    if total_cost_display == int(total_cost_display):
                        total_cost_display = int(total_cost_display)
                    else:
                        total_cost_display = f"{total_cost:.2f}"
                    st.markdown(f"### 總計：NT$ {total_cost_display}")
            
            # 食譜保存部分（始終顯示）
            if total_cost > 0:
                st.markdown("---")
                st.markdown("### 保存食譜")
                
                recipe_name = st.text_input(
                    "食譜名稱",
                    placeholder="例如：巧克力蛋糕、麵包...",
                    help="為這個食譜組合取個名字",
                    key="recipe_name_input"
                )
                
                # 顯示保存成功訊息
                if st.session_state.show_save_success:
                    st.markdown(f"""
                    <div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; border: 1px solid #c3e6cb; margin: 10px 0;">
                        <strong>✅ 保存成功！</strong> 食譜「{st.session_state.saved_recipe_name}」已保存到食譜區。
                    </div>
                    """, unsafe_allow_html=True)
                    # 重置狀態
                    st.session_state.show_save_success = False
                    st.session_state.saved_recipe_name = ""
                
                # 保存按鈕
                if recipe_name:
                    if st.button("保存食譜", type="secondary", use_container_width=True, key="save_recipe_btn"):
                        # 檢查是否已存在同名食譜
                        if recipe_name in st.session_state.saved_recipes:
                            st.warning(f"⚠️ 食譜「{recipe_name}」已存在，將覆蓋原有食譜")
                        
                        # 保存食譜
                        recipe_data = {
                            "materials": recipe_materials,
                            "total_cost": total_cost,
                            "created_at": get_taiwan_time().isoformat()
                        }
                        st.session_state.saved_recipes[recipe_name] = recipe_data
                        save_recipes_data()
                        
                        # 設置成功狀態
                        st.session_state.show_save_success = True
                        st.session_state.saved_recipe_name = recipe_name
                        st.success(f"✅ 食譜「{recipe_name}」保存成功！")
                        st.rerun()
                else:
                    st.info("先輸入食譜名稱才能保存")
    else:
        st.markdown("""
        <div class="warning-message">
            <h4>尚未新增材料</h4>
            <p>先在「材料管理」頁面新增常用的材料！</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "材料管理":
    # 材料管理頁面
    st.markdown("### 材料管理")

    # 新增材料區塊
    st.markdown("#### 新增材料")

    col1, col2 = st.columns([1, 1])

    with col1:

        # 檢查是否在編輯模式
        if hasattr(st.session_state, 'editing_material') and st.session_state.editing_material:
            st.markdown(f"#### 編輯材料：{st.session_state.editing_material}")

            # 編輯材料表單
            with st.form("edit_material_form"):
                edited_name = st.text_input(
                    "材料名稱",
                    value=st.session_state.editing_material,
                    label_visibility="visible"
                )
                edited_price = st.number_input(
                    "單價 (每g，NT$)", 
                    min_value=0.0, 
                    value=float(st.session_state.editing_price) if st.session_state.editing_price is not None else 0.0, 
                    step=0.01,
                    help="輸入每克的價格",
                    label_visibility="visible"
                )

                col_save, col_cancel = st.columns(2)
                with col_save:
                    submitted = st.form_submit_button("儲存修改", type="primary", use_container_width=True)
                with col_cancel:
                    if st.form_submit_button("取消編輯", use_container_width=True):
                        st.session_state.editing_material = None
                        st.session_state.editing_price = None
                        st.rerun()

                if submitted:
                    if not edited_name:
                        st.error("請輸入材料名稱！")
                    elif edited_price is None or edited_price < 0:
                        st.error("請輸入有效的單價（必須大於等於0）！")
                    else:
                        # 如果名稱改變，需要檢查是否已存在
                        if edited_name != st.session_state.editing_material and edited_name in st.session_state.saved_materials:
                            st.error("材料名稱已存在！")
                        else:
                            old_material_name = st.session_state.editing_material
                            old_price = st.session_state.saved_materials[old_material_name]
                            
                            # 刪除舊材料，添加新材料
                            del st.session_state.saved_materials[old_material_name]
                            st.session_state.saved_materials[edited_name] = edited_price
                            
                            # 更新自訂順序（保持原位置）
                            if hasattr(st.session_state, 'custom_material_order'):
                                if old_material_name in st.session_state.custom_material_order:
                                    idx = st.session_state.custom_material_order.index(old_material_name)
                                    st.session_state.custom_material_order[idx] = edited_name
                            
                            # 更新食譜中的材料價格和成本
                            updated_recipes = []
                            for recipe_name, recipe_data in st.session_state.saved_recipes.items():
                                if old_material_name in recipe_data['materials']:
                                    # 更新材料名稱（如果名稱改變）
                                    if edited_name != old_material_name:
                                        recipe_data['materials'][edited_name] = recipe_data['materials'].pop(old_material_name)
                                    
                                    # 更新材料價格
                                    recipe_data['materials'][edited_name]['price'] = edited_price
                                    
                                    # 重新計算材料成本
                                    weight = recipe_data['materials'][edited_name]['weight']
                                    yield_rate = recipe_data['materials'][edited_name].get('yield_rate')
                                    
                                    if yield_rate is not None and yield_rate > 0:
                                        # 使用熟成率計算
                                        adjusted_weight = weight / yield_rate
                                        material_cost = adjusted_weight * edited_price
                                    else:
                                        # 原本的計算
                                        material_cost = weight * edited_price
                                    
                                    recipe_data['materials'][edited_name]['cost'] = material_cost
                                    recipe_data['materials'][edited_name]['adjusted_weight'] = adjusted_weight if yield_rate is not None and yield_rate > 0 else weight
                                    
                                    # 重新計算食譜總成本
                                    total_cost = sum(mat_data['cost'] for mat_data in recipe_data['materials'].values())
                                    recipe_data['total_cost'] = total_cost
                                    
                                    updated_recipes.append(recipe_name)
                            
                            save_materials_data()
                            if updated_recipes:
                                save_recipes_data()
                            
                            st.session_state.editing_material = None
                            st.session_state.editing_price = None
                            
                            if updated_recipes:
                                st.success(f"✅ 已更新材料「{edited_name}」並同步更新了 {len(updated_recipes)} 個食譜的成本")
                            else:
                                st.success(f"✅ 已更新材料「{edited_name}」")
                            st.rerun()
        
        # 只有在非編輯模式時才顯示新增材料表單
        else:
            # 新增材料表單
            with st.container():
                st.markdown('<div class="form-container">', unsafe_allow_html=True)
                
                with st.form("add_material_form"):
                    material_name = st.text_input(
                        "材料名稱",
                        key=f"material_input_{st.session_state.material_input_key}",
                        label_visibility="visible",
                        help="請只輸入材料名稱，不要包含重量或價格信息"
                    )
                    price_per_100g = st.number_input(
                        "單價 (每g，NT$)", 
                        min_value=0.0, 
                        value=None, 
                        key=f"price_input_{st.session_state.price_input_key}",
                        step=0.01,
                        help="輸入每克的價格",
                        label_visibility="visible"
                    )
                    
                    submitted = st.form_submit_button("儲存材料", type="primary", use_container_width=True)
                    if submitted:
                        if not material_name:
                            st.error("請輸入材料名稱！")
                        elif price_per_100g is None or price_per_100g < 0:
                            st.error("請輸入有效的單價（必須大於等於0）！")
                        else:
                            st.session_state.saved_materials[material_name] = price_per_100g
                            save_materials_data()
                            # 記住展開狀態
                            st.session_state.materials_expander_expanded = True
                            # 增加key值來清空輸入框
                            st.session_state.material_input_key += 1
                            st.session_state.price_input_key += 1
                            st.markdown(f"""
                            <div class="success-message">
                                <strong>成功！</strong> 已儲存 {material_name}
                            </div>
                            """, unsafe_allow_html=True)
                            st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 右側空白區域
        pass

    # 已儲存材料區塊（移到下方）
    st.markdown("---")
    st.markdown("#### 已儲存材料")

    if st.session_state.saved_materials:
        # 顯示材料數量
        material_count = len(st.session_state.saved_materials)
        st.info(f"📦 已儲存 {material_count} 個材料")
        
        # 使用自訂順序顯示材料
        if hasattr(st.session_state, 'custom_material_order'):
            # 根據自訂順序排序
            order_dict = {material: i for i, material in enumerate(st.session_state.custom_material_order)}
            sorted_materials = sorted(st.session_state.saved_materials.items(), key=lambda x: order_dict.get(x[0], 999))
        else:
            # 初始化自訂順序
            st.session_state.custom_material_order = list(st.session_state.saved_materials.keys())
            sorted_materials = list(st.session_state.saved_materials.items())
        
        # 使用可展開容器顯示材料列表
        with st.expander(f"📋 查看所有材料 ({material_count} 個)", expanded=st.session_state.materials_expander_expanded):
            # 並排顯示材料（每行2個）
            materials_per_row = 2
            
            for i in range(0, len(sorted_materials), materials_per_row):
                row_materials = sorted_materials[i:i + materials_per_row]
                cols = st.columns(materials_per_row)
                
                for j, (material, price) in enumerate(row_materials):
                    with cols[j]:
                        price_display = price
                        if price_display is not None and price_display == int(price_display):
                            price_display = int(price_display)
                        
                        # 材料信息和操作按鈕並排顯示
                        col_info, col_actions = st.columns([3, 1])
                        
                        with col_info:
                            # 檢查是否在編輯此材料
                            if st.session_state.get('editing_material') == material:
                                # 顯示內聯編輯表單
                                col_name, col_price = st.columns([2, 1])
                                with col_name:
                                    # 使用安全的key，避免特殊符號問題
                                    safe_edit_name_key = f"edit_name_{hash(material) % 1000000}"
                                    safe_edit_price_key = f"edit_price_{hash(material) % 1000000}"
                                    safe_save_key = f"save_edit_{hash(material) % 1000000}"
                                    safe_cancel_key = f"cancel_edit_{hash(material) % 1000000}"
                                    
                                    edited_name = st.text_input(
                                        "材料名稱",
                                        value=material,
                                        key=safe_edit_name_key,
                                        label_visibility="collapsed",
                                        help="請只輸入材料名稱，不要包含重量或價格信息"
                                    )
                                with col_price:
                                    edited_price = st.number_input(
                                        "單價",
                                        value=float(price),
                                        min_value=0.0,
                                        step=0.01,
                                        key=safe_edit_price_key,
                                        label_visibility="collapsed"
                                    )
                                
                                # 確認和取消按鈕
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.button("✅", key=safe_save_key, help="保存修改", use_container_width=True):
                                        if edited_name and edited_price >= 0:
                                            # 檢查名稱是否已存在（除了自己）
                                            if edited_name != material and edited_name in st.session_state.saved_materials:
                                                st.error("材料名稱已存在！")
                                            else:
                                                old_price = st.session_state.saved_materials[material]
                                                # 更新材料
                                                del st.session_state.saved_materials[material]
                                                st.session_state.saved_materials[edited_name] = edited_price
                                                
                                                # 更新自訂順序（保持原位置）
                                                if hasattr(st.session_state, 'custom_material_order'):
                                                    if material in st.session_state.custom_material_order:
                                                        idx = st.session_state.custom_material_order.index(material)
                                                        st.session_state.custom_material_order[idx] = edited_name
                                                
                                                # 更新食譜中的材料價格和成本
                                                updated_recipes = []
                                                for recipe_name, recipe_data in st.session_state.saved_recipes.items():
                                                    if material in recipe_data['materials']:
                                                        # 更新材料名稱（如果名稱改變）
                                                        if edited_name != material:
                                                            recipe_data['materials'][edited_name] = recipe_data['materials'].pop(material)
                                                        
                                                        # 更新材料價格
                                                        recipe_data['materials'][edited_name]['price'] = edited_price
                                                        
                                                        # 重新計算材料成本
                                                        weight = recipe_data['materials'][edited_name]['weight']
                                                        yield_rate = recipe_data['materials'][edited_name].get('yield_rate')
                                                        
                                                        if yield_rate is not None and yield_rate > 0:
                                                            # 使用熟成率計算
                                                            adjusted_weight = weight / yield_rate
                                                            material_cost = adjusted_weight * edited_price
                                                        else:
                                                            # 原本的計算
                                                            material_cost = weight * edited_price
                                                        
                                                        recipe_data['materials'][edited_name]['cost'] = material_cost
                                                        recipe_data['materials'][edited_name]['adjusted_weight'] = adjusted_weight if yield_rate is not None and yield_rate > 0 else weight
                                                        
                                                        # 重新計算食譜總成本
                                                        total_cost = sum(mat_data['cost'] for mat_data in recipe_data['materials'].values())
                                                        recipe_data['total_cost'] = total_cost
                                                        
                                                        updated_recipes.append(recipe_name)
                                                
                                                save_materials_data()
                                                if updated_recipes:
                                                    save_recipes_data()
                                                
                                                st.session_state.editing_material = None
                                                st.session_state.materials_expander_expanded = True
                                                
                                                if updated_recipes:
                                                    st.success(f"✅ 已更新材料「{edited_name}」並同步更新了 {len(updated_recipes)} 個食譜的成本")
                                                else:
                                                    st.success(f"✅ 已更新材料「{edited_name}」")
                                                st.rerun()
                                        else:
                                            st.error("請輸入有效的材料名稱和單價！")
                                with col_cancel:
                                    if st.button("❌", key=safe_cancel_key, help="取消編輯", use_container_width=True):
                                        st.session_state.editing_material = None
                                        st.rerun()
                            else:
                                # 顯示正常的材料信息
                                import html
                                # 使用更安全的字符串處理，特別處理 $ 符號
                                safe_material_name = material.replace('$', '＄')  # 使用全形美元符號
                                safe_material_name = html.escape(safe_material_name)
                                
                                # 檢查是否為標記的材料，如果是則加上星號
                                is_starred = material in st.session_state.starred_materials
                                star_prefix = "⭐ " if is_starred else ""
                                st.markdown(f"<div style='padding-top: 8px;'><strong>{star_prefix}{safe_material_name}</strong> (NT$ {price_display}/g)</div>", unsafe_allow_html=True)
                        
                        with col_actions:
                            # 操作按鈕
                            col_star, col_edit, col_move_up, col_move_down, col_delete = st.columns(5)
                            
                            with col_star:
                                # 星星按鈕 - 使用安全的key，避免特殊符號問題
                                safe_star_key = f"star_{hash(material) % 1000000}"
                                is_starred = material in st.session_state.starred_materials
                                star_icon = "⭐" if is_starred else "☆"
                                star_help = f"取消標記 {material}" if is_starred else f"標記 {material}"
                                if st.button(star_icon, key=safe_star_key, help=star_help, use_container_width=True):
                                    if is_starred:
                                        st.session_state.starred_materials.remove(material)
                                        st.success(f"✅ 已取消標記材料「{material}」")
                                    else:
                                        st.session_state.starred_materials.add(material)
                                        st.success(f"✅ 已標記材料「{material}」")
                                    st.rerun()
                            
                            with col_edit:
                                # 使用安全的key，避免特殊符號問題
                                safe_edit_btn_key = f"edit_{hash(material) % 1000000}"
                                if st.button("✏️", key=safe_edit_btn_key, help=f"編輯 {material}", use_container_width=True):
                                    # 記住展開狀態
                                    st.session_state.materials_expander_expanded = True
                                    st.session_state.editing_material = material
                                    st.rerun()
                            
                            with col_move_up:
                                # 使用安全的key，避免特殊符號問題
                                safe_move_up_key = f"move_up_{hash(material) % 1000000}"
                                if st.button("⬆️", key=safe_move_up_key, help=f"上移 {material}", use_container_width=True):
                                    # 初始化自訂順序並同步
                                    if not hasattr(st.session_state, 'custom_material_order'):
                                        st.session_state.custom_material_order = list(st.session_state.saved_materials.keys())
                                    else:
                                        # 同步 custom_material_order 和 saved_materials
                                        st.session_state.custom_material_order = [mat for mat in st.session_state.custom_material_order if mat in st.session_state.saved_materials]
                                        # 添加任何缺失的材料
                                        for mat in st.session_state.saved_materials.keys():
                                            if mat not in st.session_state.custom_material_order:
                                                st.session_state.custom_material_order.append(mat)
                                    
                                    # 移動材料
                                    if material in st.session_state.custom_material_order:
                                        current_index = st.session_state.custom_material_order.index(material)
                                        if current_index > 0:
                                            # 交換順序
                                            st.session_state.custom_material_order[current_index], st.session_state.custom_material_order[current_index-1] = \
                                                st.session_state.custom_material_order[current_index-1], st.session_state.custom_material_order[current_index]
                                            
                                            # 重新排序 saved_materials 字典
                                            new_materials = {}
                                            for mat in st.session_state.custom_material_order:
                                                if mat in st.session_state.saved_materials:
                                                    new_materials[mat] = st.session_state.saved_materials[mat]
                                            
                                            st.session_state.saved_materials = new_materials
                                            save_materials_data()
                                            # 記住展開狀態
                                            st.session_state.materials_expander_expanded = True
                                            st.success(f"✅ 已上移材料「{material}」")
                                            st.rerun()
                                        else:
                                            st.info("📌 已經是第一個材料")
                                    else:
                                        st.error(f"❌ 材料「{material}」不在列表中")
                                        st.rerun()
                            
                            with col_move_down:
                                # 使用安全的key，避免特殊符號問題
                                safe_move_down_key = f"move_down_{hash(material) % 1000000}"
                                if st.button("⬇️", key=safe_move_down_key, help=f"下移 {material}", use_container_width=True):
                                    # 初始化自訂順序並同步
                                    if not hasattr(st.session_state, 'custom_material_order'):
                                        st.session_state.custom_material_order = list(st.session_state.saved_materials.keys())
                                    else:
                                        # 同步 custom_material_order 和 saved_materials
                                        st.session_state.custom_material_order = [mat for mat in st.session_state.custom_material_order if mat in st.session_state.saved_materials]
                                        # 添加任何缺失的材料
                                        for mat in st.session_state.saved_materials.keys():
                                            if mat not in st.session_state.custom_material_order:
                                                st.session_state.custom_material_order.append(mat)
                                    
                                    # 移動材料
                                    if material in st.session_state.custom_material_order:
                                        current_index = st.session_state.custom_material_order.index(material)
                                        if current_index < len(st.session_state.custom_material_order) - 1:
                                            # 交換順序
                                            st.session_state.custom_material_order[current_index], st.session_state.custom_material_order[current_index+1] = \
                                                st.session_state.custom_material_order[current_index+1], st.session_state.custom_material_order[current_index]
                                            
                                            # 重新排序 saved_materials 字典
                                            new_materials = {}
                                            for mat in st.session_state.custom_material_order:
                                                if mat in st.session_state.saved_materials:
                                                    new_materials[mat] = st.session_state.saved_materials[mat]
                                            
                                            st.session_state.saved_materials = new_materials
                                            save_materials_data()
                                            # 記住展開狀態
                                            st.session_state.materials_expander_expanded = True
                                            st.success(f"✅ 已下移材料「{material}」")
                                            st.rerun()
                                        else:
                                            st.info("📌 已經是最後一個材料")
                                    else:
                                        st.error(f"❌ 材料「{material}」不在列表中")
                                        st.rerun()
                            
                            with col_delete:
                                # 檢查是否在確認刪除狀態
                                if st.session_state.get(f"show_delete_modal_{material}", False):
                                    # 顯示確認按鈕（垂直排列）
                                    # 使用安全的key，避免特殊符號問題
                                    safe_confirm_del_key = f"confirm_del_{hash(material) % 1000000}"
                                    safe_cancel_del_key = f"cancel_del_{hash(material) % 1000000}"
                                    if st.button("✅", key=safe_confirm_del_key, help="確認刪除", use_container_width=True):
                                        # 記住展開狀態
                                        st.session_state.materials_expander_expanded = True
                                        
                                        # 檢查哪些食譜使用了這個材料
                                        affected_recipes = []
                                        for recipe_name, recipe_data in st.session_state.saved_recipes.items():
                                            if material in recipe_data['materials']:
                                                affected_recipes.append(recipe_name)
                                        
                                        # 刪除材料
                                        del st.session_state.saved_materials[material]
                                        
                                        # 同時從自訂順序中移除
                                        if hasattr(st.session_state, 'custom_material_order') and material in st.session_state.custom_material_order:
                                            st.session_state.custom_material_order.remove(material)
                                        
                                        # 從食譜中移除該材料並重新計算成本
                                        for recipe_name in affected_recipes:
                                            recipe_data = st.session_state.saved_recipes[recipe_name]
                                            # 移除材料
                                            del recipe_data['materials'][material]
                                            
                                            # 重新計算食譜總成本
                                            if recipe_data['materials']:  # 如果還有其他材料
                                                total_cost = sum(mat_data['cost'] for mat_data in recipe_data['materials'].values())
                                                recipe_data['total_cost'] = total_cost
                                            else:
                                                # 如果沒有材料了，刪除整個食譜
                                                del st.session_state.saved_recipes[recipe_name]
                                                affected_recipes.remove(recipe_name)
                                        
                                        save_materials_data()
                                        if affected_recipes:
                                            save_recipes_data()
                                        
                                        # 重置刪除確認狀態
                                        st.session_state[f"show_delete_modal_{material}"] = False
                                        
                                        if affected_recipes:
                                            st.success(f"✅ 已刪除材料「{material}」並更新了 {len(affected_recipes)} 個食譜")
                                        else:
                                            st.success(f"✅ 已刪除材料「{material}」")
                                        st.rerun()
                                    if st.button("❌", key=safe_cancel_del_key, help="取消刪除", use_container_width=True):
                                        # 重置刪除確認狀態
                                        st.session_state[f"show_delete_modal_{material}"] = False
                                        st.rerun()
                                else:
                                    # 顯示刪除按鈕
                                    # 使用安全的key，避免特殊符號問題
                                    safe_del_key = f"del_{hash(material) % 1000000}"
                                    if st.button("🗑️", key=safe_del_key, help=f"刪除 {material}", use_container_width=True):
                                        # 設置刪除確認狀態
                                        st.session_state[f"show_delete_modal_{material}"] = True
                                        st.rerun()
                        
                        st.markdown("<div style='margin: 4px 0; border-bottom: 1px solid #e0e0e0;'></div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-message">
            <p>尚未新增任何材料</p>
        </div>
        """, unsafe_allow_html=True)

    # 批量操作
    if st.session_state.saved_materials:
        st.markdown("---")
        st.markdown("#### 批量操作")

        # 檢查是否在確認清除狀態
        if "confirming_clear_all" not in st.session_state:
            st.session_state["confirming_clear_all"] = False

        if not st.session_state["confirming_clear_all"]:
            if st.button("清除所有材料", type="secondary", use_container_width=True, key="clear_all_materials"):
                st.session_state["confirming_clear_all"] = True
                st.rerun()
        else:
            st.warning("⚠️ 確定要清除所有材料嗎？此操作無法復原！")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("確認清除", type="secondary", use_container_width=True, key="confirm_clear_materials"):
                    # 直接清除所有材料
                    st.session_state.saved_materials = {}
                    # 同時清除自訂順序
                    if hasattr(st.session_state, 'custom_material_order'):
                        st.session_state.custom_material_order = []
                    save_materials_data()
                    st.session_state["confirming_clear_all"] = False
                    st.success("✅ 已清除所有材料")
                    st.rerun()
            with col_cancel:
                if st.button("取消", type="secondary", use_container_width=True, key="cancel_clear_materials"):
                    st.session_state["confirming_clear_all"] = False
                    st.info("❌ 已取消清除所有材料")
                    st.rerun()
        
        # if st.button("切換到成本計算", use_container_width=True):
        #     st.info("🔄 正在切換到成本計算頁面...")
        #     st.session_state.current_page = "成本計算"
        #     st.rerun()

elif st.session_state.current_page == "食譜區":
    # 食譜區頁面
    st.markdown("### 食譜區")
    
    # 檢查是否在編輯食譜模式
    if hasattr(st.session_state, 'editing_recipe') and st.session_state.editing_recipe:
        st.markdown(f"#### 編輯食譜：{st.session_state.editing_recipe}")
        
        # 編輯食譜表單
        with st.form("edit_recipe_form"):
            edited_recipe_name = st.text_input(
                "食譜名稱",
                value=st.session_state.editing_recipe,
                label_visibility="visible"
            )
            
            # 顯示材料列表（可編輯）
            st.markdown("#### 材料清單")
            recipe_data = st.session_state.editing_recipe_data
            edited_materials = {}
            
            for material, data in recipe_data['materials'].items():
                st.markdown(f"**{material}**")
                col1, col2 = st.columns(2)
                
                with col1:
                    weight = st.number_input(
                        f"{material} 重量 (g)",
                        value=float(data['weight']),
                        min_value=0.0,
                        step=1.0,
                        key=f"edit_weight_{material}"
                    )
                
                with col2:
                    price = st.number_input(
                        f"{material} 單價",
                        value=float(data['price']),
                        min_value=0.0,
                        step=0.01,
                        key=f"edit_price_{material}"
                    )
                
                # 熟成率固定為0.8（不顯示編輯選項）
                yield_enabled = True
                
                # 計算成本
                if yield_enabled:
                    # 使用固定熟成率0.8計算：重量 / 0.8 * 單價
                    adjusted_weight = weight / 0.8
                    material_cost = adjusted_weight * price
                    yield_rate = 0.8
                else:
                    # 原本的計算：重量 * 單價
                    material_cost = weight * price
                    yield_rate = None
                
                edited_materials[material] = {
                    "weight": weight,
                    "price": price,
                    "cost": material_cost,
                    "yield_rate": yield_enabled,  # 儲存勾選狀態
                    "adjusted_weight": adjusted_weight if yield_enabled else weight
                }
                
                st.markdown(f"成本：NT$ {material_cost:.2f}")
                st.markdown("---")
            
            # 計算總成本
            total_cost = sum(mat_data['cost'] for mat_data in edited_materials.values())
            st.markdown(f"**總成本：NT$ {total_cost:.2f}**")
            
            # 添加提交按鈕
            col_save, col_cancel = st.columns(2)
            with col_save:
                submitted = st.form_submit_button("儲存修改", type="primary", use_container_width=True)
            with col_cancel:
                if st.form_submit_button("取消編輯", use_container_width=True):
                    st.session_state.editing_recipe = None
                    st.session_state.editing_recipe_data = None
                    st.rerun()
        
        # 處理表單提交（在表單外部）
        if submitted:
            if edited_recipe_name:
                # 如果名稱改變，需要檢查是否已存在
                if edited_recipe_name != st.session_state.editing_recipe and edited_recipe_name in st.session_state.saved_recipes:
                    st.error("食譜名稱已存在！")
                else:
                    # 同步更新材料管理的單價
                    for material, data in edited_materials.items():
                        if material in st.session_state.saved_materials:
                            # 更新材料管理中的單價
                            st.session_state.saved_materials[material] = data['price']
                    
                    # 儲存材料資料
                    save_materials_data()
                    
                    # 更新食譜
                    old_name = st.session_state.editing_recipe
                    updated_recipe_data = {
                        "materials": edited_materials,
                        "total_cost": total_cost,
                        "created_at": recipe_data['created_at'],
                        "updated_at": get_taiwan_time().isoformat()
                    }
                    
                    # 如果名稱改變，刪除舊食譜
                    if edited_recipe_name != old_name:
                        del st.session_state.saved_recipes[old_name]
                    
                    st.session_state.saved_recipes[edited_recipe_name] = updated_recipe_data
                    save_recipes_data()
                    st.session_state.editing_recipe = None
                    st.session_state.editing_recipe_data = None
                    # 保持食譜展開狀態
                    if edited_recipe_name in st.session_state.recipe_expander_states:
                        st.session_state.recipe_expander_states[edited_recipe_name] = True
                    st.success(f"✅ 已更新食譜「{edited_recipe_name}」並同步更新材料管理單價")
                    # 不刷新頁面，只重新渲染當前部分
                    st.rerun()
            else:
                st.error("請輸入食譜名稱！")
    
    if st.session_state.saved_recipes:
        # 顯示已保存的食譜
        for recipe_name, recipe_data in st.session_state.saved_recipes.items():
            total_cost_display = recipe_data['total_cost']
            if total_cost_display == int(total_cost_display):
                total_cost_display = int(total_cost_display)
            else:
                total_cost_display = f"{recipe_data['total_cost']:.2f}"
            
            # 使用動態展開狀態
            expander_key = f"recipe_expander_{recipe_name}"
            is_expanded = st.session_state.recipe_expander_states.get(recipe_name, False)
            
            with st.expander(f"📖 {recipe_name} - NT$ {total_cost_display}", expanded=is_expanded):
                # 更新展開狀態
                st.session_state.recipe_expander_states[recipe_name] = True
                
                # 顯示食譜詳細資訊
                st.markdown(f"**創建時間：** {recipe_data['created_at'][:19]}")
                if 'updated_at' in recipe_data:
                    st.markdown(f"**最後更新：** {recipe_data['updated_at'][:19]}")
                st.markdown("---")
                
                # 顯示材料列表
                st.markdown("#### 材料清單")
                
                # 添加欄位標題
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown("**材料名稱**")
                with col2:
                    st.markdown("**克數**")
                with col3:
                    st.markdown("**單價**")
                with col4:
                    st.markdown("**成本**")
                
                st.markdown("---")
                
                for material, data in recipe_data['materials'].items():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"**{material}**")
                    with col2:
                        st.markdown(f"{data['weight']:.1f} g")
                    with col3:
                        price_display = data['price']
                        if price_display == int(price_display):
                            price_display = int(price_display)
                        st.markdown(f"NT$ {price_display}")
                    with col4:
                        cost_display = data['cost']
                        if cost_display == int(cost_display):
                            cost_display = int(cost_display)
                        else:
                            cost_display = f"{data['cost']:.2f}"
                        st.markdown(f"NT$ {cost_display}")
                
                st.markdown("---")
                total_cost_display = recipe_data['total_cost']
                if total_cost_display == int(total_cost_display):
                    total_cost_display = int(total_cost_display)
                else:
                    total_cost_display = f"{recipe_data['total_cost']:.2f}"
                st.markdown(f"**總成本：NT$ {total_cost_display}**")

                # 操作按鈕
                col_use, col_edit, col_delete = st.columns(3)
                with col_use:
                    if st.button("使用此食譜", key=f"use_{recipe_name}", use_container_width=True):
                        st.info(f"🔄 正在載入食譜「{recipe_name}」...")
                        # 將食譜材料載入到成本計算頁面
                        st.session_state.selected_materials = list(recipe_data['materials'].keys())
                        st.session_state.material_weights = {
                            material: data['weight'] 
                            for material, data in recipe_data['materials'].items()
                        }
                        st.session_state.current_page = "成本計算"
                        st.success(f"✅ 已載入食譜「{recipe_name}」到成本計算頁面")
                        st.rerun()

                with col_edit:
                    if st.button("✏️ 編輯", key=f"edit_recipe_{recipe_name}", use_container_width=True):
                        st.session_state.editing_recipe = recipe_name
                        st.session_state.editing_recipe_data = recipe_data
                        # 保持展開狀態
                        st.session_state.recipe_expander_states[recipe_name] = True
                        st.rerun()

                with col_delete:
                    # 檢查是否在確認刪除狀態
                    if st.session_state.get(f'show_delete_recipe_modal_{recipe_name}', False):
                        st.warning(f"⚠️ 確定要刪除食譜「{recipe_name}」嗎？此操作無法復原！")
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("確認刪除", key=f"confirm_del_recipe_{recipe_name}", use_container_width=True):
                                del st.session_state.saved_recipes[recipe_name]
                                # 移除展開狀態
                                if recipe_name in st.session_state.recipe_expander_states:
                                    del st.session_state.recipe_expander_states[recipe_name]
                                save_recipes_data()
                                st.session_state[f'show_delete_recipe_modal_{recipe_name}'] = False
                                st.success(f"✅ 已刪除食譜「{recipe_name}」")
                                st.rerun()
                        with col_cancel:
                            if st.button("取消", key=f"cancel_del_recipe_{recipe_name}", use_container_width=True):
                                st.session_state[f'show_delete_recipe_modal_{recipe_name}'] = False
                                st.info(f"❌ 已取消刪除食譜「{recipe_name}」")
                                st.rerun()
                    else:
                        if st.button("🗑️ 刪除", key=f"del_recipe_{recipe_name}", use_container_width=True):
                            st.session_state[f'show_delete_recipe_modal_{recipe_name}'] = True
                            st.rerun()
    else:
        st.markdown("""
        <div class="warning-message">
            <h4>尚未保存任何食譜</h4>
            <p>請先在「成本計算」頁面創建並保存食譜。</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "記帳區":
    # 記帳區頁面
    st.markdown("### 記帳區")
    

    

    
    # 記帳表單（現在佔據整個寬度）
    st.markdown("#### 新增記帳")
        
    # 新增類別功能（在表單外面）
    with st.expander("➕ 新增自訂類別", expanded=False):
        col_new_category, col_add_btn = st.columns([3, 1])
        with col_new_category:
            new_category = st.text_input(
                "新類別名稱",
                placeholder="例如：食材、設備、包裝...",
                key="new_category_input"
            )
        with col_add_btn:
            if st.button("新增", type="primary"):
                if new_category and new_category.strip():
                    if new_category not in st.session_state.custom_categories:
                        st.session_state.custom_categories.append(new_category.strip())
                        save_custom_categories()
                        st.success(f"✅ 已新增類別「{new_category}」")
                        st.rerun()
                    else:
                        st.error("❌ 此類別已存在！")
                else:
                    st.error("❌ 請輸入類別名稱！")
    
    st.markdown("---")
    
    # 新增記帳表單
    with st.form(f"add_accounting_form_{st.session_state.accounting_form_key}"):
        # 日期選擇
        record_date = st.date_input(
            "日期",
            value=datetime.now().date(),
            key=f"record_date_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 收入/支出選擇
        transaction_type = st.selectbox(
            "類型",
            ["支出", "收入"],
            key=f"transaction_type_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 類別選擇
        category = st.selectbox(
            "類別",
            options=st.session_state.custom_categories,
            placeholder="選擇類別...",
            key=f"category_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 細項
        description = st.text_input(
            "細項",
            placeholder="例如：購買麵粉、運費、銷售收入...",
            key=f"description_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 金額
        amount = st.number_input(
            "金額 (NT$)",
            min_value=0.0,
            value=None,
            step=1.0,
            key=f"amount_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 地點
        location = st.text_input(
            "地點",
            placeholder="例如：超市、網購、實體店...",
            key=f"location_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 購買人
        buyer = st.text_input(
            "購買人",
            placeholder="例如：張三、李四...",
            key=f"buyer_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 產品選擇（來自食譜區）- 改為複選
        product_options = list(st.session_state.saved_recipes.keys())
        selected_products = st.multiselect(
            "產品（可複選）",
            product_options,
            key=f"products_{st.session_state.accounting_form_key}",
            label_visibility="visible"
        )
        
        # 備註（非必填）
        remark = st.text_area(
            "備註",
            placeholder="額外說明（非必填）...",
            key=f"remark_{st.session_state.accounting_form_key}",
            label_visibility="visible",
            height=80
        )
        
        submitted = st.form_submit_button("新增記帳", type="primary", use_container_width=True)
        if submitted:
            if description and amount > 0:
                # 生成唯一ID
                record_id = str(uuid.uuid4())
                
                # 新增記帳記錄
                record = {
                    "id": record_id,
                    "date": record_date.isoformat(),
                    "type": transaction_type,
                    "category": category if category else "其他",  # 使用選擇的類別
                    "description": description,
                    "amount": amount,
                    "location": location,
                    "buyer": buyer,
                    "products": selected_products,  # 改為複選
                    "remark": remark,
                    "created_at": get_taiwan_time().isoformat()
                }
                st.session_state.accounting_records.append(record)
                save_accounting_data()
                
                # 增加form key來清空輸入框
                st.session_state.accounting_form_key += 1
                
                st.success(f"✅ 記帳成功！{transaction_type} - {description} - NT$ {amount}")
                st.rerun()
            else:
                st.error("請輸入細項和金額！")

    
    # 記帳記錄和月報表
    if st.session_state.accounting_records:
        st.markdown("---")
        
        # 選擇顯示模式
        display_mode = st.radio(
            "顯示模式",
            ["記帳記錄", "購買人紀錄"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if display_mode == "記帳記錄":
            st.markdown("#### 記帳記錄")
            
            # 記錄類型篩選
            record_filter = st.radio(
                "記錄類型",
                ["全部記錄", "總收入紀錄", "總支出紀錄"],
                horizontal=True,
                label_visibility="collapsed"
            )
            
            # 產品篩選
            # 獲取所有產品的值
            all_products = set()
            for record in st.session_state.accounting_records:
                products = record.get('products', [])
                if not products:  # 相容舊格式
                    product = record.get('product', '')
                    products = [product] if product else []
                for product in products:
                    if product:  # 只包含有產品的記錄
                        all_products.add(product)
            

            
            # 產品選擇（始終顯示）
            product_filter = st.selectbox(
                "產品篩選",
                ["全部產品"] + sorted(list(all_products)),
                label_visibility="collapsed"
            )
            
            # 根據篩選條件過濾記錄
            filtered_records = st.session_state.accounting_records
            if record_filter == "總收入紀錄":
                filtered_records = [r for r in st.session_state.accounting_records if r["type"] == "收入"]
            elif record_filter == "總支出紀錄":
                filtered_records = [r for r in st.session_state.accounting_records if r["type"] == "支出"]
            

            
            # 根據產品篩選
            if product_filter != "全部產品":
                filtered_records = [r for r in filtered_records if product_filter in (r.get('products', []) or [r.get('product', '')])]
            
            # 日期篩選
            if filtered_records:
                # 獲取所有記錄的日期
                all_dates = []
                for record in filtered_records:
                    date_str = record.get('date', record.get('datetime', ''))
                    if 'T' in date_str:  # 如果是datetime格式，只取日期部分
                        date_str = date_str.split('T')[0]
                    all_dates.append(datetime.fromisoformat(date_str))
                
                # 日期選擇模式
                date_mode = st.radio(
                    "日期篩選",
                    ["全部日期", "選擇月份", "選擇日期範圍"],
                    horizontal=True,
                    label_visibility="collapsed"
                )
                
                if date_mode == "選擇月份":
                    years = sorted(list(set(date.year for date in all_dates)), reverse=True)
                    months = sorted(list(set(date.month for date in all_dates)), reverse=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_year = st.selectbox("選擇年份", years, label_visibility="collapsed")
                    with col2:
                        selected_month = st.selectbox("選擇月份", [m for m in months if datetime(selected_year, m, 1) in [datetime(date.year, date.month, 1) for date in all_dates]], label_visibility="collapsed")
                    
                    # 篩選該月份的記錄
                    month_records = []
                    for record in filtered_records:
                        date_str = record.get('date', record.get('datetime', ''))
                        if 'T' in date_str:  # 如果是datetime格式，只取日期部分
                            date_str = date_str.split('T')[0]
                        record_date = datetime.fromisoformat(date_str)
                        if record_date.year == selected_year and record_date.month == selected_month:
                            month_records.append(record)
                    
                    filtered_records = month_records
                    period_title = f"{selected_year}年{selected_month}月"
                    
                elif date_mode == "選擇日期範圍":
                    min_date = min(all_dates).date()
                    max_date = max(all_dates).date()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        start_date = st.date_input("開始日期", value=min_date, min_value=min_date, max_value=max_date, label_visibility="collapsed")
                    with col2:
                        end_date = st.date_input("結束日期", value=max_date, min_value=min_date, max_value=max_date, label_visibility="collapsed")
                    
                    # 篩選日期範圍內的記錄
                    date_range_records = []
                    for record in filtered_records:
                        date_str = record.get('date', record.get('datetime', ''))
                        if 'T' in date_str:  # 如果是datetime格式，只取日期部分
                            date_str = date_str.split('T')[0]
                        record_date = datetime.fromisoformat(date_str).date()
                        if start_date <= record_date <= end_date:
                            date_range_records.append(record)
                    
                    filtered_records = date_range_records
                    period_title = f"{start_date} 至 {end_date}"
                else:
                    period_title = "全部日期"
            
            # 按日期排序（最新的在前）
            sorted_records = sorted(filtered_records, 
                                  key=lambda x: x.get("date", x.get("datetime", "")), reverse=True)
            
            # 顯示統計資訊
            if sorted_records:
                # 計算統計
                period_income = sum(record["amount"] for record in sorted_records if record["type"] == "收入")
                period_expense = sum(record["amount"] for record in sorted_records if record["type"] == "支出")
                period_net = period_income - period_expense
                
                # 顯示統計
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("收入", f"NT$ {period_income}")
                with col2:
                    st.metric("支出", f"NT$ {period_expense}")
                with col3:
                    st.metric("淨收入", f"NT$ {period_net}")
                
                st.markdown(f"**{period_title}記錄：**")
            
            # 顯示記帳記錄（每行都有編輯和刪除按鈕）
            # 表頭
            with st.container():
                col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1, 1, 1, 2, 1, 1, 1, 1, 1, 1])
                
                with col1:
                    st.markdown("**日期**")
                with col2:
                    st.markdown("**類型**")
                with col3:
                    st.markdown("**類別**")
                with col4:
                    st.markdown("**細項**")
                with col5:
                    st.markdown("**金額**")
                with col6:
                    st.markdown("**地點**")
                with col7:
                    st.markdown("**購買人**")
                with col8:
                    st.markdown("**產品**")
                with col9:
                    st.markdown("**備註**")
                with col10:
                    st.markdown("**操作**")
            
            st.markdown("---")
            
            for i, record in enumerate(sorted_records):
                # 相容舊資料格式
                date_str = record.get('date', record.get('datetime', ''))
                if 'T' in date_str:  # 如果是datetime格式，只取日期部分
                    date_str = date_str.split('T')[0]
                record_date = datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
                type_icon = "💰" if record['type'] == "收入" else "💸"
                record_id = record.get('id', f'legacy_{i}')  # 相容舊資料
                
                # 處理產品顯示（支援舊格式和新格式）
                products = record.get('products', [])
                if not products:  # 相容舊格式
                    product = record.get('product', '')
                    products = [product] if product else []
                products_display = ", ".join(products) if products else ""
                
                # 檢查是否正在編輯此記錄
                is_editing = st.session_state.get('editing_record_id') == record_id
                
                if is_editing:
                    # 內嵌編輯表單
                    with st.container():
                        st.markdown("**📝 編輯記錄**")
                        with st.form(f"inline_edit_{record_id}"):
                            col_edit1, col_edit2 = st.columns(2)
                            
                            with col_edit1:
                                edit_date = st.date_input(
                                    "日期",
                                    value=datetime.fromisoformat(record['date']).date(),
                                    key=f"edit_date_{record_id}"
                                )
                                edit_type = st.selectbox(
                                    "類型",
                                    ["支出", "收入"],
                                    index=0 if record['type'] == "支出" else 1,
                                    key=f"edit_type_{record_id}"
                                )
                                edit_category = st.selectbox(
                                    "類別",
                                    st.session_state.custom_categories,
                                    index=st.session_state.custom_categories.index(record['category']) if record['category'] in st.session_state.custom_categories else 0,
                                    key=f"edit_category_{record_id}"
                                )
                                edit_description = st.text_input(
                                    "細項",
                                    value=record['description'],
                                    key=f"edit_description_{record_id}"
                                )
                                edit_amount = st.number_input(
                                    "金額 (NT$)",
                                    min_value=0.0,
                                    value=float(record['amount']),
                                    key=f"edit_amount_{record_id}"
                                )
                            
                            with col_edit2:
                                edit_location = st.text_input(
                                    "地點",
                                    value=record.get('location', ''),
                                    key=f"edit_location_{record_id}"
                                )
                                edit_buyer = st.text_input(
                                    "購買人",
                                    value=record.get('buyer', ''),
                                    key=f"edit_buyer_{record_id}"
                                )
                                
                                # 產品選擇
                                product_options = list(st.session_state.saved_recipes.keys())
                                current_products = record.get('products', [])
                                if not current_products:
                                    product = record.get('product', '')
                                    current_products = [product] if product else []
                                
                                edit_products = st.multiselect(
                                    "產品（可複選）",
                                    product_options,
                                    default=current_products,
                                    key=f"edit_products_{record_id}"
                                )
                                
                                edit_remark = st.text_area(
                                    "備註",
                                    value=record.get('remark', ''),
                                    height=80,
                                    key=f"edit_remark_{record_id}"
                                )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("💾 儲存", type="primary"):
                                    # 更新記錄
                                    record['date'] = edit_date.isoformat()
                                    record['type'] = edit_type
                                    record['category'] = edit_category
                                    record['description'] = edit_description
                                    record['amount'] = edit_amount
                                    record['location'] = edit_location
                                    record['buyer'] = edit_buyer
                                    record['products'] = edit_products
                                    record['remark'] = edit_remark
                                    
                                    save_accounting_data()
                                    st.session_state.editing_record_id = None
                                    st.success("✅ 記錄已更新")
                                    st.rerun()
                            
                            with col_cancel:
                                if st.form_submit_button("❌ 取消"):
                                    st.session_state.editing_record_id = None
                                    st.rerun()
                else:
                    # 正常顯示記錄
                    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([1, 1, 1, 2, 1, 1, 1, 1, 1, 1])
                    
                    with col1:
                        st.markdown(f"**{record_date}**")
                    with col2:
                        st.markdown(f"{type_icon} {record['type']}")
                    with col3:
                        st.markdown(f"{record['category']}")
                    with col4:
                        st.markdown(f"{record['description']}")
                    with col5:
                        st.markdown(f"NT$ {record['amount']}")
                    with col6:
                        st.markdown(f"{record.get('location', '')}")
                    with col7:
                        st.markdown(f"{record.get('buyer', '')}")
                    with col8:
                        st.markdown(f"{products_display}")
                    with col9:
                        st.markdown(f"{record.get('remark', '')}")
                    with col10:
                        # 編輯和刪除按鈕
                        col_edit, col_delete = st.columns(2)
                        with col_edit:
                            if st.button("✏️", key=f"edit_{record_id}", help="編輯此記錄", use_container_width=True):
                                st.session_state.editing_record_id = record_id
                                st.rerun()
                        with col_delete:
                            # 檢查是否在刪除確認狀態
                            if st.session_state.get(f"show_delete_modal_{record_id}", False):
                                st.warning("⚠️ 確定要刪除這筆記錄嗎？")
                                col_confirm, col_cancel = st.columns(2)
                                with col_confirm:
                                    if st.button("✅", key=f"confirm_del_{record_id}", help="確認刪除", use_container_width=True):
                                        # 執行刪除
                                        st.session_state.accounting_records = [
                                            r for r in st.session_state.accounting_records 
                                            if r.get('id', '') != record_id
                                        ]
                                        save_accounting_data()
                                        st.session_state[f"show_delete_modal_{record_id}"] = False
                                        st.success("✅ 記錄已刪除")
                                        st.rerun()
                                with col_cancel:
                                    if st.button("❌", key=f"cancel_del_{record_id}", help="取消刪除", use_container_width=True):
                                        st.session_state[f"show_delete_modal_{record_id}"] = False
                                        st.rerun()
                            else:
                                if st.button("🗑️", key=f"del_{record_id}", help="刪除此記錄", use_container_width=True):
                                    # 設定刪除確認狀態
                                    st.session_state[f"show_delete_modal_{record_id}"] = True
                                    st.rerun()
                
                # 添加分隔線
                st.markdown("---")
        
        else:  # 購買人紀錄
            st.markdown("#### 購買人紀錄")
            
            # 獲取所有購買人（只從支出記錄中）
            all_buyers = set()
            for record in st.session_state.accounting_records:
                if record["type"] == "支出":  # 只包含支出記錄
                    buyer = record.get('buyer', '')
                    if buyer:  # 只包含有購買人的記錄
                        all_buyers.add(buyer)
            
            if all_buyers:
                # 選擇購買人
                selected_buyer = st.selectbox(
                    "選擇購買人",
                    sorted(list(all_buyers)),
                    label_visibility="collapsed"
                )
                
                # 篩選該購買人的支出記錄
                buyer_records = [
                    record for record in st.session_state.accounting_records 
                    if record.get('buyer', '') == selected_buyer and record["type"] == "支出"
                ]
                
                if buyer_records:
                    # 計算購買人統計（只計算支出）
                    buyer_total_expense = sum(record["amount"] for record in buyer_records)
                    buyer_record_count = len(buyer_records)
                    
                    # 顯示購買人統計
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("購買次數", buyer_record_count)
                    with col2:
                        st.metric("總支出", f"NT$ {buyer_total_expense}")
                    
                    # 按類別統計
                    st.markdown("---")
                    st.markdown("#### 按類別統計")
                    
                    category_stats = {}
                    for record in buyer_records:
                        category = record['category']
                        amount = record['amount']
                        
                        if category not in category_stats:
                            category_stats[category] = {'expense': 0, 'count': 0}
                        
                        category_stats[category]['expense'] += amount
                        category_stats[category]['count'] += 1
                    
                    # 顯示類別統計表格
                    category_data = []
                    for category, stats in category_stats.items():
                        category_data.append({
                            "類別": category,
                            "購買次數": stats['count'],
                            "支出金額": f"NT$ {stats['expense']}"
                        })
                    
                    if category_data:
                        df_category = pd.DataFrame(category_data)
                        st.dataframe(
                            df_category,
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    # 顯示購買人詳細記錄
                    st.markdown("---")
                    st.markdown("#### 詳細記錄")
                    
                    # 篩選選項
                    filter_category = st.selectbox(
                        "篩選類別",
                        ["全部"] + sorted(list(set(record['category'] for record in buyer_records))),
                        label_visibility="collapsed"
                    )
                    
                    # 應用篩選
                    filtered_records = buyer_records
                    if filter_category != "全部":
                        filtered_records = [r for r in filtered_records if r['category'] == filter_category]
                    
                    # 顯示篩選後的記錄
                    if filtered_records:
                        # 按日期排序
                        sorted_filtered_records = sorted(filtered_records, 
                                                       key=lambda x: x.get("date", x.get("datetime", "")), reverse=True)
                        
                        # 顯示記錄表格
                        filtered_table_data = []
                        for record in sorted_filtered_records:
                            date_str = record.get('date', record.get('datetime', ''))
                            if 'T' in date_str:
                                date_str = date_str.split('T')[0]
                            record_date = datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
                            type_icon = "💰" if record['type'] == "收入" else "💸"
                            
                            filtered_table_data.append({
                                "日期": record_date,
                                "類別": record['category'],
                                "細項": record['description'],
                                "金額": f"NT$ {record['amount']}",
                                "地點": record.get('location', ''),
                                "備註": record.get('remark', '')
                            })
                        
                        df_filtered = pd.DataFrame(filtered_table_data)
                        st.dataframe(
                            df_filtered,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # 顯示篩選統計
                        filtered_expense = sum(record["amount"] for record in filtered_records)
              
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("篩選次數", len(filtered_records))
                        with col2:
                            st.metric("篩選支出", f"NT$ {filtered_expense}")
                    else:
                        st.info("沒有符合篩選條件的記錄")
                else:
                    st.info(f"沒有 {selected_buyer} 的購買記錄")
            else:
                st.info("沒有購買人資料，請先在記帳時填寫購買人欄位")

    # 批量操作（只在記帳記錄模式顯示）
    if st.session_state.accounting_records and display_mode == "記帳記錄":
        st.markdown("---")
        st.markdown("#### 批量操作")

        if st.button("清除所有記錄", type="secondary", use_container_width=True, key="clear_all_records"):
            st.warning("⚠️ 確定要清除所有記帳記錄嗎？此操作無法復原！")
            col_confirm, col_cancel = st.columns(2)
            with col_confirm:
                if st.button("確認清除", type="secondary", use_container_width=True, key="confirm_clear_all"):
                    st.session_state.accounting_records = []
                    save_accounting_data()
                    st.success("✅ 已清除所有記帳記錄")
                    st.rerun()
            with col_cancel:
                if st.button("取消", type="secondary", use_container_width=True, key="cancel_clear_all"):
                    st.info("❌ 已取消清除所有記錄")
                    st.rerun()

    # 總收支總結
    if st.session_state.accounting_records:
        st.markdown("---")
        st.markdown("### 📊 總收支總結")

        # 計算總收入和總支出
        total_income = sum(record["amount"] for record in st.session_state.accounting_records if record["type"] == "收入")
        total_expense = sum(record["amount"] for record in st.session_state.accounting_records if record["type"] == "支出")
        net_income = total_income - total_expense

        # 顯示總結
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div style="background-color: #d4edda; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: #155724; margin: 0;">💰 總收入</h4>
                <h2 style="color: #155724; margin: 10px 0;">NT$ {total_income}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: #721c24; margin: 0;">💸 總支出</h4>
                <h2 style="color: #721c24; margin: 10px 0;">NT$ {total_expense}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            net_color = "#155724" if net_income >= 0 else "#721c24"
            net_icon = "↗️" if net_income >= 0 else "↘️"
            st.markdown(f"""
            <div style="background-color: {'#d4edda' if net_income >= 0 else '#f8d7da'}; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: {net_color}; margin: 0;">{net_icon} 淨收入</h4>
                <h2 style="color: {net_color}; margin: 10px 0;">NT$ {net_income}</h2>
            </div>
            """, unsafe_allow_html=True)

# 頁腳
st.markdown('</div>', unsafe_allow_html=True)
