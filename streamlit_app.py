import streamlit as st
import pandas as pd
import math
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="AI价到 - 小微外贸智能出口报价系统",
    page_icon="🇨🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0a2463 0%, #1e3a8a 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .profit-card {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .table-header {
        background-color: #0a2463;
        color: white;
        padding: 10px;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# 头部
st.markdown("""
<div class="main-header">
    <h1 style="margin:0; font-size:3rem;">🇨🇳 郑秀英国际贸易</h1>
    <p style="margin:0.5rem 0 0 0; font-size:1.2rem; opacity:0.9;">Pinic International Trading · 智能出口报价引擎</p>
</div>
""", unsafe_allow_html=True)

# 侧边栏 - 参数设置
with st.sidebar:
    st.markdown("## ⚙️ 参数设置")
    
    # 汇率设置
    exchange_rate = st.number_input("💱 美元汇率 (USD/CNY)", 
                                   value=7.2, 
                                   min_value=6.0, 
                                   max_value=8.0, 
                                   step=0.1)
    
    # 利润率设置
    profit_rate = st.number_input("📈 目标利润率 (%)", 
                                 value=20.0, 
                                 min_value=0.0, 
                                 max_value=100.0, 
                                 step=1.0) / 100
    
    st.markdown("---")
    st.markdown("### 📦 集装箱参数")
    
    # ✅ 用户只选择类型，不输入数值
    container_type = st.selectbox(
        "选择集装箱类型",
        options=["20HQ (28 CBM / 22吨)", "40HQ (67.7 CBM / 26吨)"],
        index=1  # 默认40HQ
    )
    
    # ✅ 后台代码定义体积和重量（在这里可以随时修改）
    if "20HQ" in container_type:
        container_volume = 28.0    # 20HQ体积 (CBM)
        container_weight = 22000    # 20HQ限重 (KG)
    elif:  # 40HQ
        container_volume = 67.7     # 40HQ体积 (CBM)
        container_weight = 26000     # 40HQ限重 (KG)
    elif:  # 40FQ
        container_volume = 67.7     # 40FQ体积 (CBM)
        container_weight = 26000     # 40FQ限重 (KG)
    
    # 只显示信息，不提供输入框
    st.info(f"📊 {container_type} - 体积: {container_volume} CBM, 限重: {container_weight/1000:.1f}吨")
    
    st.markdown("---")
    st.markdown("### 💰 费用参数")
    domestic_fee_base = st.number_input("国内运费基础 (¥)", value=3000, step=100)
    domestic_fee_per = st.number_input("每柜国内运费 (¥)", value=1500, step=100)
    freight_usd = st.number_input("海运费 (USD/柜)", value=1000, step=50)
    
    st.markdown("---")
    st.markdown("### 📊 税费参数")
    vat_rate = st.number_input("增值税率 (%)", value=13.0, step=0.5) / 100
    tariff_rate = st.number_input("关税率 (%)", value=5.0, step=0.5) / 100
    insurance_rate = st.number_input("保险费率 (%)", value=0.2, step=0.05) / 100

# 主界面 - 两列布局
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 客户询盘信息")
    with st.container():
        customer = st.text_input("客户名称", "Abdul Jaleel Trading")
        country = st.text_input("目的国家", "菲律宾")
        port = st.text_input("目的港口", "马尼拉港")
        incoterm = st.selectbox("贸易术语", ["CIP", "FOB", "CIF", "EXW", "DAP"])

with col2:
    st.markdown("### 📦 商品信息")
    with st.container():
        product_name = st.text_input("商品名称", "自动售货机 MF-782")
        hs_code = st.text_input("HS编码", "84762100")
        
        col_vol, col_weight = st.columns(2)
        with col_vol:
            volume = st.number_input("单件体积 (CBM)", value=2.55, min_value=0.01, step=0.1)
        with col_weight:
            weight = st.number_input("单件毛重 (KG)", value=280.0, min_value=0.1, step=10.0)
        
        col_price, col_qty = st.columns(2)
        with col_price:
            purchase_price = st.number_input("采购单价 (¥)", value=4778.0, min_value=0.01, step=100.0)
        with col_qty:
            quantity = st.number_input("数量 (台)", value=29, min_value=1, step=1)

# 计算按钮
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
with col_btn1:
    calculate = st.button("🚀 开始智能计算", type="primary", use_container_width=True)

# 计算结果
if calculate:
    # 基础计算
    total_volume = volume * quantity
    total_weight = weight * quantity
    
    # 集装箱计算
    containers_by_volume = math.ceil(total_volume / container_volume)
    containers_by_weight = math.ceil(total_weight / container_weight)
    containers = max(containers_by_volume, containers_by_weight)
    
    # 费用计算
    purchase_total = purchase_price * quantity
    tax_rebate = purchase_total / (1 + vat_rate) * vat_rate
    domestic_fee = domestic_fee_base + domestic_fee_per * containers
    intl_freight = freight_usd * exchange_rate * containers
    insurance = (purchase_total + intl_freight) * 1.1 * insurance_rate
    tariff = purchase_total * tariff_rate
    
    # 成本计算
    total_cost = purchase_total - tax_rebate + domestic_fee + intl_freight + insurance + tariff
    
    # 利润计算
    target_profit = total_cost * profit_rate
    contract_amount = total_cost + target_profit
    unit_price_usd = contract_amount / quantity / exchange_rate
    
    # 显示结果 - 智能推荐卡片
    st.markdown("### 🤖 智能分析结果")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    
    with res_col1:
        st.markdown("""
        <div class="card">
            <h4 style="color:#0a2463;">📦 装箱推荐</h4>
        """, unsafe_allow_html=True)
        st.metric("集装箱类型", "40HQ 高柜")
        st.metric("需要集装箱", f"{containers} 个")
        st.metric("总体积", f"{total_volume:.2f} CBM")
        st.metric("总毛重", f"{total_weight:,.0f} KG")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with res_col2:
        st.markdown("""
        <div class="card">
            <h4 style="color:#0a2463;">💰 报价建议</h4>
        """, unsafe_allow_html=True)
        st.metric("FOB单价 (USD)", f"USD {unit_price_usd:,.2f}")
        st.metric("合同总额 (CNY)", f"¥{contract_amount:,.2f}")
        st.metric("利润率", f"{profit_rate*100:.1f}%")
        st.metric("目标利润", f"¥{target_profit:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with res_col3:
        st.markdown("""
        <div class="card">
            <h4 style="color:#0a2463;">📊 成本分析</h4>
        """, unsafe_allow_html=True)
        st.metric("采购总价", f"¥{purchase_total:,.2f}")
        st.metric("退税金额", f"¥{tax_rebate:,.2f}")
        st.metric("总成本", f"¥{total_cost:,.2f}")
        st.metric("成本利润率", f"{(target_profit/total_cost*100):.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 预算表
    st.markdown("### 📊 出口预算表（单位：人民币）")
    
    # 创建预算表格数据
    budget_data = {
        '项目': ['采购总价', '出口退税', '国内运费', '国际运费', '保险费', '出口关税', '总成本', '合同金额'],
        '金额': [
            f"¥{purchase_total:,.2f}",
            f"-¥{tax_rebate:,.2f}",
            f"¥{domestic_fee:,.2f}",
            f"¥{intl_freight:,.2f}",
            f"¥{insurance:,.2f}",
            f"¥{tariff:,.2f}",
            f"¥{total_cost:,.2f}",
            f"¥{contract_amount:,.2f}"
        ],
        '计算公式': [
            f"{purchase_price:,.0f} × {quantity}台",
            f"采购价 ÷ {1+vat_rate:.2f} × {vat_rate:.2f}",
            f"{domestic_fee_base} + {domestic_fee_per} × {containers}柜",
            f"${freight_usd} × {exchange_rate} × {containers}柜",
            f"(采购价+运费) × 110% × {insurance_rate:.2%}",
            f"采购价 × {tariff_rate:.2%}",
            "采购总价 - 退税 + 各项费用",
            f"总成本 × (1 + {profit_rate:.0%})"
        ]
    }
    
    df = pd.DataFrame(budget_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "项目": "项目",
            "金额": "金额 (CNY)",
            "计算公式": "计算公式"
        }
    )
    
    # 利润展示 - 三列
    st.markdown("### 💰 利润分析")
    
    profit_col1, profit_col2, profit_col3 = st.columns(3)
    
    with profit_col1:
        st.markdown(f"""
        <div class="profit-card">
            <div class="metric-label">💰 预计利润</div>
            <div class="metric-value">¥{target_profit:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with profit_col2:
        st.markdown(f"""
        <div class="profit-card">
            <div class="metric-label">📈 利润率</div>
            <div class="metric-value">{profit_rate*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with profit_col3:
        roi = (target_profit / purchase_total) * 100
        st.markdown(f"""
        <div class="profit-card">
            <div class="metric-label">🔄 投资回报率</div>
            <div class="metric-value">{roi:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 详细数据表格
    st.markdown("### 📋 详细计算数据")
    
    detail_data = {
        '参数': [
            '单件体积 (CBM)',
            '单件毛重 (KG)',
            '总体积 (CBM)',
            '总毛重 (KG)',
            '所需集装箱数',
            'FOB单价 (USD)',
            'FOB单价 (CNY)',
            '总成本 (CNY)',
            '合同金额 (CNY)',
            '预计利润 (CNY)'
        ],
        '数值': [
            f"{volume:.2f}",
            f"{weight:.1f}",
            f"{total_volume:.2f}",
            f"{total_weight:,.0f}",
            f"{containers}",
            f"USD {unit_price_usd:,.2f}",
            f"¥{unit_price_usd * exchange_rate:,.2f}",
            f"¥{total_cost:,.2f}",
            f"¥{contract_amount:,.2f}",
            f"¥{target_profit:,.2f}"
        ]
    }
    
    df_detail = pd.DataFrame(detail_data)
    st.dataframe(df_detail, use_container_width=True, hide_index=True)
    
    # 生成报价单按钮
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        if st.button("📄 生成正式报价单", use_container_width=True):
            st.success("✅ 报价单已生成！")
            st.balloons()
            st.info("📧 报价单已发送到您的邮箱 (演示版)")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>© 2026 郑秀英国际贸易有限公司 · 智能出口报价系统 v2.0</p>
        <p style="font-size: 0.875rem;">✅ 已修复plotly依赖问题 · 所有数据实时计算</p>
    </div>
    """, 
    unsafe_allow_html=True
)
