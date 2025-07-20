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
    layout="wide"
)

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
st.title("💰 Gwen的成本計算器")
st.markdown("---")

# 側邊欄 - 頁面選擇
with st.sidebar:
    st.header("📱 頁面選擇")
    
    # 頁面選擇器
    page = st.selectbox(
        "選擇頁面",
        ["成本計算", "材料管理"],
        index=0 if st.session_state.current_page == "成本計算" else 1
    )
    
    # 更新當前頁面
    if page != st.session_state.current_page:
        st.session_state.current_page = page
        st.rerun()

# 根據選擇的頁面顯示不同內容
if st.session_state.current_page == "成本計算":
    # 成本計算頁面
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🧮 成本計算")
        
        # 簡化的材料輸入介面
        if st.session_state.saved_materials:
            # 選擇材料
            selected_material = st.selectbox(
                "選擇材料",
                options=list(st.session_state.saved_materials.keys()),
                placeholder="請選擇材料..."
            )
            
            if selected_material:
                # 顯示材料單價
                price = st.session_state.saved_materials[selected_material]
                st.info(f"💰 {selected_material} 單價：NT$ {price} / 100g")
                
                # 輸入克數
                weight = st.number_input("克數 (g)", min_value=0.0, value=100.0, step=1.0, key="main_weight")
                
                # 計算按鈕
                if st.button("🧮 計算成本", type="primary"):
                    # 計算成本
                    cost = (weight / 100) * price
                    
                    # 顯示計算結果
                    st.markdown("---")
                    st.subheader("計算結果")
                    
                    col1_result, col2_result, col3_result = st.columns(3)
                    with col1_result:
                        st.metric("材料", selected_material)
                    with col2_result:
                        st.metric("重量", f"{weight:.1f} g")
                    with col3_result:
                        st.metric("成本", f"NT$ {cost:.2f}")
                        
                    # 顯示詳細計算
                    st.markdown("---")
                    st.markdown(f"""
                    **計算公式：**
                    - 重量：{weight:.1f} g
                    - 單價：NT$ {price} / 100g
                    - 成本：({weight:.1f} ÷ 100) × {price} = **NT$ {cost:.2f}**
                    """)
                else:
                    st.info("👆 請點擊「計算成本」按鈕來查看結果")
        else:
            st.warning("⚠️ 請先在「材料管理」頁面新增一些材料！")
            st.info("💡 點擊左側「材料管理」來新增您常用的材料。")
    
    with col2:
        st.header("💡 使用說明")
        
        st.markdown("""
        **快速計算步驟：**
        1. 在「材料管理」頁面新增常用材料
        2. 選擇要計算的材料
        3. 輸入克數
        4. 點擊「計算成本」按鈕
        
        **材料管理：**
        - 點擊左側「材料管理」頁面
        - 新增、編輯或刪除材料
        """)

else:
    # 材料管理頁面
    st.header("📝 材料管理")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("新增材料")
        
        # 新增材料表單
        with st.form("add_material_form"):
            material_name = st.text_input("材料名稱")
            price_per_100g = st.number_input("單價 (每100g，NT$)", min_value=0.0, value=10.0, step=0.1)
            
            submitted = st.form_submit_button("💾 儲存材料", type="primary")
            if submitted:
                if material_name:
                    st.session_state.saved_materials[material_name] = price_per_100g
                    save_materials_data()
                    st.success(f"✅ 已成功儲存 {material_name}！")
                    st.rerun()
                else:
                    st.error("❌ 請輸入材料名稱！")
    
    with col2:
        st.subheader("已儲存材料")
        
        if st.session_state.saved_materials:
            
            # 材料列表
            for i, (material, price) in enumerate(st.session_state.saved_materials.items()):
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.write(f"**{material}**")
                    with col2:
                        st.write(f"NT$ {price}")
                    with col3:
                        if st.button("❌", key=f"del_{material}"):
                            del st.session_state.saved_materials[material]
                            save_materials_data()
                            st.success(f"✅ 已刪除 {material}")
                            st.rerun()
                    st.divider()
        else:
            st.info("📝 尚未新增任何材料")
    

    if st.session_state.saved_materials:
        st.markdown("---")
        
        if st.button("🗑️ 清除所有材料", type="secondary"):
            st.session_state.saved_materials = {}
            save_materials_data()
            st.success("✅ 已清除所有材料")
            st.rerun()

# 頁腳
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>💡 使用提示：</p>
        <ul style='text-align: left; display: inline-block;'>
            <li>在「材料管理」頁面新增常用材料</li>
            <li>在「成本計算」頁面選擇材料並計算成本</li>
            <li>已儲存的材料資料會永久保存</li>
            <li>單價請輸入每100克的價格</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)
