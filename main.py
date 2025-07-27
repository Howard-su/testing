import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
import os

# 添加缓存装饰器
@st.cache_data
def get_material_options(materials_dict):
    """缓存材料选项列表，避免重复计算"""
    return list(materials_dict.keys())

# 設定頁面配置
st.set_page_config(
    page_title="Gwen的材料成本計算",
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
                return json.load(f)
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
    <h1>Gwen 的材料成本計算器</h1>
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
        
        # 使用复选框選擇材料
        selected_materials = []
        
        # 創建兩列布局來顯示材料選項
        col1, col2 = st.columns(2)
        
        for i, material in enumerate(material_options):
            # 交替分配到兩列
            with col1 if i % 2 == 0 else col2:
                # 檢查是否已選中
                is_selected = material in st.session_state.selected_materials
                
                # 使用复选框
                price_display = st.session_state.saved_materials[material]
                if price_display == int(price_display):
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
                    st.session_state.selected_materials = material_options.copy()
                    st.rerun()

            with col_clear_all:
                if st.button("清除選擇", use_container_width=True, key="clear_all_btn"):
                    st.session_state.selected_materials = []
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
                    if price_display == int(price_display):
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
                    
                    # 轉換為數字
                    try:
                        weight = float(weight) if weight else 0.0
                    except ValueError:
                        weight = 0.0
                    
                    # 只在重量改變時更新session state
                    if weight != current_weight:
                        st.session_state.material_weights[material] = weight
                    
                    # 計算單個材料成本
                    material_cost = weight * price
                    total_cost += material_cost
                    recipe_materials[material] = {
                        "weight": weight,
                        "price": price,
                        "cost": material_cost
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
                    # 顯示計算結果
                    st.markdown("---")
                    st.markdown("### 計算結果")
                    
                    # 顯示每個材料的詳細信息
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
                
                # 顯示保存成功消息
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
                        # 保存食譜
                        recipe_data = {
                            "materials": recipe_materials,
                            "total_cost": total_cost,
                            "created_at": datetime.now().isoformat()
                        }
                        st.session_state.saved_recipes[recipe_name] = recipe_data
                        save_recipes_data()
                        
                        # 設置成功狀態
                        st.session_state.show_save_success = True
                        st.session_state.saved_recipe_name = recipe_name
                        st.rerun()
                else:
                    st.info("請先輸入食譜名稱才能保存")
    else:
        st.markdown("""
        <div class="warning-message">
            <h4>尚未新增材料</h4>
            <p>請先在「材料管理」頁面新增您常用的材料。</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "材料管理":
    # 材料管理頁面
    st.markdown("### 材料管理")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 新增材料")
        
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
                    value=1.0, 
                    step=0.01,
                    help="輸入每克的價格",
                    label_visibility="visible"
                )
                
                submitted = st.form_submit_button("儲存材料", type="primary", use_container_width=True)
                if submitted:
                    if material_name:
                        st.session_state.saved_materials[material_name] = price_per_100g
                        save_materials_data()
                        st.markdown(f"""
                        <div class="success-message">
                            <strong>成功！</strong> 已儲存 {material_name}
                        </div>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("請輸入材料名稱！")

            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### 已儲存材料")

        if st.session_state.saved_materials:
            # 材料列表
            for i, (material, price) in enumerate(st.session_state.saved_materials.items()):
                price_display = price
                if price_display == int(price_display):
                    price_display = int(price_display)

                with st.container():
                    st.markdown(f"""
                    <div class="material-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{material}</strong><br>
                                <small>NT$ {price_display} / 1g</small>
                            </div>
                            <div>
                                <button onclick="deleteMaterial('{material}')" style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 4px 8px; cursor: pointer;">刪除</button>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 實際的刪除按鈕（隱藏）
                    if st.button("刪除", key=f"del_{material}", help=f"刪除 {material}"):
                        del st.session_state.saved_materials[material]
                        save_materials_data()
                        st.success(f"已刪除 {material}")
                        st.rerun()
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
        
        if st.button("清除所有材料", type="secondary", use_container_width=True):
            st.session_state.saved_materials = {}
            save_materials_data()
            st.success("已清除所有材料")
            st.rerun()
        
        if st.button("切換到成本計算", use_container_width=True):
            st.session_state.current_page = "成本計算"
            st.rerun()

elif st.session_state.current_page == "食譜區":
    # 食譜區頁面
    st.markdown("### 食譜區")
    
    if st.session_state.saved_recipes:
        # 顯示已保存的食譜
        for recipe_name, recipe_data in st.session_state.saved_recipes.items():
            total_cost_display = recipe_data['total_cost']
            if total_cost_display == int(total_cost_display):
                total_cost_display = int(total_cost_display)
            else:
                total_cost_display = f"{recipe_data['total_cost']:.2f}"
            
            with st.expander(f"📖 {recipe_name} - NT$ {total_cost_display}", expanded=False):
                # 顯示食譜詳細信息
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
                col_use, col_delete = st.columns(2)
                with col_use:
                    if st.button("使用此食譜", key=f"use_{recipe_name}", use_container_width=True):
                        # 將食譜材料載入到成本計算頁面
                        st.session_state.selected_materials = list(recipe_data['materials'].keys())
                        st.session_state.material_weights = {
                            material: data['weight'] 
                            for material, data in recipe_data['materials'].items()
                        }
                        st.session_state.current_page = "成本計算"
                        st.rerun()

                with col_delete:
                    if st.button("刪除食譜", key=f"del_recipe_{recipe_name}", use_container_width=True):
                        del st.session_state.saved_recipes[recipe_name]
                        save_recipes_data()
                        st.success(f"已刪除食譜「{recipe_name}」")
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
            # 日期和時間選擇
            record_date = st.date_input(
                "日期",
                value=datetime.now().date(),
                label_visibility="visible"
            )
            
            record_time = st.time_input(
                "時間",
                value=datetime.now().time(),
                label_visibility="visible"
            )
            
            # 收入/支出選擇
            transaction_type = st.selectbox(
                "類型",
                ["支出", "收入"],
                label_visibility="visible"
            )
            
            # 類別選擇
            category = st.selectbox(
                "類別",
                ["食材", "設備", "包裝", "運輸", "其他"],
                label_visibility="visible"
            )
            
            # 描述
            description = st.text_input(
                "描述",
                placeholder="例如：購買麵粉、運費、銷售收入...",
                label_visibility="visible"
            )
            
            # 金額
            amount = st.number_input(
                "金額 (NT$)",
                min_value=0.0,
                value=0.0,
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
            
            submitted = st.form_submit_button("新增記帳", type="primary", use_container_width=True)
            if submitted:
                if description and amount > 0:
                    # 組合日期和時間
                    record_datetime = datetime.combine(record_date, record_time)
                    
                    # 新增記帳記錄
                    record = {
                        "datetime": record_datetime.isoformat(),
                        "type": transaction_type,
                        "category": category,
                        "description": description,
                        "amount": amount,
                        "location": location,
                        "buyer": buyer,
                        "created_at": datetime.now().isoformat()
                    }
                    st.session_state.accounting_records.append(record)
                    save_accounting_data()
                    st.success(f"✅ 記帳成功！{transaction_type} - {description} - NT$ {amount}")
                    st.rerun()
                else:
                    st.error("請輸入描述和金額！")
    
    with col2:
        st.markdown("#### 記帳統計")
        
        if st.session_state.accounting_records:
            # 計算總收入和總支出
            total_income = sum(record["amount"] for record in st.session_state.accounting_records if record["type"] == "收入")
            total_expense = sum(record["amount"] for record in st.session_state.accounting_records if record["type"] == "支出")
            
            # 按類別統計
            category_stats = {}
            for record in st.session_state.accounting_records:
                cat = record["category"]
                if cat not in category_stats:
                    category_stats[cat] = {"收入": 0, "支出": 0}
                category_stats[cat][record["type"]] += record["amount"]
            
            # 顯示統計
            col_income, col_expense = st.columns(2)
            with col_income:
                st.metric("總收入", f"NT$ {total_income}")
            with col_expense:
                st.metric("總支出", f"NT$ {total_expense}")
            
            st.markdown("---")
            st.markdown("**按類別統計：**")
            for cat, amounts in category_stats.items():
                income = amounts["收入"]
                expense = amounts["支出"]
                if income > 0 or expense > 0:
                    st.markdown(f"• {cat}: 收入 NT$ {income} | 支出 NT$ {expense}")
        else:
            st.info("尚未有任何記帳記錄")
    
    # 記帳記錄列表
    if st.session_state.accounting_records:
        st.markdown("---")
        st.markdown("#### 記帳記錄")
        
        # 按時間排序（最新的在前）
        sorted_records = sorted(st.session_state.accounting_records, 
                              key=lambda x: x["datetime"], reverse=True)
        
        for i, record in enumerate(sorted_records):
            # 格式化時間顯示
            record_time = datetime.fromisoformat(record['datetime']).strftime("%Y-%m-%d %H:%M")
            type_icon = "💰" if record['type'] == "收入" else "💸"
            
            with st.expander(f"{type_icon} {record_time} - {record['description']} - NT$ {record['amount']}", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**時間：** {record_time}")
                    st.markdown(f"**類型：** {record['type']}")
                    st.markdown(f"**類別：** {record['category']}")
                with col2:
                    st.markdown(f"**描述：** {record['description']}")
                    st.markdown(f"**金額：** NT$ {record['amount']}")
                with col3:
                    st.markdown(f"**地點：** {record.get('location', '未填寫')}")
                    st.markdown(f"**購買人：** {record.get('buyer', '未填寫')}")
                
                # 刪除按鈕
                if st.button("刪除記錄", key=f"del_record_{i}", use_container_width=True):
                    st.session_state.accounting_records.pop(i)
                    save_accounting_data()
                    st.success("記錄已刪除")
                    st.rerun()
    
    # 批量操作
    if st.session_state.accounting_records:
        st.markdown("---")
        st.markdown("#### 批量操作")
        
        if st.button("清除所有記錄", type="secondary", use_container_width=True):
            st.session_state.accounting_records = []
            save_accounting_data()
            st.success("已清除所有記帳記錄")
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
            net_icon = "📈" if net_income >= 0 else "📉"
            st.markdown(f"""
            <div style="background-color: {'#d4edda' if net_income >= 0 else '#f8d7da'}; padding: 15px; border-radius: 10px; text-align: center;">
                <h4 style="color: {net_color}; margin: 0;">{net_icon} 淨收入</h4>
                <h2 style="color: {net_color}; margin: 10px 0;">NT$ {net_income}</h2>
            </div>
            """, unsafe_allow_html=True)

# 頁腳
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p>Gwen 的材料成本計算器 | 簡潔高效的食材管理工具</p>
        <p style='font-size: 0.8em;'>單價請輸入每克的價格 | 資料會自動保存</p>
    </div>
    """,
    unsafe_allow_html=True
)