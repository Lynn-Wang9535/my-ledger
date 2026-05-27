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

st.set_page_config(
    page_title="账本",
    page_icon="💰",
    layout="wide"
)

# =========================
# session_state
# =========================
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if "edited_df" not in st.session_state:
    st.session_state.edited_df = None

# =========================
# 初始化文件
# =========================
if not os.path.exists(DATA_FILE):

    pd.DataFrame(
        columns=[
            "日期时间",
            "记账人",
            "类型",
            "类别",
            "金额",
            "备注"
        ]
    ).to_csv(DATA_FILE, index=False)

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

    try:

        df = pd.read_csv(DATA_FILE)

    except:

        df = pd.DataFrame(
            columns=[
                "日期时间",
                "记账人",
                "类型",
                "类别",
                "金额",
                "备注"
            ]
        )

    columns = [
        "日期时间",
        "记账人",
        "类型",
        "类别",
        "金额",
        "备注"
    ]

    for col in columns:

        if col not in df.columns:
            df[col] = ""

    df = df[columns]

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
# CSS
# =========================
st.markdown(
    """
    <style>

    h2 {
        font-size: 22px !important;
    }

    h3 {
        font-size: 18px !important;
    }

    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
    }

    div[data-testid="stMetricValue"] {
        font-size: 17px !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# 标题
# =========================
st.markdown(
    "<h2>📊 我的财务概览</h2>",
    unsafe_allow_html=True
)

# =========================
# 读取数据
# =========================
df = get_data()

# =========================
# 数据预处理
# =========================
if not df.empty:

    df["金额"] = pd.to_numeric(
        df["金额"],
        errors="coerce"
    ).fillna(0)

    df["日期时间"] = pd.to_datetime(
        df["日期时间"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["日期时间"]
    )

    df["年份"] = (
        df["日期时间"]
        .dt.year
        .astype(int)
        .astype(str)
    )

    df["月份"] = (
        df["日期时间"]
        .dt.month
        .astype(int)
        .astype(str)
        .str.zfill(2)
    )

    df["日期"] = (
        df["日期时间"]
        .dt.day
        .astype(int)
        .astype(str)
        .str.zfill(2)
    )

# =========================
# 总体统计
# =========================
if not df.empty:

    st.markdown(
        "<h3>总体统计</h3>",
        unsafe_allow_html=True
    )

    total_income = df[
        df["类型"] == "收入"
    ]["金额"].sum()

    total_outcome = df[
        df["类型"] == "支出"
    ]["金额"].sum()

    total_balance = total_income - total_outcome

    overview_df = pd.DataFrame([
        {
            "总收入": total_income,
            "总支出": total_outcome,
            "结余": total_balance
        }
    ])

    st.dataframe(
        overview_df,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # 记账人统计
    # =========================
    st.markdown(
        "<h3>记账人统计</h3>",
        unsafe_allow_html=True
    )

    person_stats = []

    for person in get_persons():

        income = df[
            (df["记账人"] == person) &
            (df["类型"] == "收入")
        ]["金额"].sum()

        outcome = df[
            (df["记账人"] == person) &
            (df["类型"] == "支出")
        ]["金额"].sum()

        person_stats.append({
            "记账人": person,
            "总收入": income,
            "总支出": outcome
        })

    st.dataframe(
        pd.DataFrame(person_stats),
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # 类别统计
    # =========================
    st.markdown(
        "<h3>类别统计</h3>",
        unsafe_allow_html=True
    )

    category_stats = []

    for category in get_categories():

        income = df[
            (df["类别"] == category) &
            (df["类型"] == "收入")
        ]["金额"].sum()

        outcome = df[
            (df["类别"] == category) &
            (df["类型"] == "支出")
        ]["金额"].sum()

        category_stats.append({
            "类别": category,
            "总收入": income,
            "总支出": outcome
        })

    st.dataframe(
        pd.DataFrame(category_stats),
        use_container_width=True,
        hide_index=True
    )

# =========================
# 历史明细
# =========================
st.markdown(
    "<h3>历史明细</h3>",
    unsafe_allow_html=True
)

if not df.empty:

    # =========================
    # 年月日筛选
    # =========================
    col1, col2, col3 = st.columns(3)

    years = sorted(
        df["年份"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_year = col1.selectbox(
        "年份",
        years
    )

    months = sorted(
        df[
            df["年份"] == selected_year
        ]["月份"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_month = col2.selectbox(
        "月份",
        months
    )

    days = sorted(
        df[
            (df["年份"] == selected_year) &
            (df["月份"] == selected_month)
        ]["日期"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected_day = col3.selectbox(
        "日期",
        ["全部"] + list(days)
    )

    # =========================
    # 数据筛选
    # =========================
    filtered_df = df[
        (df["年份"] == selected_year) &
        (df["月份"] == selected_month)
    ]

    if selected_day != "全部":

        filtered_df = filtered_df[
            filtered_df["日期"] == selected_day
        ]

    # =========================
    # 当前月份统计
    # =========================
    st.markdown(
        "<h3>当前筛选统计</h3>",
        unsafe_allow_html=True
    )

    filter_income = filtered_df[
        filtered_df["类型"] == "收入"
    ]["金额"].sum()

    filter_outcome = filtered_df[
        filtered_df["类型"] == "支出"
    ]["金额"].sum()

    st.dataframe(
        pd.DataFrame([
            {
                "总收入": filter_income,
                "总支出": filter_outcome
            }
        ]),
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # 表格按钮
    # =========================
    btn1, btn2 = st.columns(2)

    with btn1:

        if not st.session_state.edit_mode:

            if st.button("✏️ 修改表格"):

                st.session_state.edit_mode = True

                st.rerun()

    with btn2:

        if st.session_state.edit_mode:

            if st.button("💾 保存修改"):

                try:

                    edited_df = (
                        st.session_state.edited_df.copy()
                    )

                    edited_df["金额"] = pd.to_numeric(
                        edited_df["金额"],
                        errors="coerce"
                    ).fillna(0)

                    edited_df = edited_df.reset_index(
                        drop=True
                    )

                    save_data(edited_df)

                    st.session_state.edit_mode = False

                    st.toast("保存成功")

                    st.rerun()

                except Exception as e:

                    st.error(f"保存失败：{e}")

    # =========================
    # 编辑模式
    # =========================
    if st.session_state.edit_mode:

        edited_df = st.data_editor(

            df[[
                "日期时间",
                "记账人",
                "类型",
                "类别",
                "金额",
                "备注"
            ]],

            use_container_width=True,

            num_rows="dynamic",

            hide_index=True,

            column_config={

                "记账人":
                st.column_config.SelectboxColumn(
                    "记账人",
                    options=get_persons()
                ),

                "类型":
                st.column_config.SelectboxColumn(
                    "类型",
                    options=["支出", "收入"]
                ),

                "类别":
                st.column_config.SelectboxColumn(
                    "类别",
                    options=get_categories()
                )
            },

            key="editable_table"
        )

        st.session_state.edited_df = (
            edited_df.copy()
        )

    # =========================
    # 普通模式
    # =========================
    else:

        st.dataframe(
            filtered_df[[
                "日期时间",
                "记账人",
                "类型",
                "类别",
                "金额",
                "备注"
            ]],
            use_container_width=True,
            hide_index=True
        )

else:

    st.info("暂无记录")

# =========================
# 侧边栏：新增记录
# =========================
st.sidebar.header("📝 新增记录")

with st.sidebar.form(
    "add_form",
    clear_on_submit=True
):

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

    amount_text = st.text_input(
        "金额",
        placeholder="请输入金额"
    )

    note = st.text_input("备注")

    submit = st.form_submit_button(
        "确认保存"
    )

    if submit:

        try:

            # 金额允许输入 1 或 1.5
            amount = float(amount_text)

            current_df = get_data()

            # 新增数据
            new_row = pd.DataFrame([
                {
                    "日期时间": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "记账人": person,
                    "类型": t_type,
                    "类别": category,
                    "金额": amount,
                    "备注": note
                }
            ])

            # 合并数据
            current_df = pd.concat(
                [current_df, new_row],
                ignore_index=True
            )

            # 保存
            save_data(current_df)

            st.toast("保存成功")

            st.rerun()

        except Exception as e:

            st.sidebar.error(
                f"保存失败：{e}"
            )

# =========================
# 管理类别
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

    new_category = st.text_input(
        "新增类别"
    )

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

        st.toast("保存成功")

        st.rerun()

# =========================
# 管理记账人
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

    new_person = st.text_input(
        "新增记账人"
    )

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

        st.toast("保存成功")

        st.rerun()
