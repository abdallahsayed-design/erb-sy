import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- إعدادات الصفحة الافتراضية لـ Streamlit ---
st.set_page_config(page_title="معرض الكبير - إدارة المبيعات", page_icon="🏢", layout="wide")

# --- إعدادات النظام الأساسية وأسماء الملفات ---
SHOWROOM_NAME = "معرض الكبير"
INVENTORY_FILE = "inventory.csv"
SALES_FILE = "sales.csv"
CONTACTS_FILE = "contacts.csv"

# --- دالة فحص وإنشاء الملفات تلقائياً لمنع الشاشة البيضاء ---
def initialize_files():
    # ملف المخزن
    if not os.path.exists(INVENTORY_FILE):
        df = pd.DataFrame([
            {"اسم الصنف": "غسالة عادية", "الكمية": 10, "سعر البيع": 4500.0},
            {"اسم الصنف": "ثلاجة 14 قدم", "الكمية": 5, "سعر البيع": 12000.0},
            {"اسم الصنف": "شاشة 43 بوصة", "الكمية": 8, "سعر البيع": 0.0}  # صنف تجريبي بسعر صفر لاختبار الحماية
        ])
        df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    
    # ملف المبيعات
    if not os.path.exists(SALES_FILE):
        df = pd.DataFrame(columns=[
            "رقم الفاتورة", "التاريخ", "اسم العميل", "هاتف العميل", "العنوان", 
            "نوع البيع", "نظام التحصيل", "تاريخ التحصيل", "الصنف", "الكمية", 
            "الخصم %", "إجمالي البيع", "المسؤول"
        ])
        df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
        
    # ملف جهات الاتصال والعملاء
    if not os.path.exists(CONTACTS_FILE):
        df = pd.DataFrame([
            {"الاسم": "عبدالله", "النوع": "عميل", "الهاتف": "01012345678", "العنوان": "العباسه"},
            {"الاسم": "محمد أحمد", "النوع": "عميل", "الهاتف": "01234567890", "العنوان": "أبو حماد"}
        ])
        df.to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')

# تشغيل دالة التجهيز تلقائياً
initialize_files()

# --- دالة التفقيط الديناميكي للمبالغ ---
def tafqeet(amount):
    try:
        amount = round(float(amount), 2)
        if amount == 0:
            return "صفر جنيهاً مصرياً لا غير"
        
        pounds = int(amount)
        piasters = int(round((amount - pounds) * 100))
        
        def convert_chunk(num):
            units = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة",
                     "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
            tens = ["", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
            hundreds = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]
            
            if num < 20:
                return units[num]
            elif num < 100:
                return units[num % 10] + (" و" if num % 10 else "") + tens[num // 10]
            elif num < 1000:
                return hundreds[num // 100] + (" و" if num % 100 else "") + convert_chunk(num % 100)
            return str(num)

        def format_large_numbers(val):
            if val == 0: return ""
            if val < 1000: return convert_chunk(val)
            if val < 1000000:
                thousands = val // 1000
                remainder = val % 1000
                th_text = "ألف" if thousands == 1 else "ألفين" if thousands == 2 else f"{convert_chunk(thousands)} آلاف" if 3 <= thousands <= 10 else f"{convert_chunk(thousands)} ألفاً"
                return th_text + (" و" if remainder else "") + convert_chunk(remainder)
            return str(val)

        text = format_large_numbers(pounds) + " جنيهاً مصرياً"
        if piasters > 0:
            text += " و" + convert_chunk(piasters) + " قرشاً"
        return text + " لا غير"
    except:
        return f"{amount} جنيهاً مصرياً لا غير"

# --- دالة توليد قالب الفاتورة الثلاثية المجمعة HTML ---
def generate_triple_invoice_html(inv_id, datetime_str, c_name, c_phone, c_address, sale_type, collect_system, collect_date, user, item_name, qty, item_price, discount, final_total):
    total_in_words = tafqeet(final_total)
    
    html_content = f"""
    <style>
        @media print {{
            .no-print-zone {{ display: none !important; }}
            .invoice-page {{ page-break-after: always; min-height: 98vh; }}
        }}
        .invoice-page {{
            direction: rtl;
            font-family: 'Arial', sans-serif;
            border: 2px dashed #000;
            padding: 15px;
            margin-bottom: 30px;
            background: #fff;
            color: #000;
        }}
        .invoice-header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 15px; }}
        .invoice-header h3 {{ margin: 0; background: #000; color: #fff; padding: 5px; display: inline-block; font-size: 16px; }}
        .invoice-header h1 {{ margin: 5px 0; font-size: 24px; }}
        .invoice-details-table, .invoice-items-table {{ width: 100%; border-collapse: collapse; margin-bottom: 15px; }}
        .invoice-details-table td {{ padding: 6px; font-size: 14px; border: 1px solid #ddd; color: #000; }}
        .invoice-items-table th {{ background: #f2f2f2; font-weight: bold; font-size: 13px; border: 1px solid #000; padding: 8px; color: #000; }}
        .invoice-items-table td {{ border: 1px solid #000; padding: 8px; text-align: center; font-size: 14px; color: #000; }}
        .total-words-area {{ border: 1px dashed #000; padding: 10px; background: #f9f9f9; font-weight: bold; font-size: 14px; margin-bottom: 15px; color: #000; }}
        .invoice-footer-alert {{ font-size: 12px; font-weight: bold; border-top: 1px solid #000; padding-top: 5px; text-align: center; color: #000; }}
    </style>

    <div class="no-print-zone" style="text-align:center; margin-bottom:20px;">
        <button class="print-trigger-btn" style="padding: 10px 20px; font-size: 16px; font-weight: bold; cursor: pointer; background-color: #1e88e5; color: white; border: none; border-radius: 4px;" onclick="window.print()">🖨️ إصدار وطباعة الفاتورة الثلاثية فوراً (A5)</button>
    </div>

    <div class="invoice-page">
        <div class="invoice-header">
            <h3>📋 نسخة العميل (أصل الفاتورة)</h3>
            <h1>🏢 {SHOWROOM_NAME}</h1>
            <p>العنوان: ابوحماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي</p>
            <p style="font-size: 12px; font-weight: bold;">📞 رقم الاستعلام والدعم: 01289518413</p>
        </div>
        <table class="invoice-details-table">
            <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
            <tr><td><b>اسم العميل:</b> {c_name}</td><td><b>الهاتف:</b> {c_phone if c_phone else "غير محدد"}</td></tr>
            <tr><td><b>العنوان:</b> {c_address if c_address else "غير محدد"}</td><td><b>المسؤول:</b> {user}</td></tr>
            <tr><td><b>نوع الدفع:</b> {sale_type}</td><td><b>حالة التحصيل:</b> {collect_system} ({collect_date})</td></tr>
        </table>
        <table class="invoice-items-table">
            <tr><th>الصنف والبيان</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي الإجمالي</th></tr>
            <tr><td>{item_name}</td><td>{qty}</td><td>{item_price} جنيه</td><td>{discount}%</td><td style='font-weight: bold;'>{final_total} جنيه</td></tr>
        </table>
        <div class="total-words-area">💰 إجمالي المبلغ باللغة العربية: <span>{total_in_words}</span></div>
        <div class="invoice-footer-alert">⚠️ تنبيه: مدة الاستبدال والارتجاع 15 يوماً من تاريخ الفاتورة بشرط سلامة الغلاف الأصلي.</div>
    </div>

    <div class="invoice-page">
        <div class="invoice-header">
            <h3>📋 نسخة الإدارة المالية والحسابات</h3>
            <h1>🏢 {SHOWROOM_NAME}</h1>
            <p>العنوان: ابوحماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي</p>
        </div>
        <table class="invoice-details-table">
            <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
            <tr><td><b>اسم العميل:</b> {c_name}</td><td><b>الهاتف:</b> {c_phone if c_phone else "غير محدد"}</td></tr>
            <tr><td><b>نوع الدفع:</b> {sale_type}</td><td><b>المسؤول:</b> {user}</td></tr>
        </table>
        <table class="invoice-items-table">
            <tr><th>الصنف والبيان</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي الإجمالي</th></tr>
            <tr><td>{item_name}</td><td>{qty}</td><td>{item_price} جنيه</td><td>{discount}%</td><td style='font-weight: bold;'>{final_total} جنيه</td></tr>
        </table>
        <div class="total-words-area">💰 إجمالي المبلغ باللغة العربية: <span>{total_in_words}</span></div>
    </div>

    <div class="invoice-page">
        <div class="invoice-header">
            <h3>📦 نسخة مسؤول المخازن والصرف (أصناف وكميات فقط)</h3>
            <h1>🏢 {SHOWROOM_NAME}</h1>
            <p>التوجيه: يرجى صرف الأصناف المبينة أدناه لمستلم الفاتورة</p>
        </div>
        <table class="invoice-details-table">
            <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
            <tr><td><b>اسم العميل:</b> {c_name}</td><td><b>المسؤول المصدر:</b> {user}</td></tr>
            <tr><td><b>نوع الدفع:</b> {sale_type}</td><td><b>حالة الإذن:</b> جاهز للصرف</td></tr>
        </table>
        <table class="invoice-items-table">
            <tr><th>الصنف والبيان</th><th>الكمية المطلوبة للصرف</th></tr>
            <tr><td style='font-size: 15px; font-weight: bold;'>{item_name}</td><td style='font-size: 16px; font-weight: bold;'>{qty}</td></tr>
        </table>
        <div class="invoice-footer-alert" style="margin-top:40px;">توقيع أمين المخزن: ............................ | توقيع المستلم: ............................</div>
    </div>

    <script>
        setTimeout(function() {{
            window.print();
        }}, 600);
    </script>
    """
    return html_content

def get_download_link(html_str, filename):
    import base64
    b64 = base64.b64encode(html_str.encode('utf-8-sig')).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="display:block; text-align:center; margin-bottom:15px; color:#fff; background:#2e7d32; padding:10px; border-radius:5px; text-decoration:none; font-weight:bold;">📥 تحميل ملف الفاتورة بصيغة HTML للكمبيوتر</a>'

# --- شاشة الفاتورة والبيع ---
def sales_invoice_tab(inv_df, sales_df, contacts_df):
    st.header(f"📤 إنشاء فاتورة مبيعات جديدة - {SHOWROOM_NAME}")
    
    if inv_df.empty: 
        st.warning("⚠️ المخزن فارغ تماماً.")
        return inv_df, sales_df

    c_list = contacts_df['الاسم'].unique() if not contacts_df.empty else []
    c1, c2, c3, c4 = st.columns(4)
    cust_type = c1.radio("نوع العميل", ["سريع / غير مسجل", "مسجل مسبقاً"])
    
    c_name, c_phone, c_address = "", "", ""
    if cust_type == "مسجل مسبقاً" and len(c_list) > 0:
        c_name = c2.selectbox("اختر العميل", c_list)
        c_address = contacts_df[contacts_df['الاسم'] == c_name]['العنوان'].values[0] if 'العنوان' in contacts_df.columns else ""
        c_phone = contacts_df[contacts_df['الاسم'] == c_name]['الهاتف'].values[0] if 'الهاتف' in contacts_df.columns else ""
    else:
        c_name = c2.text_input("اسم العميل")
        c_phone = c3.text_input("رقم هاتف العميل")
        c_address = c4.text_input("عنوان العميل")
    
    st.markdown("---")
    cc1, cc2, cc3 = st.columns(3)
    sale_type = cc1.selectbox("طبيعة البيع", ["نقدي (كاش)", "آجل (على الحساب)"])
    
    collect_system = "دفعة كاملة كاش"
    collect_date = "فورياً"
    if sale_type == "آجل (على الحساب)":
        collect_system = cc2.selectbox("نظام تحصيل الفاتورة الآجلة", ["دفعة واحدة لاحقاً", "أقساط أسبوعية", "أقساط شهرية", "نظام دفعات مخصصة"])
        collect_date = str(cc3.date_input("تاريخ التحصيل المستهدف"))
    
    st.markdown("---")
    c5, c6, c7 = st.columns(3)
    selected_item = c5.selectbox("اختر المنتج للبيع", inv_df['اسم الصنف'].unique())
    qty = c6.number_input("الكمية المطلوبة", min_value=1, step=1)
    
    discount = 0.0
    user_role = st.session_state.get('role', 'مدير')
    if user_role in ["مدير", "مشرف"]:
        discount = c7.number_input("نسبة الخصم الممنوحة (%)", min_value=0.0, max_value=100.0, step=0.5)
    else: 
        c7.write("🔒 *صلاحية الخصم مغلقة للموظفين*")
        
    item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
    original_price = float(item_row['سعر البيع'])
    
    if original_price == 0.0:
        st.error("⚠️ تنبيه أمين النظام: سعر هذا الصنف مسجل بـ 0.0 في قاعدة البيانات!")
        item_price = st.number_input("الرجاء إدخال سعر بيع القطعة الفعلي يدوياً الآن لإصلاح الفاتورة:", min_value=0.01, value=1.0, key="manual_price_entry")
    else:
        item_price = original_price

    subtotal = item_price * qty
    discount_amount = subtotal * (discount / 100)
    final_total = subtotal - discount_amount
    
    st.info(f"📊 المتوفر بالمخزن: {item_row['الكمية']} قطعة | الصافي الإجمالي المطلوب: {final_total} جنيه")
    
    # استخدام session_state لعرض الفاتورة بعد الـ rerun لضمان الاستقرار الفوري
    if "invoice_ready" in st.session_state and st.session_state.invoice_ready:
        st.markdown(get_download_link(st.session_state.invoice_html, f"الفاتورة_{st.session_state.invoice_id}.html"), unsafe_allow_html=True)
        st.markdown(st.session_state.invoice_html, unsafe_allow_html=True)
        # مسح الفاتورة المؤقتة حتى لا تظل عالقة عند تغيير الأصناف
        del st.session_state.invoice_ready
    
    if st.button("🧾 إصدار وطباعة وحفظ الفاتورة الثلاثية المجمعة (A5)", use_container_width=True):
        idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
        
        if int(inv_df.at[idx, 'الكمية']) < qty: 
            st.error("❌ خطأ: الكمية المطلوبة غير متوفرة حالياً في المخزن!")
        elif not c_name: 
            st.error("❌ خطأ: يرجى كتابة اسم العميل أولاً لإصدار الفاتورة باسمه.")
        else:
            inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) - qty
            inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
            
            inv_id = "INV-" + str(int(datetime.now().timestamp()))
            current_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_user = st.session_state.get('user', 'admin')
            
            new_s = pd.DataFrame([{
                "رقم الفاتورة": inv_id, "التاريخ": current_datetime_str, "اسم العميل": c_name, 
                "هاتف العميل": c_phone, "العنوان": c_address, "نوع البيع": sale_type, 
                "نظام التحصيل": collect_system, "تاريخ التحصيل": collect_date, "الصنف": selected_item, 
                "الكمية": str(qty), "الخصم %": str(discount), "إجمالي البيع": str(final_total), "المسؤول": current_user
            }])
            
            sales_df = pd.concat([sales_df, new_s], ignore_index=True)
            sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
            
            # حفظ الفاتورة في جلسة العمل المؤقتة لعرضها بعد التحديث الفوري
            triple_html = generate_triple_invoice_html(
                inv_id, current_datetime_str, c_name, c_phone, c_address, 
                sale_type, collect_system, collect_date, current_user, 
                selected_item, qty, item_price, discount, final_total
            )
            st.session_state.invoice_html = triple_html
            st.session_state.invoice_id = inv_id
            st.session_state.invoice_ready = True
            
            st.success("🎉 تم تسجيل وحفظ الفاتورة بنجاح وجاري تحديث البيانات والطباعة...")
            st.rerun()  # 🔄 تحديث الشاشة فورياً لمزامنة جدول الجرد والتقارير
            
    return inv_df, sales_df

# --- نقطة انطلاق البرنامج (Main Executable) ---
if __name__ == "__main__":
    # تهيئة بيانات الجلسة الافتراضية لمنع الأخطاء البيضاء
    if 'role' not in st.session_state: st.session_state['role'] = 'مدير'
    if 'user' not in st.session_state: st.session_state['user'] = 'admin'
    
    # قراءة الملفات الحالية المحدثة
    inv_df = pd.read_csv(INVENTORY_FILE)
    sales_df = pd.read_csv(SALES_FILE)
    contacts_df = pd.read_csv(CONTACTS_FILE)
    
    # القائمة الجانبية للتنقل
    st.sidebar.title("🏢 لوحة التحكم")
    menu = ["📤 فاتورة بيع جديدة", "📊 عرض المخزون", "📜 سجل الفواتير القديمة"]
    choice = st.sidebar.radio("اختر الشاشة", menu)
    
    if choice == "📤 فاتورة بيع جديدة":
        inv_df, sales_df = sales_invoice_tab(inv_df, sales_df, contacts_df)
    elif choice == "📊 عرض المخزون":
        st.header("📊 حالة بضائع المخزن الحالية")
        st.dataframe(inv_df, use_container_width=True)
    elif choice == "📜 سجل الفواتير القديمة":
        st.header("📜 أرشيف فواتير مبيعات المعرض")
        st.dataframe(sales_df, use_container_width=True)
