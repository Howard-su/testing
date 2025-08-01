import streamlit as st
import pandas as pd
import json
import base64
import uuid
from datetime import datetime, timezone, timedelta
import os

# 設定台灣時區
TAIWAN_TZ = timezone(timedelta(hours=8))

def get_taiwan_time():
    """取得台灣時間"""
    return datetime.now(TAIWAN_TZ)

# 添加快取裝飾器
@st.cache_data
def get_material_options(materials_dict):
    """快取材料選項列表，避免重複計算"""
    return list(materials_dict.keys())

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

# 載入已儲存的材料資料
def load_saved_materials():
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
        # 直接儲存，不使用 base64 編碼
        with open('saved_materials.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.saved_materials, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存材料資料時發生錯誤：{e}")

 
# 載入已儲存的食譜資料
def load_saved_recipes():
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
        with open('saved_recipes.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.saved_recipes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存食譜資料時發生錯誤：{e}")


# 載入記帳資料
def load_accounting_data():
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
        with open('accounting_records.json', 'w', encoding='utf-8') as f:
            json.dump(st.session_state.accounting_records, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"儲存記帳資料時發生錯誤：{e}")


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

# 側邊欄 - 頁面選擇
with st.sidebar:
    st.markdown('<div class="sidebar-container">', unsafe_allow_html=True)
    st.markdown("### 功能選單")
    
    # 頁面選擇器
    page_options = ["成本計算", "材料管理", "食譜區", "記帳區"]
    page_index = 0 if st.session_state.current_page == "成本計算" else (1 if st.session_state.current_page == "材料管理" else (2 if st.session_state.current_page == "食譜區" else 3))
    
    page = st.selectbox(
        "選擇功能",
        page_options,
        index=page_index,
        label_visibility="collapsed",
        key="page_selector"
    )

    # 更新當前頁面
    if page != st.session_state.current_page:
        st.session_state.current_page = page
        st.rerun()

    # 顯示統計資訊
    if st.session_state.saved_materials:
        st.markdown("---")
        st.markdown("### 材料統計")
        st.metric("已儲存材料", len(st.session_state.saved_materials))

        # 顯示最近新增的材料
        if st.session_state.saved_materials:
            recent_materials = list(st.session_state.saved_materials.keys())[-3:]
            st.markdown("**最近新增：**")
            for material in recent_materials:
                st.markdown(f"• {material}")
    

    
    # 新增資料匯出功能
    st.markdown("---")
    st.markdown("### 📤 資料匯出")
    if st.button("📥 下載所有資料", key="download_btn"):
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

                if st.checkbox(
                    f"{material} (NT$ {price_display}/g)",
                    value=is_selected,
                    key=f"checkbox_{material}"
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
                if st.button("清除選擇", use_container_width=True, key="clear_all_btn"):
                    if not st.session_state.selected_materials:
                        st.info("✅ 已經沒有選擇任何材料")
                    else:
                        st.warning("⚠️ 確定要清除所有選擇嗎？")
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("確認清除", key="confirm_clear_all", use_container_width=True):
                                st.session_state.selected_materials = []
                                st.success("✅ 已清除所有選擇")
                                st.rerun()
                        with col_cancel:
                            if st.button("取消", key="cancel_clear_all", use_container_width=True):
                                st.info("❌ 已取消清除操作")
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
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{material}</h4>
                        <p><strong>單價：</strong>NT$ {price_display} / 1g</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # 輸入克數
                    current_weight = st.session_state.material_weights.get(material, 0.0)
                    weight = st.text_input(
                        f"{material} 克數 (g)", 
                        value=str(current_weight) if current_weight > 0 else "",
                        key=f"weight_{material}",
                        help=f"請輸入 {material} 的重量（克）",
                        label_visibility="collapsed",
                        placeholder="克數"
                    )
                    
                    # 輸入熟成率（可選）
                    current_yield_rate = st.session_state.material_yield_rates.get(
                        material, ""
                    )
                    help_text = (f"請輸入 {material} 的熟成率（例如：0.8 表示 80%），"
                                f"留空則不計算熟成率")
                    yield_rate = st.text_input(
                        f"{material} 熟成率", 
                        value=current_yield_rate,
                        key=f"yield_rate_{material}",
                        help=help_text,
                        label_visibility="collapsed",
                        placeholder="熟成率（可選）"
                    )
                    
                    # 轉換為數字
                    try:
                        weight = float(weight) if weight else 0.0
                    except ValueError:
                        weight = 0.0
                    
                    try:
                        yield_rate = float(yield_rate) if yield_rate else None
                    except ValueError:
                        yield_rate = None
                    
                    # 只在重量改變時更新session state
                    if weight != current_weight:
                        st.session_state.material_weights[material] = weight
                    
                    # 只在熟成率改變時更新session state
                    if yield_rate != current_yield_rate:
                        st.session_state.material_yield_rates[material] = yield_rate if yield_rate is not None else ""
                    
                    # 計算單個材料成本（考慮熟成率）
                    if yield_rate is not None and yield_rate > 0:
                        # 使用熟成率計算：重量 / 熟成率 * 單價
                        adjusted_weight = weight / yield_rate
                        material_cost = adjusted_weight * price
                    else:
                        # 原本的計算：重量 * 單價
                        material_cost = weight * price
                    
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
                            # 如果有熟成率，顯示更多資訊
                            if data['yield_rate'] is not None and data['yield_rate'] > 0:
                                col1_result, col2_result, col3_result, col4_result, col5_result = st.columns(5)
                                with col1_result:
                                    st.metric("材料", material)
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
                                st.markdown(f"**{material}** 調整後重量：{data['adjusted_weight']:.1f} g (原重量 ÷ 熟成率)")
                            else:
                                col1_result, col2_result, col3_result, col4_result = st.columns(4)
                                with col1_result:
                                    st.metric("材料", material)
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
                    value=st.session_state.editing_price, 
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
                    elif edited_price is None or edited_price <= 0:
                        st.error("請輸入有效的單價（必須大於0）！")
                    else:
                        # 如果名稱改變，需要檢查是否已存在
                        if edited_name != st.session_state.editing_material and edited_name in st.session_state.saved_materials:
                            st.error("材料名稱已存在！")
                        else:
                            # 刪除舊材料，添加新材料
                            del st.session_state.saved_materials[st.session_state.editing_material]
                            st.session_state.saved_materials[edited_name] = edited_price
                            save_materials_data()
                            st.session_state.editing_material = None
                            st.session_state.editing_price = None
                            st.success(f"✅ 已更新材料「{edited_name}」")
                            st.rerun()
        
        # 新增材料表單
        with st.container():
            st.markdown('<div class="form-container">', unsafe_allow_html=True)
            
            with st.form("add_material_form"):
                material_name = st.text_input(
                    "材料名稱",
                    label_visibility="visible"
                )
                price_per_100g = st.number_input(
                    "單價 (每g，NT$)", 
                    min_value=0.0, 
                    value=None, 
                    step=0.01,
                    help="輸入每克的價格",
                    label_visibility="visible"
                )
                
                submitted = st.form_submit_button("儲存材料", type="primary", use_container_width=True)
                if submitted:
                    if not material_name:
                        st.error("請輸入材料名稱！")
                    elif price_per_100g is None or price_per_100g <= 0:
                        st.error("請輸入有效的單價（必須大於0）！")
                    else:
                        st.session_state.saved_materials[material_name] = price_per_100g
                        save_materials_data()
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
        with st.expander(f"📋 查看所有材料 ({material_count} 個)", expanded=False):
            # 計算每行顯示的材料數量（並排顯示）
            materials_per_row = 2
            
            # 分批顯示材料
            for i in range(0, len(sorted_materials), materials_per_row):
                row_materials = sorted_materials[i:i + materials_per_row]
                cols = st.columns(materials_per_row)
                
                for j, (material, price) in enumerate(row_materials):
                    with cols[j]:
                        price_display = price
                        if price_display is not None and price_display == int(price_display):
                            price_display = int(price_display)

                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                            border-radius: 12px;
                            padding: 16px;
                            margin: 8px 0;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                            border: 2px solid #f8d7da;
                            transition: all 0.3s ease;
                        ">
                            <div style="
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                text-align: center;
                                color: #8b4513;
                            ">
                                <div style="
                                    font-size: 18px;
                                    font-weight: bold;
                                    margin-bottom: 8px;
                                    text-shadow: 1px 1px 2px rgba(139,69,19,0.2);
                                ">
                                    📦 {material}
                                </div>
                                <div style="
                                    font-size: 14px;
                                    background: rgba(255,255,255,0.6);
                                    padding: 4px 8px;
                                    border-radius: 6px;
                                    backdrop-filter: blur(5px);
                                    color: #8b4513;
                                    font-weight: 500;
                                ">
                                    NT$ {price_display} / 1g
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 編輯、移動和刪除按鈕
                        st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)
                        col_edit, col_move_up, col_move_down, col_delete = st.columns(4)
                        
                        with col_edit:
                            if st.button("✏️ 編輯", key=f"edit_{material}", help=f"編輯 {material}", use_container_width=True, type="secondary"):
                                st.session_state.editing_material = material
                                st.session_state.editing_price = price
                                st.rerun()
                        
                        with col_move_up:
                            if st.button("⬆️ 上移", key=f"move_up_{material}", help=f"上移 {material}", use_container_width=True, type="secondary"):
                                # 初始化自訂順序
                                if not hasattr(st.session_state, 'custom_material_order'):
                                    st.session_state.custom_material_order = list(st.session_state.saved_materials.keys())
                                
                                # 移動材料
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
                                    st.success(f"✅ 已上移材料「{material}」")
                                    st.rerun()
                                else:
                                    st.info("📌 已經是第一個材料")
                        
                        with col_move_down:
                            if st.button("⬇️ 下移", key=f"move_down_{material}", help=f"下移 {material}", use_container_width=True, type="secondary"):
                                # 初始化自訂順序
                                if not hasattr(st.session_state, 'custom_material_order'):
                                    st.session_state.custom_material_order = list(st.session_state.saved_materials.keys())
                                
                                # 移動材料
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
                                    st.success(f"✅ 已下移材料「{material}」")
                                    st.rerun()
                                else:
                                    st.info("📌 已經是最後一個材料")
                        
                        with col_delete:
                            # 檢查是否在確認刪除狀態
                            if f"confirming_delete_{material}" not in st.session_state:
                                st.session_state[f"confirming_delete_{material}"] = False
                            
                            if not st.session_state[f"confirming_delete_{material}"]:
                                if st.button("🗑️ 刪除", key=f"del_{material}", help=f"刪除 {material}", use_container_width=True, type="secondary"):
                                    st.session_state[f"confirming_delete_{material}"] = True
                                    st.rerun()
                            else:
                                st.warning(f"⚠️ 確定要刪除材料「{material}」嗎？")
                                col_confirm, col_cancel = st.columns(2)
                                with col_confirm:
                                    if st.button("確認刪除", key=f"confirm_del_{material}", help=f"確認刪除 {material}", use_container_width=True):
                                        # 直接刪除材料
                                        del st.session_state.saved_materials[material]
                                        # 同時從自訂順序中移除
                                        if hasattr(st.session_state, 'custom_material_order') and material in st.session_state.custom_material_order:
                                            st.session_state.custom_material_order.remove(material)
                                        save_materials_data()
                                        st.session_state[f"confirming_delete_{material}"] = False
                                        st.success(f"✅ 已刪除材料「{material}」")
                                        st.rerun()
                                with col_cancel:
                                    if st.button("取消", key=f"cancel_del_{material}", help=f"取消刪除 {material}", use_container_width=True):
                                        st.session_state[f"confirming_delete_{material}"] = False
                                        st.info(f"❌ 已取消刪除材料「{material}」")
                                        st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.markdown("<div style='margin: 16px 0; border-bottom: 1px solid #e0e0e0;'></div>", unsafe_allow_html=True)
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
        
        if st.button("切換到成本計算", use_container_width=True):
            st.info("🔄 正在切換到成本計算頁面...")
            st.session_state.current_page = "成本計算"
            st.rerun()

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
            
            # 顯示材料列表（唯讀）
            st.markdown("#### 材料清單（不可編輯）")
            recipe_data = st.session_state.editing_recipe_data
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
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                submitted = st.form_submit_button("儲存修改", type="primary", use_container_width=True)
            with col_cancel:
                if st.form_submit_button("取消編輯", use_container_width=True):
                    st.session_state.editing_recipe = None
                    st.session_state.editing_recipe_data = None
                    st.rerun()
            
            if submitted:
                if edited_recipe_name:
                    # 如果名稱改變，需要檢查是否已存在
                    if edited_recipe_name != st.session_state.editing_recipe and edited_recipe_name in st.session_state.saved_recipes:
                        st.error("食譜名稱已存在！")
                    else:
                        # 更新食譜名稱
                        old_name = st.session_state.editing_recipe
                        recipe_data = st.session_state.saved_recipes[old_name]
                        del st.session_state.saved_recipes[old_name]
                        st.session_state.saved_recipes[edited_recipe_name] = recipe_data
                        save_recipes_data()
                        st.session_state.editing_recipe = None
                        st.session_state.editing_recipe_data = None
                        st.success(f"✅ 已更新食譜名稱為「{edited_recipe_name}」")
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
            
            with st.expander(f"📖 {recipe_name} - NT$ {total_cost_display}", expanded=False):
                # 顯示食譜詳細資訊
                st.markdown(f"**創建時間：** {recipe_data['created_at'][:19]}")
                st.markdown("---")
                
                # 顯示材料列表
                st.markdown("#### 材料清單")
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
                        st.rerun()

                with col_delete:
                    if st.button("🗑️ 刪除", key=f"del_recipe_{recipe_name}", use_container_width=True):
                        st.warning(f"⚠️ 確定要刪除食譜「{recipe_name}」嗎？此操作無法復原！")
                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("確認刪除", key=f"confirm_del_recipe_{recipe_name}", use_container_width=True):
                                del st.session_state.saved_recipes[recipe_name]
                                save_recipes_data()
                                st.success(f"✅ 已刪除食譜「{recipe_name}」")
                                st.rerun()
                        with col_cancel:
                            if st.button("取消", key=f"cancel_del_recipe_{recipe_name}", use_container_width=True):
                                st.info(f"❌ 已取消刪除食譜「{recipe_name}」")
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
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 新增記帳")
        
        # 新增記帳表單
        with st.form("add_accounting_form"):
            # 日期選擇
            record_date = st.date_input(
                "日期",
                value=datetime.now().date(),
                label_visibility="visible"
            )
            
            # 收入/支出選擇
            transaction_type = st.selectbox(
                "類型",
                ["支出", "收入"],
                label_visibility="visible"
            )
            
            # 類別選擇
            category_options = ["食材", "設備", "包裝", "運輸", "食譜", "其他"]
            category = st.selectbox(
                "類別",
                category_options,
                label_visibility="visible"
            )
            
            # 細項
            description = st.text_input(
                "細項",
                placeholder="例如：購買麵粉、運費、銷售收入...",
                label_visibility="visible"
            )
            
            # 金額
            amount = st.number_input(
                "金額 (NT$)",
                min_value=0.0,
                value=None,
                step=1.0,
                label_visibility="visible"
            )
            
            # 地點
            location = st.text_input(
                "地點",
                placeholder="例如：超市、網購、實體店...",
                label_visibility="visible"
            )
            
            # 購買人
            buyer = st.text_input(
                "購買人",
                placeholder="例如：張三、李四...",
                label_visibility="visible"
            )
            
            # 食譜區欄位
            recipe_area = st.text_input(
                "食譜區",
                placeholder="例如：巧克力蛋糕、麵包、餅乾...",
                label_visibility="visible"
            )
            
            # 備註（非必填）
            remark = st.text_area(
                "備註",
                placeholder="額外說明（非必填）...",
                label_visibility="visible",
                height=80
            )
            
            submitted = st.form_submit_button("新增記帳", type="primary", use_container_width=True)
            if submitted:
                if description and amount > 0 and category:
                    # 生成唯一ID
                    record_id = str(uuid.uuid4())
                    
                    # 新增記帳記錄
                    record = {
                        "id": record_id,
                        "date": record_date.isoformat(),
                        "type": transaction_type,
                        "category": category,
                        "description": description,
                        "amount": amount,
                        "location": location,
                        "buyer": buyer,
                        "recipe_area": recipe_area,
                        "remark": remark,
                        "created_at": get_taiwan_time().isoformat()
                    }
                    st.session_state.accounting_records.append(record)
                    save_accounting_data()
                    st.success(f"✅ 記帳成功！{transaction_type} - {description} - NT$ {amount}")
                    st.rerun()
                else:
                    st.error("請輸入細項、金額和類別！")
    
    with col2:
        st.markdown("#### 記帳統計")
        
        if st.session_state.accounting_records:
            # 計算總收入和總支出
            total_income = sum(record["amount"] for record in st.session_state.accounting_records if record["type"] == "收入")
            total_expense = sum(record["amount"] for record in st.session_state.accounting_records if record["type"] == "支出")

    
            # 顯示統計
            col_income, col_expense = st.columns(2)
            with col_income:
                st.metric("總收入", f"NT$ {total_income}")
            with col_expense:
                st.metric("總支出", f"NT$ {total_expense}")
            
            st.markdown("---")

        else:
            st.info("尚未有任何記帳記錄")
    
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
            
            # 食譜區篩選
            # 獲取所有食譜區的值
            all_recipe_areas = set()
            for record in st.session_state.accounting_records:
                recipe_area = record.get('recipe_area', '')
                if recipe_area:  # 只包含有食譜區的記錄
                    all_recipe_areas.add(recipe_area)
            
            # 食譜區選擇（始終顯示）
            recipe_area_filter = st.selectbox(
                "食譜區篩選",
                ["全部食譜區"] + sorted(list(all_recipe_areas)),
                label_visibility="collapsed"
            )
            
            # 根據篩選條件過濾記錄
            filtered_records = st.session_state.accounting_records
            if record_filter == "總收入紀錄":
                filtered_records = [r for r in st.session_state.accounting_records if r["type"] == "收入"]
            elif record_filter == "總支出紀錄":
                filtered_records = [r for r in st.session_state.accounting_records if r["type"] == "支出"]
            
            # 根據食譜區篩選
            if recipe_area_filter != "全部食譜區":
                filtered_records = [r for r in filtered_records if r.get('recipe_area', '') == recipe_area_filter]
            
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
            
            # 顯示記帳記錄（每行都有刪除按鈕）
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
                    st.markdown("**食譜區**")
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
                
                # 創建記錄行
                with st.container():
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
                        st.markdown(f"{record.get('recipe_area', '')}")
                    with col9:
                        st.markdown(f"{record.get('remark', '')}")
                    with col10:
                        # 刪除按鈕
                        if st.button("🗑️", key=f"del_{record_id}", help="刪除此記錄", use_container_width=True):
                            st.warning(f"⚠️ 確定要刪除這筆記錄嗎？")
                            col_confirm, col_cancel = st.columns(2)
                            with col_confirm:
                                if st.button("確認刪除", key=f"confirm_del_{record_id}", help="確認刪除此記錄", use_container_width=True):
                                    # 根據ID刪除記錄
                                    st.session_state.accounting_records = [
                                        r for r in st.session_state.accounting_records 
                                        if r.get('id', '') != record_id
                                    ]
                                    save_accounting_data()
                                    st.success("✅ 記錄已刪除")
                                    st.rerun()
                            with col_cancel:
                                if st.button("取消", key=f"cancel_del_{record_id}", help="取消刪除此記錄", use_container_width=True):
                                    st.info("❌ 已取消刪除記錄")
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
