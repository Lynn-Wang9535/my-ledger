import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 配置
DATA_FILE = "my_data.csv"
st.set_page_config(page_title="账本", page_icon="💰")

# 初始化数据
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["日期", "类型", "类别", "金额", "备注"])
    df_init.to_csv(DATA_FILE, index=False)

def get_data():
    return pd.read_csv(DATA_FILE)

# 侧边栏：记账录入
st.sidebar.header("📝 新增记录")
with st.sidebar.form("add_form", clear_on_submit=True):
    date = st.date_input("日期", datetime.now())
    t_type = st.selectbox("类型", ["支出", "收入"])
    category = st.selectbox("类别", ["餐饮", "购物", "交通", "工资", "理财", "其他"])
    amount = st.number_input("金额", min_value=0.0, step=1.0)
    note = st.text_input("备注")
    if st.form_submit_button("确认保存"):
        df = get_data()
        new_row = pd.DataFrame([[date, t_type, category, amount, note]], columns=df.columns)
        pd.concat([df, new_row]).to_csv(DATA_FILE, index=False)
        st.sidebar.success("已保存！")
        st.rerun()

# 主界面：数据显示
st.title("📊 我的财务概览")
df = get_data()

if not df.empty:
    # 顶部统计
    in_sum = df[df["类型"] == "收入"]["金额"].sum()
    out_sum = df[df["类型"] == "支出"]["金额"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("总收入", f"¥{in_sum}")
    c2.metric("总支出", f"¥{out_sum}")
    c3.metric("结余", f"¥{in_sum - out_sum}")

    # 数据表
    st.write("### 历史明细")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.info("还没有记录，从左侧开始记账吧！")