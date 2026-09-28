import os
import streamlit as st
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner

st.set_page_config(page_title="手機座位查詢系統", layout="centered")

st.title("📱 查詢系統")

# 1. 載入 Excel 資料庫
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(BASE_DIR, "data.xlsx")
    df = pd.read_excel(excel_path, dtype={"編號": str})
    df["編號"] = df["編號"].str.strip()
    return df

try:
    df = load_data()
    st.success("內部資料庫已成功載入！")
except Exception as e:
    st.error(f"無法載入 data.xlsx，錯誤訊息：{e}")
    st.stop()

st.markdown("---")

# 2. 選擇查詢方式
option = st.radio("選擇查詢方式：", ("鏡頭掃描 QR Code", "手動輸入訊息"))

code_input = ""

if option == "鏡頭掃描 QR Code":
    st.write("請將鏡頭對準 QR Code：")
    qr_code = qrcode_scanner(key="qrcode_scanner")
    if qr_code:
        code_input = qr_code
        st.info(f"掃描到的原始訊息：`{code_input}`")
else:
    code_input = st.text_input("請貼上或輸入掃描到的訊息：", placeholder="例如：7552379030Z3024AP 030H")

# 3. 擷取前 10 碼與比對
if code_input:
    # 擷取字串前 10 碼
    target_id = code_input[:10].strip()
    st.write(f"🔍 擷取比對編號：**`{target_id}`**")
    
    # 於 Excel 中比對
    result = df[df["編號"] == target_id]
    
    if not result.empty:
    st.balloons()
    st.success("✅ 找到對應資料！")

    for idx, row in result.iterrows():
        # 自動把 Excel 裡除了「編號」以外的每個欄位都用漂亮的卡片顯示出來
        for col in df.columns:
            if col != "編號":
                st.metric(label=f"📌 {col}", value=row[col] if pd.notna(row[col]) else "無紀錄")

        with st.expander("檢視完整詳細資料"):
            st.dataframe(result)
    else:
        st.error(f"❌ 查無此編號 (`{target_id}`)，請確認資料庫內容。")