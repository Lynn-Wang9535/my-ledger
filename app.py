import streamlit as st
import pandas as pd
from datetime import datetime
import os
import time

# =========================
# 文件配置
# =========================
DATA_FILE = "my_data.csv"
CATEGORY_FILE = "categories.csv"
PERSON_FILE = "persons.csv"

st.set_page_config(
    page_title="账本",
    page_icon="💰",
    layout="wide"
)

# =========================
# 初始化文件
# =========================
if not os.path.exists(DATA_FILE):

    df_init = pd.DataFrame(
        columns=[
            "日期时间",
            "记账人",
            "类型",
            "类别",
            "金额",
            "备注"
        ]
    )

    df_init.to_csv(DATA_FILE, index=False)

if not os.path.exists(CATEGORY_FILE):

    pd.DataFrame({
        "类别": ["餐饮", "购物", "交通"]
    }).to_csv(CATEGORY_FILE, index=False)

if not os.path.exists(PERSON_FILE):

    pd.DataFrame({
        "记账人": ["自己"]
    }).to_csv(PERSON_FILE, index=False)

# =========================
# 数据函数
# =========================
def get_data():

    df = pd.read_csv(DATA_FILE)

    # 兼容旧版本
    if "日期时间" not in df.columns:

        if "日期" in df.columns:
            df["日期时间"] = df["日期"]
        else:
            df["日期时间"] = ""

    if "记账人" not in df.columns:
        df["记账人"] = "自己"

    if "日期" in df.columns:
        df = df.drop(columns=["日期"])

    columns = [
        "日期时间",
        "记账人",
        "类型",
        "类别",
        "金额",
        "备注"
    ]

    df = df[columns]

    save_data(df)

    return df


def save_data(df):

    df.to_csv(DATA_FILE, index=False)


def get_categories():

    df = pd.read_csv(CATEGORY_FILE)

    return df["类别"].dropna().tolist()


def save_categories(categories):

    pd.DataFrame({
        "类别": categories
    }).to_csv(CATEGORY_FILE, index=False)


def get_persons():

    df = pd.read_csv(PERSON_FILE)

    return df["记账人"].dropna().tolist()


def save_persons(persons):

    pd.DataFrame({
        "记账人": persons
    }).to_csv(PERSON_FILE, index=False)

# =========================
# CSS样式
# =========================
st.markdown(
    """
    <style>

    h2 {
        font-size: 24px !important;
    }

    h3 {
        font-size: 18px !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 18px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# 页面标题
# =========================
st.markdown(
    """
    <h2>📊 我的财务概览</h2>
    """,
    unsafe_allow_html=True
)

# =========================
# 读取数据
# =========================
df = get_data()

# =========================
# 总体统计
# =========================
if not df.empty:

    in_sum = df[df["类型"] == "收入"]["金额"].sum()

    out_sum = df[df["类型"] == "支出"]["金额"].sum()

    balance = in_sum - out_sum

    col1, col2, col3 = st.columns(3)

    col1.metric("总收入", f"¥{in_sum}")

    col2.metric("总支出", f"¥{out_sum}")

    col3.metric("结余", f"¥{balance}")

    # =========================
    # 各记账人统计
    # =========================
    persons = get_persons()

    if persons:

        cols = st.columns(len(persons))

        for i, person in enumerate(persons):

            person_income = df[
                (df["记账人"] == person) &
                (df["类型"] == "收入")
            ]["金额"].sum()

            person_outcome = df[
                (df["记账人"] == person) &
                (df["类型"] == "支出")
            ]["金额"].sum()

            cols[i].metric(
                f"{person}的收入",
                f"¥{person_income}"
            )

            cols[i].metric(
                f"{person}的支出",
                f"¥{person_outcome}"
            )

# =========================
# 历史明细
# =========================
st.markdown(
    """
    <h3>历史明细</h3>
    """,
    unsafe_allow_html=True
)

if not df.empty:

    # 增加删除列
    df_display = df.copy()

    df_display["删除"] = False

    edited_df = st.data_editor(

        df_display,

        use_container_width=True,

        num_rows="fixed",

        hide_index=True,

        column_config={

            "删除": st.column_config.CheckboxColumn(
                "删除",
                help="勾选后点击保存修改即可删除"
            )

        },

        disabled=[],
    )

    col_save, col_reload = st.columns(2)

    # =========================
    # 保存修改
    # =========================
    with col_save:

        if st.button("💾 保存修改"):

            try:

                # 删除勾选行
                edited_df = edited_df[
                    edited_df["删除"] == False
                ]

                # 删除辅助列
                edited_df = edited_df.drop(
                    columns=["删除"]
                )

                # 金额转数字
                edited_df["金额"] = pd.to_numeric(
                    edited_df["金额"]
                )

                save_data(edited_df)

                msg = st.success("保存成功")

                time.sleep(0.5)

                msg.empty()

                st.rerun()

            except:

                msg = st.error("保存失败")

                time.sleep(0.5)

                msg.empty()

    # =========================
    # 刷新
    # =========================
    with col_reload:

        if st.button("🔄 刷新数据"):

            st.rerun()

else:

    st.info("还没有记录")

# =========================
# 侧边栏：新增记录
# =========================
st.sidebar.header("📝 新增记录")

with st.sidebar.form("add_form", clear_on_submit=True):

    persons = get_persons()

    categories = get_categories()

    now_time = datetime.now()

    person = st.selectbox(
        "记账人",
        persons
    )

    t_type = st.selectbox(
        "类型",
        ["支出", "收入"]
    )

    category = st.selectbox(
        "类别",
        categories
    )

    # 不限制1.00
    amount_text = st.text_input(
        "金额",
        placeholder="请输入金额"
    )

    note = st.text_input("备注")

    submit = st.form_submit_button("确认保存")

    if submit:

        try:

            amount = float(amount_text)

            df = get_data()

            new_row = pd.DataFrame(
                [[
                    now_time.strftime("%Y-%m-%d %H:%M:%S"),
                    person,
                    t_type,
                    category,
                    amount,
                    note
                ]],
                columns=df.columns
            )

            df = pd.concat(
                [df, new_row],
                ignore_index=True
            )

            save_data(df)

            msg = st.sidebar.success("保存成功")

            time.sleep(0.5)

            msg.empty()

            st.rerun()

        except:

            msg = st.sidebar.error("保存失败")

            time.sleep(0.5)

            msg.empty()

# =========================
# 侧边栏：管理类别
# =========================
with st.sidebar.expander("⚙️ 管理类别"):

    categories = get_categories()

    for i, cat in enumerate(categories):

        col1, col2 = st.columns([4, 1])

        categories[i] = col1.text_input(
            f"类别{i}",
            value=cat,
            key=f"cat_{i}"
        )

        if col2.button(
            "删除",
            key=f"del_cat_{i}"
        ):

            categories.pop(i)

            save_categories(categories)

            st.rerun()

    new_category = st.text_input("新增类别")

    if st.button("保存类别"):

        if new_category.strip():

            categories.append(
                new_category.strip()
            )

        categories = list(dict.fromkeys(
            [
                c.strip()
                for c in categories
                if c.strip()
            ]
        ))

        save_categories(categories)

        msg = st.success("保存成功")

        time.sleep(0.5)

        msg.empty()

        st.rerun()

# =========================
# 侧边栏：管理记账人
# =========================
with st.sidebar.expander("👤 管理记账人"):

    persons = get_persons()

    for i, p in enumerate(persons):

        col1, col2 = st.columns([4, 1])

        persons[i] = col1.text_input(
            f"记账人{i}",
            value=p,
            key=f"person_{i}"
        )

        if col2.button(
            "删除",
            key=f"del_person_{i}"
        ):

            persons.pop(i)

            save_persons(persons)

            st.rerun()

    new_person = st.text_input("新增记账人")

    if st.button("保存记账人"):

        if new_person.strip():

            persons.append(
                new_person.strip()
            )

        persons = list(dict.fromkeys(
            [
                p.strip()
                for p in persons
                if p.strip()
            ]
        ))

        save_persons(persons)

        msg = st.success("保存成功")

        time.sleep(0.5)

        msg.empty()

        st.rerun()
