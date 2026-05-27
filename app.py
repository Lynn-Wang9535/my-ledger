import streamlit as st
import pandas as pd
from datetime import datetime
import os

# =========================
# 文件配置
# =========================
DATA_FILE = "my_data.csv"
CATEGORY_FILE = "categories.csv"
PERSON_FILE = "persons.csv"

st.set_page_config(page_title="账本", page_icon="💰", layout="wide")

# =========================
# 初始化文件
# =========================
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(
        columns=["日期时间", "记账人", "类型", "类别", "金额", "备注"]
    )
    df_init.to_csv(DATA_FILE, index=False)

if not os.path.exists(CATEGORY_FILE):
    pd.DataFrame({"类别": ["餐饮", "购物", "交通"]}).to_csv(
        CATEGORY_FILE, index=False
    )

if not os.path.exists(PERSON_FILE):
    pd.DataFrame({"记账人": ["自己"]}).to_csv(
        PERSON_FILE, index=False
    )


# =========================
# 数据读取函数
# =========================
def get_data():
    return pd.read_csv(DATA_FILE)


def save_data(df):
    df.to_csv(DATA_FILE, index=False)


def get_categories():
    df = pd.read_csv(CATEGORY_FILE)
    return df["类别"].dropna().tolist()


def save_categories(categories):
    pd.DataFrame({"类别": categories}).to_csv(
        CATEGORY_FILE, index=False
    )


def get_persons():
    df = pd.read_csv(PERSON_FILE)
    return df["记账人"].dropna().tolist()


def save_persons(persons):
    pd.DataFrame({"记账人": persons}).to_csv(
        PERSON_FILE, index=False
    )


# =========================
# 页面标题（缩小）
# =========================
st.markdown(
    """
    <h2 style='margin-bottom:10px;'>📊 我的财务概览</h2>
    """,
    unsafe_allow_html=True,
)

# =========================
# 侧边栏：类别管理
# =========================
with st.sidebar.expander("⚙️ 管理类别", expanded=False):

    categories = get_categories()

    st.write("### 当前类别")

    for i, cat in enumerate(categories):
        col1, col2 = st.columns([4, 1])

        new_name = col1.text_input(
            f"类别{i}",
            value=cat,
            key=f"cat_{i}"
        )

        if col2.button("删除", key=f"del_cat_{i}"):
            categories.pop(i)
            save_categories(categories)
            st.rerun()

        categories[i] = new_name

    new_category = st.text_input("新增类别")

    if st.button("保存类别"):
        if new_category.strip():
            categories.append(new_category.strip())

        # 去重 + 去空
        categories = list(dict.fromkeys(
            [c.strip() for c in categories if c.strip()]
        ))

        save_categories(categories)
        st.success("类别已保存")
        st.rerun()


# =========================
# 侧边栏：记账人管理
# =========================
with st.sidebar.expander("👤 管理记账人", expanded=False):

    persons = get_persons()

    st.write("### 当前记账人")

    for i, p in enumerate(persons):
        col1, col2 = st.columns([4, 1])

        new_p = col1.text_input(
            f"记账人{i}",
            value=p,
            key=f"person_{i}"
        )

        if col2.button("删除 ", key=f"del_person_{i}"):
            persons.pop(i)
            save_persons(persons)
            st.rerun()

        persons[i] = new_p

    new_person = st.text_input("新增记账人")

    if st.button("保存记账人"):
        if new_person.strip():
            persons.append(new_person.strip())

        persons = list(dict.fromkeys(
            [p.strip() for p in persons if p.strip()]
        ))

        save_persons(persons)
        st.success("记账人已保存")
        st.rerun()


# =========================
# 侧边栏：新增记录
# =========================
st.sidebar.header("📝 新增记录")

with st.sidebar.form("add_form", clear_on_submit=True):

    persons = get_persons()
    categories = get_categories()

    # 自动记录当前时间
    now_time = datetime.now()

    person = st.selectbox("记账人", persons)

    t_type = st.selectbox("类型", ["支出", "收入"])

    category = st.selectbox("类别", categories)

    # 金额输入框默认为空
    amount = st.number_input(
        "金额",
        min_value=0.0,
        step=1.0,
        value=None,
        placeholder="请输入金额"
    )

    note = st.text_input("备注")

    submit = st.form_submit_button("确认保存")

    if submit:

        if amount is None:
            st.warning("请输入金额")
        else:

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

            df = pd.concat([df, new_row], ignore_index=True)

            save_data(df)

            st.sidebar.success("已保存！")
            st.rerun()


# =========================
# 主界面数据
# =========================
df = get_data()

if not df.empty:

    # 金额统计
    in_sum = df[df["类型"] == "收入"]["金额"].sum()
    out_sum = df[df["类型"] == "支出"]["金额"].sum()
    balance = in_sum - out_sum

    # 缩小指标字体
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            padding: 5px;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 14px;
        }

        div[data-testid="stMetricValue"] {
            font-size: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("总收入", f"¥{in_sum:.2f}")
    c2.metric("总支出", f"¥{out_sum:.2f}")
    c3.metric("结余", f"¥{balance:.2f}")

    st.write("## 历史明细")

    # =========================
    # 可编辑表格
    # =========================
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        key="editor",
    )

    col_save, col_reload = st.columns(2)

    with col_save:
        if st.button("💾 保存修改"):
            save_data(edited_df)
            st.success("修改已保存")

    with col_reload:
        if st.button("🔄 刷新数据"):
            st.rerun()

else:
    st.info("还没有记录，从左侧开始记账吧！")
