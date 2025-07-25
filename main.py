import streamlit as st
import pandas as pd
import json
import base64
from datetime import datetime
import os

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

# 載入已儲存的材料
if not st.session_state.saved_materials:
    st.session_state.saved_materials = load_saved_materials()

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
    page = st.selectbox(
        "選擇功能",
        ["成本計算", "材料管理"],
        index=0 if st.session_state.current_page == "成本計算" else 1,
        label_visibility="collapsed"
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
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 成本計算", help="選擇材料並計算成本")
        
        # 簡化的材料輸入介面
        if st.session_state.saved_materials:
            # 選擇材料
            selected_material = st.selectbox(
                "選擇材料",
                options=list(st.session_state.saved_materials.keys()),
                placeholder="請選擇要計算的材料...",
                label_visibility="collapsed"
            )
            
            if selected_material:
                # 顯示材料單價
                price = st.session_state.saved_materials[selected_material]
                
                # 創建計算區域
                with st.container():
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>{selected_material}</h4>
                        <p><strong>單價：</strong>NT$ {price} / g</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 輸入克數
                weight = st.number_input(
                    "選擇克數 (g)", 
                    min_value=0.0, 
                    value=100.0, 
                    step=1.0, 
                    key="main_weight",
                    help="請選擇或輸入需要的材料重量（克）",
                    label_visibility="collapsed"
                )
                
                # 即時預覽計算結果
                if weight > 0:
                    cost = weight * price
                    st.markdown(f"""
                    <div class="metric-card">
                        <h4>預覽結果</h4>
                        <p><strong>重量：</strong>{weight:.1f} g</p>
                        <p><strong>預估成本：</strong>NT$ {cost:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 計算按鈕
                if st.button("計算成本", type="primary", use_container_width=True):
                    # 計算成本
                    cost = weight * price
                    
                    # 顯示計算結果
                    st.markdown("---")
                    st.markdown("### 計算結果")
                    
                    col1_result, col2_result, col3_result = st.columns(3)
                    with col1_result:
                        st.metric("材料", selected_material)
                    with col2_result:
                        st.metric("重量", f"{weight:.1f} g")
                    with col3_result:
                        st.metric("成本", f"NT$ {cost:.2f}")
                        
                    # 顯示詳細計算
                    st.markdown("---")
                    with st.expander("查看計算公式", expanded=False):
                        st.markdown(f"""
                        **計算過程：**
                        - 重量：{weight:.1f} g
                        - 單價：NT$ {price} / g
                        - 成本：{weight:.1f} × {price} = **NT$ {cost:.2f}**
                        """)
        else:
            st.markdown("""
            <div class="warning-message">
                <h4>尚未新增材料</h4>
                <p>請先在「材料管理」頁面新增您常用的材料。</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 使用說明")
        
        with st.expander("快速指南", expanded=True):
            st.markdown("""
            **計算步驟：**
            1. 選擇要計算的材料
            2. 輸入需要的克數
            3. 點擊「計算成本」按鈕
            
            **材料管理：**
            - 切換到「材料管理」頁面
            - 新增、編輯或刪除材料
            """)
        
        # 快速操作
        if st.session_state.saved_materials:
            st.markdown("### 快速操作")
            if st.button("切換到材料管理", use_container_width=True):
                st.session_state.current_page = "材料管理"
                st.rerun()

else:
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
                    placeholder="例如：麵粉、糖、雞蛋...",
                    label_visibility="collapsed"
                )
                price_per_100g = st.number_input(
                    "單價 (每g，NT$)", 
                    min_value=0.0, 
                    value=0.1, 
                    step=0.01,
                    help="輸入每克的價格",
                    label_visibility="collapsed"
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
                with st.container():
                    st.markdown(f"""
                    <div class="material-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>{material}</strong><br>
                                <small>NT$ {price} / g</small>
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
        
        col_clear, col_switch = st.columns(2)
        with col_clear:
            if st.button("清除所有材料", type="secondary", use_container_width=True):
                st.session_state.saved_materials = {}
                save_materials_data()
                st.success("已清除所有材料")
                st.rerun()
        
        with col_switch:
            if st.button("切換到成本計算", use_container_width=True):
                st.session_state.current_page = "成本計算"
                st.rerun()

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
