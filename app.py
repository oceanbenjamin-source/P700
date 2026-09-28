import os
import streamlit as st
import pandas as pd
from streamlit_qrcode_scanner import qrcode_scanner

st.set_page_config(page_title="P700 VR 料號與站別查詢系統", layout="centered")

st.title("📱站別與料號查詢")

# 1. 載入 Excel 資料庫
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    excel_path = os.path.join(BASE_DIR, "data.xlsx")
    
    # 根據檔案結構：header=1 代表 Excel 的第 2 列是標題欄位列
    df = pd.read_excel(excel_path, header=2, dtype=str)
    
    # 清理欄位名稱前後空白
    df.columns = [str(col).strip() for col in df.columns]
    
    # 確保 PNO 欄位存在且去除字串前後空格
    if "PNO" in df.columns:
        df["PNO"] = df["PNO"].astype(str).str.strip()
    
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
    code_input = st.text_input("請貼上或輸入掃描到的件號：", placeholder="例如：7552379030Z3024AP 030H")

# 3. 擷取前 10 碼與比對
if code_input:
    # 擷取字串前 10 碼
    target_id = code_input[:10].strip()
    st.write(f"🔍 擷取比對編號 (PNO)：**`{target_id}`**")
    
    # 於 Excel 的 PNO 欄位中比對
    if "PNO" in df.columns:
        result = df[df["PNO"] == target_id]
        
        if not result.empty:
            st.balloons()
            st.success("✅ 找到對應資料！")
            
            # 逐筆顯示指定的三個欄位資訊
            for idx, row in result.iterrows():
                pno_val = row.get("PNO", "無紀錄")
                pnm_val = row.get("PNM", "無紀錄")
                station_val = row.get("站別", "無紀錄")
                
                # 顯示要求的三個欄位卡片
                st.metric(label="🔢 PNO (料號/編號)", value=str(pno_val) if pd.notna(pno_val) else "無紀錄")
                st.metric(label="📦 PNM (品名/名稱)", value=str(pnm_val) if pd.notna(pnm_val) else "無紀錄")
                st.metric(label="📍 站別", value=str(station_val) if pd.notna(station_val) else "無紀錄")
                
                # 下方詳細資料表也僅保留這三個欄位
                with st.expander("檢視這三個欄位的簡明表格"):
                    target_cols = [c for c in ["PNO", "PNM", "站別"] if c in result.columns]
                    st.dataframe(result[target_cols])
        else:
            st.error(f"❌ 查無此 PNO 編號 (`{target_id}`) 的資料，請確認資料庫內容。")
    else:
        st.error("❌ Excel 檔案中找不到『PNO』欄位，請確認標題列位置。")