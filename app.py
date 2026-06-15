import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64
from io import BytesIO

# إعدادات الصفحة والشكل العام
st.set_page_config(page_title="نظام معرض الكبير لإدارة المخازن", layout="wide")

# أسماء ملفات البيانات
INVENTORY_FILE = "inventory_data.csv"
USERS_FILE = "users_data.csv"
SALES_FILE = "sales_data.csv"
PURCHASES_FILE = "purchases_data.csv"
EXPENSES_FILE = "expenses_data.csv"
ATTENDANCE_FILE = "attendance_data.csv"
CONTACTS_FILE = "contacts_data.csv"
PERMISSIONS_FILE = "permissions_config.csv"
SETTINGS_FILE = "system_settings.csv"

# دالة تحويل الأرقام إلى كلمات عربية
def number_to_arabic_words(number):
    try:
        num = int(float(number))
        if num == 0: return "صفر جنيهاً مصرياً لا غير"
        
        units = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"]
        tens = ["", "عشرة", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
        hundreds = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]
        
        words = []
        if num >= 1000:
            thousands = num // 1000
            if thousands == 1: words.append("ألف")
            elif thousands == 2: words.append("ألفين")
            elif thousands >= 3 and thousands <= 10: words.append(f"{units[thousands]} آلاف")
            else: words.append(f"{thousands} ألف")
            num %= 1000
            
        if num >= 100:
            words.append(hundreds[num // 100])
            num %= 100
            
        if num > 0:
            if len(words) > 0: words.append("و")
            if num < 10: words.append(units[num])
            elif num < 20:
                special = ["عشرة", "أحد عشر", "إثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
                words.append(special[num - 10])
            else:
                unit_part = num % 10
                tens_part = num // 10
                if unit_part > 0:
                    words.append(f"{units[unit_part]} و{tens[tens_part]}")
                else:
                    words.append(tens[tens_part])
                    
        return "فقط " + " و ".join([w for w in words if w != "و"]) + " جنيهاً مصرياً لا غير"
    except:
        return ""

def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([
            {"username": "admin", "password": "123", "role": "مدير"},
            {"username": "sharaf", "password": "456", "role": "مشرف"},
            {"username": "user1", "password": "111", "role": "موظف"}
        ]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "هاتف العميل", "العنوان", "نوع البيع", "نظام التحصيل", "تاريخ التحصيل", "الصنف", "الكمية", "الخصم %", "إجمالي البيع", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(PURCHASES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "المورد", "الصنف", "الكمية", "إجمالي الشراء", "المسؤول"]).to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(EXPENSES_FILE):
        pd.DataFrame(columns=["التاريخ", "البيان", "المبلغ", "المسؤول"]).to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(ATTENDANCE_FILE):
        pd.DataFrame(columns=["الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف"]).to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(CONTACTS_FILE):
        pd.DataFrame(columns=["النوع", "الاسم", "الهاتف", "العنوان"]).to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
    
    if not os.path.exists(SETTINGS_FILE):
        pd.DataFrame([{"اسم المعرض": "معرض الكبير", "العنوان": "ابوحماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي", "رقم الدعم": "0100XXXXXXX"}]).to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')

    all_pages = [
        "📦 تكويد الأصناف", "📊 رصيد أول المدة Excel", "🔍 حالة المخزن", 
        "🤝 العملاء والموردين", "📥 فاتورة شراء جديدة", "📤 فاتورة بيع جديدة", 
        "🔎 البحث عن الفواتير وطباعتها", "📈 تقارير البيع والشراء والأرباح", "💸 المصاريف", 
        "⏰ الحضور والانصراف", "⚙️ إدارة وتعديل الصلاحيات والحسابات", "⚙️ إعدادات بيانات الفاتورة والدعم"
    ]
    
    if not os.path.exists(PERMISSIONS_FILE):
        default_perms = []
        for page in all_pages:
            default_perms.append({
                "اسم الصفحة": page, 
                "مدير": True, 
                "مشرف": True if page in ["🔍 حالة المخزن", "📥 فاتورة شراء جديدة", "📤 فاتورة بيع جديدة", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False, 
                "موظف": True if page in ["🔍 حالة المخزن", "📤 فاتورة بيع جديدة", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False
            })
        pd.DataFrame(default_perms).to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')

init_files()

settings_df = pd.read_csv(SETTINGS_FILE)
SHOWROOM_NAME = settings_df.iloc[0]["اسم المعرض"]
SHOWROOM_ADDRESS = settings_df.iloc[0]["العنوان"]
INQUIRY_NUMBER = settings_df.iloc[0]["رقم الدعم"]

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "موظف"

# دالة توليد الفاتورة الثلاثية المحدثة بالوقت والتفقيط وعرض صفحة الـ A5 بالكامل
def generate_triple_invoice_html(inv_id, datetime_str, client_name, phone, address, pay_type, collect_system, collect_date, user, item, qty, price, discount, final_total):
    collect_info = f"<tr><td><b>نظام التحصيل:</b> {collect_system}</td><td><b>تاريخ التحصيل:</b> {collect_date}</td></tr>" if pay_type == "آجل (على الحساب)" else ""
    arabic_total_words = number_to_arabic_words(final_total)
    
    standard_table_th = "<tr><th>الصنف والبيان</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي الإجمالي</th></tr>"
    standard_table_td = f"<tr><td>{item}</td><td>{qty}</td><td>{price} جنيه</td><td>{discount}%</td><td style='font-weight: bold;'>{final_total} جنيه</td></tr>"
    
    store_table_th = "<tr><th>الصنف والبيان</th><th>الكمية المطلوبة للصرف</th></tr>"
    store_table_td = f"<tr><td style='font-size: 15px; font-weight: bold;'>{item}</td><td style='font-size: 16px; font-weight: bold;'>{qty}</td></tr>"

    html_content = f"""
    <div class="triple-print-wrapper">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
            @page {{ size: A5 portrait; margin: 0; }}
            @media print {{
                body {{ direction: rtl; background: #fff; color: #000; padding: 0; margin: 0; }}
                header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-zone, .stButton, .download-btn-area {{ display: none !important; }}
                .invoice-page {{ width: 148mm; height: 210mm; box-sizing: border-box; padding: 10mm !important; margin: 0 !important; page-break-after: always; border: none !important; box-shadow: none !important; }}
            }}
            .triple-print-wrapper {{ direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; }}
            .invoice-page {{ width: 148mm; max-width: 100%; border: 2px solid #000; padding: 20px; margin: 20px auto; background: #fff; color: #000; box-sizing: border-box; page-break-after: always; }}
            .invoice-header {{ text-align: center; border-bottom: 2px solid #000; padding-bottom: 8px; margin-bottom: 10px; }}
            .invoice-header h3 {{ margin: 0; background: #000; color: #fff; padding: 4px 12px; display: inline-block; font-size: 14px; border-radius: 4px; }}
            .invoice-header h1 {{ margin: 6px 0; font-size: 24px; color: #000; font-weight: 700; }}
            .invoice-header p {{ font-size: 12px; margin: 2px 0; color: #000; }}
            .invoice-details-table {{ width: 100%; font-size: 13px; margin-top: 5px; border-bottom: 1px solid #000; padding-bottom: 8px; }}
            .invoice-details-table td {{ padding: 4px 0; width: 50%; }}
            .invoice-items-table {{ width: 100%; border-collapse: collapse; margin-top: 15px; border: 2px solid black; font-size: 13px; text-align: center; }}
            .invoice-items-table th {{ background: #f2f2f2; border: 1px solid black; padding: 8px; font-weight: bold; color: #000; }}
            .invoice-items-table td {{ border: 1px solid black; padding: 8px; }}
            .total-words-area {{ margin-top: 15px; background: #fff; border: 1px dashed #000; padding: 8px; font-size: 14px; font-weight: bold; text-align: right; }}
            .invoice-footer-alert {{ margin-top: 15px; font-size: 11px; font-weight: bold; text-align: center; border: 1px solid #000; padding: 6px; background: #fff; }}
            .print-trigger-btn {{ background-color: #28a745; color: white; padding: 12px 24px; margin: 10px auto; border: none; border-radius: 5px; cursor: pointer; font-size: 15px; font-weight: bold; display: block; text-align: center; }}
        </style>
        
        <div class="no-print-zone" style="text-align:center; margin-bottom:20px;">
            <button class="print-trigger-btn" onclick="window.print()">🖨️ إصدار وطباعة الفاتورة الثلاثية فوراً (A5)</button>
        </div>

        <div class="invoice-page">
            <div class="invoice-header">
                <h3>📋 نسخة العميل (أصل الفاتورة)</h3>
                <h1>🏢 {SHOWROOM_NAME}</h1>
                <p>العنوان: {SHOWROOM_ADDRESS}</p>
                <p style="font-size: 12px; font-weight: bold;">📞 رقم الاستعلام والدعم: {INQUIRY_NUMBER}</p>
            </div>
            <table class="invoice-details-table">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>الهاتف:</b> {phone if phone else 'غير محدد'}</td></tr>
                <tr><td><b>العنوان:</b> {address if address else 'غير محدد'}</td><td><b>المسؤول:</b> {user}</td></tr>
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td></td></tr>
                {collect_info}
            </table>
            <table class="invoice-items-table">
                {standard_table_th}
                {standard_table_td}
            </table>
            <div class="total-words-area">💰 إجمالي المبلغ باللغة العربية: <span style="color:#000;">{arabic_total_words}</span></div>
            <div class="invoice-footer-alert">⚠️ تنبيه: مدة الاستبدال والارتجاع 15 يوماً من تاريخ الفاتورة بشرط سلامة الغلاف الأصلي.</div>
        </div>

        <div class="invoice-page">
            <div class="invoice-header">
                <h3>📋 نسخة الإدارة المالية والحسابات</h3>
                <h1>🏢 {SHOWROOM_NAME}</h1>
                <p>العنوان: {SHOWROOM_ADDRESS}</p>
            </div>
            <table class="invoice-details-table">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>الهاتف:</b> {phone if phone else 'غير محدد'}</td></tr>
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>المسؤول:</b> {user}</td></tr>
                {collect_info}
            </table>
            <table class="invoice-items-table">
                {standard_table_th}
                {standard_table_td}
            </table>
            <div class="total-words-area">💰 إجمالي المبلغ باللغة العربية: <span style="color:#000;">{arabic_total_words}</span></div>
        </div>

        <div class="invoice-page">
            <div class="invoice-header">
                <h3>📦 نسخة مسؤول المخازن والصرف (أصناف وكميات فقط)</h3>
                <h1>🏢 {SHOWROOM_NAME}</h1>
                <p>التوجيه: يرجى صرف الأصناف المبينة أدناه لمستلم الفاتورة</p>
            </div>
            <table class="invoice-details-table">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ والوقت:</b> {datetime_str}</td></tr>
                <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>المسؤول المصدر:</b> {user}</td></tr>
                <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>حالة الإذن:</b> جاهز للصرف</td></tr>
            </table>
            <table class="invoice-items-table">
                {store_table_th}
                {store_table_td}
            </table>
            <div class="invoice-footer-alert" style="margin-top:40px;">توقيع أمين المخزن: ............................ | توقيع المستلم: ............................</div>
        </div>

        <script>
            setTimeout(function() {{
                window.print();
            }}, 500);
        </script>
    </div>
    """
    return html_content

def get_download_link(html_content, filename="invoice.html"):
    b64 = base64.b64encode(html_content.encode('utf-8-sig')).decode()
    return f'<div class="download-btn-area"><a href="data:text/html;base64,{b64}" download="{filename}" style="display: block; padding: 12px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px; font-weight: bold; text-align: center; margin: 15px auto; max-width:400px;">📥 اضغط هنا لتنزيل وحفظ ملف الفاتورة في التحميلات فوراً</a></div>'

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    st.title(f"🏢 نظام {SHOWROOM_NAME} - تسجيل الدخول")
    user_input = st.text_input("اسم المستخدم", key="login_user").strip()
    pw_input = st.text_input("كلمة المرور", type="password", key="login_pw").strip()
    
    if st.button("دخول للنظام", use_container_width=True):
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        match = u_df[(u_df['username'] == user_input) & (u_df['password'] == pw_input)]
        if not match.empty:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.session_state.role = match.iloc[0]['role']
            st.success(f"مرحباً بك يا {user_input} ({st.session_state.role})")
            st.rerun()
        else: st.error("بيانات الدخول خاطئة.")
else:
    perms_df = pd.read_csv(PERMISSIONS_FILE)
    current_role = st.session_state.role
    
    # فلترة الصفحات النشطة حسب صلاحية المستخدم الحالية
    allowed_actions = perms_df[perms_df[current_role] == True]["اسم الصفحة"].tolist()
    sidebar_pages = [p for p in allowed_actions]
    
    if not sidebar_pages: sidebar_pages = ["🔍 حالة المخزن"]
        
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"الرتبة: **{st.session_state.role}**")
    
    choice = st.sidebar.selectbox("الانتقال إلى", sidebar_pages)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # تحميل البيانات مع التأكد من الأنواع الصحيحة منعاً للأخطاء الحسابية
    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
    inv_df["الكمية"] = pd.to_numeric(inv_df["الكمية"], errors='coerce').fillna(0).astype(int)
    inv_df["سعر الشراء"] = pd.to_numeric(inv_df["سعر الشراء"], errors='coerce').fillna(0.0)
    inv_df["سعر البيع"] = pd.to_numeric(inv_df["سعر البيع"], errors='coerce').fillna(0.0)

    sales_df = pd.read_csv(SALES_FILE, dtype=str)
    purchases_df = pd.read_csv(PURCHASES_FILE, dtype=str)
    exp_df = pd.read_csv(EXPENSES_FILE)
    att_df = pd.read_csv(ATTENDANCE_FILE)
    contacts_df = pd.read_csv(CONTACTS_FILE, dtype=str)

    # --- 1. صفحة تكويد الأصناف ---
    if "تكويد الأصناف" in choice:
        st.header("📦 تكويد وتسجيل أصناف جديدة")
        st.dataframe(inv_df, use_container_width=True)
        st.subheader("➕ إضافة صنف جديد")
        c1, c2, c3, c4 = st.columns(4)
        iid = c1.text_input("كود الصنف (الباركود / ID)")
        iname = c2.text_input("اسم المنتج")
        ipurchase = c3.number_input("سعر الشراء الافتراضي", min_value=0.0, step=1.0)
        isale = c4.number_input("سعر البيع الافتراضي", min_value=0.0, step=1.0)
        
        if st.button("تكويد وحفظ"):
            if iid and iname:
                if iid in inv_df["كود الصنف"].values: st.warning("⚠️ هذا الكود مسجل مسبقاً!")
                else:
                    new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "الكمية": 0, "سعر الشراء": ipurchase, "سعر البيع": isale}])
                    inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("🎉 تم تكويد المنتج بنجاح!")
                    st.rerun()

    # --- 2. صفحة رفع رصيد أول المدة ---
    elif "رصيد أول المدة" in choice:
        st.header("📊 رفع بضائع ورصيد أول المدة عبر ملف Excel")
        uploaded_file = st.file_uploader("اختر شيت الاكسل الخاص بالبضائع", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                excel_df = pd.read_excel(uploaded_file, dtype={"كود الصنف": str})
                st.dataframe(excel_df)
                if st.button("تأكيد ودمج الملف في رصيد أول المدة"):
                    combined_df = pd.concat([inv_df, excel_df]).drop_duplicates(subset=['كود الصنف'], keep='last')
                    combined_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("🚀 تم رفع وتحديث المخزن بنجاح!")
                    st.rerun()
            except Exception as e: st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")

    # --- 3. صفحة حالة المخزن ---
    elif "حالة المخزن" in choice:
        st.header("🔍 جرد بضائع المخزن الحالية")
        st.dataframe(inv_df, use_container_width=True)

    # --- 4. صفحة العملاء والموردين ---
    elif "العملاء والموردين" in choice:
        st.header("🤝 إدارة بيانات العملاء والموردين")
        st.dataframe(contacts_df, use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        ctype = c1.selectbox("النوع", ["عميل", "مورد"])
        cname = c2.text_input("الاسم")
        cphone = c3.text_input("الهاتف")
        caddress = c4.text_input("العنوان")
        if st.button("حفظ الجهة"):
            if cname:
                new_c = pd.DataFrame([{"النوع": ctype, "الاسم": cname, "الهاتف": cphone, "العنوان": caddress}])
                contacts_df = pd.concat([contacts_df, new_c], ignore_index=True)
                contacts_df.to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم الحفظ!")
                st.rerun()

    # --- 5. صفحة المشتريات ---
    elif "فاتورة شراء جديدة" in choice:
        st.header("📥 تسجيل وإدارة فواتير المشتريات")
        t_new, t_manage = st.tabs(["📥 تسجيل فاتورة شراء جديدة", "✏️ تعديل وحذف فواتير الشراء"])
        
        with t_new:
            if inv_df.empty: st.warning("⚠️ قم بتكويد بضائع أولاً.")
            else:
                m_list = contacts_df[contacts_df['النوع'] == 'مورد']['الاسم'].unique()
                if len(m_list) == 0: m_list = ["مورد عام"]
                c1, c2, c3 = st.columns(3)
                vendor = c1.selectbox("المورد", m_list)
                item = c2.selectbox("الصنف المشترى", inv_df['اسم الصنف'].unique())
                qty = c3.number_input("الكمية", min_value=1, step=1)
                
                item_row = inv_df[inv_df['اسم الصنف'] == item].iloc[0]
                total = float(item_row['سعر الشراء']) * qty
                if st.button("حفظ المشتريات"):
                    idx = inv_df[inv_df['اسم الصنف'] == item].index[0]
                    inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) + qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    pur_id = "PUR-" + str(int(datetime.now().timestamp()))
                    new_p = pd.DataFrame([{"رقم الفاتورة": pur_id, "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "المورد": vendor, "الصنف": item, "الكمية": str(qty), "إجمالي الشراء": str(total), "المسؤول": st.session_state.user}])
                    purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                    purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم تسجيل الوارد!")
                    st.rerun()
                        
        with t_manage:
            st.subheader("⚙️ مراجعة وتعديل وحذف فواتير الشراء السابقة")
            if purchases_df.empty: st.info("لا توجد فواتير شراء مسجلة حالياً.")
            else:
                st.dataframe(purchases_df, use_container_width=True)
                target_pur_id = st.selectbox("اختر رقم فاتورة الشراء للإجراء", purchases_df["رقم الفاتورة"].unique())
                p_row = purchases_df[purchases_df["رقم الفاتورة"] == target_pur_id].iloc[0]
                
                if st.button("❌ حذف فاتورة الشراء هذه بالكامل وخصمها من المخزن", use_container_width=True):
                    p_item = p_row["الصنف"]
                    p_qty = int(p_row["الكمية"])
                    if p_item in inv_df["اسم الصنف"].values:
                        inv_idx = inv_df[inv_df["اسم الصنف"] == p_item].index[0]
                        inv_df.at[inv_idx, "الكمية"] = max(0, int(inv_df.at[inv_idx, "الكمية"]) - p_qty)
                        inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    purchases_df = purchases_df[purchases_df["رقم الفاتورة"] != target_pur_id]
                    purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    st.success("🔥 تم حذف فاتورة الشراء وتعديل رصيد المخزن!")
                    st.rerun()

    # --- 6. صفحة فاتورة بيع جديدة ---
    elif "فاتورة بيع جديدة" in choice:
        st.header(f"📤 إنشاء فاتورة مبيعات جديدة - {SHOWROOM_NAME}")
        if inv_df.empty: st.warning("⚠️ المخزن فارغ.")
        else:
            c_list = contacts_df[contacts_df['النوع'] == 'عميل']['الاسم'].unique()
            c1, c2, c3, c4 = st.columns(4)
            cust_type = c1.radio("نوع العميل", ["سريع / غير مسجل", "مسجل مسبقاً"])
            
            c_phone = ""
            if cust_type == "مسجل مسبقاً" and len(c_list) > 0:
                c_name = c2.selectbox("اختر العميل", c_list)
                c_address = contacts_df[contacts_df['الاسم'] == c_name]['العنوان'].values[0]
                c_phone = contacts_df[contacts_df['الاسم'] == c_name]['الهاتف'].values[0]
            else:
                c_name = c2.text_input("اسم العميل")
                c_phone = c3.text_input("رقم هاتف العميل")
                c_address = c4.text_input("عنوان العميل")
            
            visit_count = 0
            if c_name and not sales_df.empty:
                visit_count = len(sales_df[sales_df["اسم العميل"] == c_name])
            elif c_phone and not sales_df.empty:
                visit_count = len(sales_df[sales_df["هاتف العميل"] == c_phone])
                
            st.info(f"📊 عدد زيارات ومبيعات هذا العميل السابقة في النظام: **{visit_count}** مرة")
            
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
            if st.session_state.role in ["مدير", "مشرف"]:
                discount = c7.number_input("نسبة الخصم الممنوحة (%)", min_value=0.0, max_value=100.0, step=0.5)
            else: c7.write("🔒 *صلاحية الخصم مغلقة للموظفين*")
                
            item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
            subtotal = float(item_row['سعر البيع']) * qty
            discount_amount = subtotal * (discount / 100)
            final_total = subtotal - discount_amount
            
            st.warning(f"📊 المتوفر بالمخزن: {item_row['الكمية']} | الصافي المطلوب: {final_total} جنيه")
            
            if st.button("🧾 إصدار وطباعة وحفظ الفاتورة الثلاثية المجمعة (A5)", use_container_width=True):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                if int(inv_df.at[idx, 'الكمية']) < qty: st.error("❌ الكمية لا تكفي في المخزن!")
                elif not c_name: st.error("❌ يرجى تحديد أو كتابة اسم العميل أولاً.")
                else:
                    inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) - qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    # جلب الوقت والتاريخ الدقيق لحل مشكلة توقيت الفواتير
                    current_datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    new_s = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": current_datetime_str, "اسم العميل": c_name, "هاتف العميل": c_phone, "العنوان": c_address, "نوع البيع": sale_type, "نظام التحصيل": collect_system, "تاريخ التحصيل": collect_date, "الصنف": selected_item, "الكمية": str(qty), "الخصم %": str(discount), "إجمالي البيع": str(final_total), "المسؤول": st.session_state.user}])
                    sales_df = pd.concat([sales_df, new_s], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    st.success("🎉 تم تسجيل وحفظ الفاتورة بنجاح في النظام!")
                    
                    triple_html = generate_triple_invoice_html(inv_id, current_datetime_str, c_name, c_phone, c_address, sale_type, collect_system, collect_date, st.session_state.user, selected_item, qty, item_row['سعر البيع'], discount, final_total)
                    st.markdown(get_download_link(triple_html, f"الفاتورة_الثلاثية_{inv_id}.html"), unsafe_allow_html=True)
                    st.markdown(triple_html, unsafe_allow_html=True)

    # --- 7. صفحة البحث عن فواتير البيع وطباعتها ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 نظام البحث والمراجعة وطباعة الفواتير")
        if sales_df.empty: st.info("لا توجد فواتير مبيعات مسجلة في النظام حتى الآن.")
        else:
            search_query = st.text_input("ابحث عن فاتورة مبيعات (أدخل رقم الفاتورة، اسم العميل أو الهاتف)").strip()
            if search_query:
                filtered_sales = sales_df[sales_df['رقم الفاتورة'].str.contains(search_query, case=False, na=False) | sales_df['اسم العميل'].str.contains(search_query, case=False, na=False)]
            else: filtered_sales = sales_df
                
            st.dataframe(filtered_sales, use_container_width=True)
            
            if not filtered_sales.empty:
                selected_inv_id = st.selectbox("اختر رقم الفاتورة لإعادة الطباعة والسحب", filtered_sales['رقم الفاتورة'].unique())
                f_row = sales_df[sales_df['رقم الفاتورة'] == selected_inv_id].iloc[0]
                
                match_inv_item = inv_df[inv_df['اسم الصنف'] == f_row['الصنف']]
                unit_price = match_inv_item.iloc[0]['سعر البيع'] if not match_inv_item.empty else 0.0
                
                p_phone = f_row['هاتف العميل'] if 'هاتف العميل' in f_row else ""
                p_sys = f_row['نظام التحصيل'] if 'نظام التحصيل' in f_row else "كاش"
                p_date = f_row['تاريخ التحصيل'] if 'تاريخ التحصيل' in f_row else "فوراً"
                p_time = f_row['التاريخ'] if 'التاريخ' in f_row else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                triple_html = generate_triple_invoice_html(f_row['رقم الفاتورة'], p_time, f_row['اسم العميل'], p_phone, f_row['العنوان'], f_row['نوع البيع'], p_sys, p_date, f_row['المسؤول'], f_row['الصنف'], int(f_row['الكمية']), unit_price, float(f_row['الخصم %']), float(f_row['إجمالي البيع']))
                st.markdown(get_download_link(triple_html, f"إعادة_طباعة_فاتورة_{selected_inv_id}.html"), unsafe_allow_html=True)
                st.markdown(triple_html, unsafe_allow_html=True)

    # --- 8. صفحة التقارير المالية المتكاملة والأرباح ---
    elif "تقارير البيع والشراء والأرباح" in choice:
        st.header(f"📈 التقارير المالية التفصيلية وحساب الأرباح لـ {SHOWROOM_NAME}")
        
        # حساب إجماليات النظام
        total_sales = pd.to_numeric(sales_df['إجمالي البيع'], errors='coerce').sum()
        total_purchases = pd.to_numeric(purchases_df['إجمالي الشراء'], errors='coerce').sum()
        total_expenses = pd.to_numeric(exp_df['المبلغ'], errors='coerce').sum()
        net_profit = total_sales - (total_purchases + total_expenses)
        
        # عرض المؤشرات المالية الرئيسية
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إجمالي المبيعات (المداخيل)", f"{total_sales:,.2f} جنيه", delta_color="normal")
        m2.metric("إجمالي المشتريات (البضائع)", f"{total_purchases:,.2f} جنيه")
        m3.metric("إجمالي المصاريف العمومية", f"{total_expenses:,.2f} جنيه")
        m4.metric("صافي الأرباح الدقيقة", f"{net_profit:,.2f} جنيه", delta=f"{net_profit:,.2f} جنيه")
        
        st.markdown("---")
        t1, t2 = st.tabs(["📋 سجل حركة المبيعات", "📋 سجل حركة المشتريات"])
        with t1:
            st.subheader("مبيعات المعرض")
            st.dataframe(sales_df, use_container_width=True)
        with t2:
            st.subheader("مشتريات المعرض الواردة")
            st.dataframe(purchases_df, use_container_width=True)

    # --- 9. صفحة المصاريف ---
    elif "المصاريف" in choice:
        st.header("💸 تسجيل المصاريف الإدارية والعمومية")
        st.dataframe(exp_df, use_container_width=True)
        b1 = st.text_input("بيان الصرف")
        b2 = st.number_input("المبلغ المنصرف", min_value=0.0, step=10.0)
        if st.button("حفظ المصروف"):
            if b1 and b2 > 0:
                new_e = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d"), "البيان": b1, "المبلغ": b2, "المسؤول": st.session_state.user}])
                exp_df = pd.concat([exp_df, new_e], ignore_index=True)
                exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم حفظ البند مصروفات!")
                st.rerun()

    # --- 10. الحضور والانصراف مع سحب التقرير excel ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ تسجيل حضور وانصراف موظفي المعرض")
        
        # لوحة تفاعلية للموظف الحالي لتسجيل الوقت
        st.subheader(f"تسجيل الميقات الفوري للمستخدم الحالى: ({st.session_state.user})")
        col_att1, col_att2 = st.columns(2)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if col_att1.button("🟢 تسجيل حضور الآن"):
            # التحقق مما إذا كان قد سجل حضور اليوم مسبقاً
            match = att_df[(att_df["الموظف"] == st.session_state.user) & (att_df["التاريخ"] == current_date)]
            if not match.empty:
                st.warning("⚠️ أنت مسجل حضور بالفعل لهذا اليوم!")
            else:
                new_attendance = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": current_date, "وقت الحضور": current_time, "وقت الانصراف": "لم ينصرف بعد"}])
                att_df = pd.concat([att_df, new_attendance], ignore_index=True)
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"🎉 تم تسجيل حضورك اليوم في تمام الساعة: {current_time}")
                st.rerun()
                
        if col_att2.button("🔴 تسجيل انصراف الآن"):
            idx_match = att_df[(att_df["الموظف"] == st.session_state.user) & (att_df["التاريخ"] == current_date)].index
            if len(idx_match) > 0:
                att_df.at[idx_match[0], "وقت الانصراف"] = current_time
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"🚀 تم تسجيل انصرافك بنجاح في تمام الساعة: {current_time}")
                st.rerun()
            else:
                st.error("❌ لم يتم العثور على حركة حضور لك اليوم لتسجيل الانصراف عليها!")

        st.markdown("---")
        st.subheader("📋 شيت حركة الحضور والانصراف العام")
        st.dataframe(att_df, use_container_width=True)
        
        # كود تصدير وسحب شيت الحضور والانصراف لملف Excel
        if not att_df.empty:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                att_df.to_excel(writer, index=False, sheet_name='الحضور والانصراف')
            processed_data = output.getvalue()
            
            st.download_button(
                label="📥 تحميل وسحب شيت تقرير الحضور والانصراف الكامل (Excel)",
                data=processed_data,
                file_name=f"تقرير_الحضور_والانصراف_{current_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    # --- 11. صفحة إدارة وتعديل الصلاحيات وإضافة الحسابات المتكاملة ---
    elif "إدارة وتعديل الصلاحيات" in choice:
        st.header("⚙️ إدارة الصلاحيات وحسابات موظفي المعرض")
        
        tab_users, tab_roles = st.tabs(["👤 إدارة اليوزرات والحسابات", "🔒 التحكم في صلاحيات الصفحات"])
        
        with tab_users:
            u_df = pd.read_csv(USERS_FILE, dtype=str)
            st.subheader("المستخدمين الحاليين بالنظام")
            st.dataframe(u_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("➕ إضافة مستخدم جديد للنظام")
            with st.form("add_user_form"):
                new_username = st.text_input("اسم المستخدم الجديد (بالإنجليزي أو العربي بدون فواصل)").strip()
                new_password = st.text_input("كلمة مرور الحساب").strip()
                new_role = st.selectbox("الرتبة / الصلاحية القانونية", ["مدير", "مشرف", "موظف"])
                
                if st.form_submit_button("➕ حفظ وإنشاء الحساب الآن"):
                    if new_username and new_password:
                        if new_username in u_df["username"].values:
                            st.error("❌ اسم المستخدم هذا مسجل مسبقاً بالمشروع!")
                        else:
                            new_acc = pd.DataFrame([{"username": new_username, "password": new_password, "role": new_role}])
                            u_df = pd.concat([u_df, new_acc], ignore_index=True)
                            u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                            st.success(f"🎉 تم إنشاء حساب جديد لـ {new_username} برتبة {new_role}!")
                            st.rerun()
                    else:
                        st.error("❌ يرجى ملء كافة حقول اسم المستخدم وكلمة المرور.")
                        
        with tab_roles:
            st.subheader("🔑 تفعيل وإخفاء الصفحات عن الرتب")
            st.info("قم بتحديد أو إلغاء تحديد الصفحات لكل رتبة، ثم اضغط على حفظ التعديلات لتحديث شريط التنقل الجانبي فوراً.")
            
            # عرض الصلاحيات في جدول تفاعلي قابل للتعديل
            edited_perms_df = st.data_editor(perms_df, use_container_width=True, disabled=["اسم الصفحة"])
            
            if st.button("💾 حفظ الصلاحيات والتعديلات الجديدة"):
                edited_perms_df.to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')
                st.success("🚀 تم تحديث صلاحيات النظام وإخفاء/إظهار القوائم بنجاح لكل الرتب!")
                st.rerun()

    # --- 12. صفحة إعدادات بيانات الفاتورة والدعم ---
    elif "إعدادات بيانات الفاتورة والدعم" in choice:
        st.header("⚙️ تحديث وإعداد بيانات طباعة الفاتورة والدعم")
        with st.form("settings_form_updated"):
            new_showroom_name = st.text_input("اسم المعرض / الشركة بالفاتورة", value=SHOWROOM_NAME)
            new_showroom_address = st.text_input("العنوان بالتفصيل بالفاتورة", value=SHOWROOM_ADDRESS)
            new_inquiry_number = st.text_input("رقم الدعم الفني للفواتير", value=INQUIRY_NUMBER)
            if st.form_submit_button("💾 حفظ وتحديث الإعدادات"):
                updated_settings = pd.DataFrame([{"اسم المعرض": new_showroom_name, "العنوان": new_showroom_address, "رقم الدعم": new_inquiry_number}])
                updated_settings.to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')
                st.success("🚀 تم تحديث بيانات الفاتورة بنجاح!")
                st.rerun()
