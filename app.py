import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# إعدادات الصفحة والشكل العام
st.set_page_config(page_title="نظام معرض الكبير لإدارة المخازن", layout="wide")

# أسماء ملفات البيانات (ثابتة ومحمية من الحذف)
INVENTORY_FILE = "inventory_data.csv"
USERS_FILE = "users_data.csv"
SALES_FILE = "sales_data.csv"
PURCHASES_FILE = "purchases_data.csv"
EXPENSES_FILE = "expenses_data.csv"
ATTENDANCE_FILE = "attendance_data.csv"
CONTACTS_FILE = "contacts_data.csv"
PERMISSIONS_FILE = "permissions_config.csv" 
SETTINGS_FILE = "system_settings.csv"

# دالة تهيئة الملفات للتأكد من وجود البيانات والتهيئة الافتراضية دون مسح القديم
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
        "🔎 البحث عن الفواتير وطباعتها", "📈 تقارير البيع والشراء", "💸 المصاريف", 
        "⏰ الحضور والانصراف", "⚙️ إدارة وتعديل الصلاحيات", "⚙️ إعدادات بيانات الفاتورة والدعم",
        "✏️ تعديل الفواتير السابقة", "❌ حذف الفواتير السابقة" 
    ]
    
    if not os.path.exists(PERMISSIONS_FILE):
        default_perms = []
        for page in all_pages:
            default_perms.append({
                "اسم الصفحة": page, "مدير": True, 
                "مشرف": True if page in ["🔍 حالة المخزن", "📥 فاتورة شراء جديدة", "📤 فاتورة بيع جديدة", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False, 
                "موظف": True if page in ["🔍 حالة المخزن", "📤 فاتورة بيع جديدة", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"] else False
            })
        pd.DataFrame(default_perms).to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')
    else:
        existing_perms = pd.read_csv(PERMISSIONS_FILE)
        missing_pages = [p for p in all_pages if p not in existing_perms["اسم الصفحة"].values]
        if missing_pages:
            new_rows = []
            for mp in missing_pages:
                new_rows.append({"اسم الصفحة": mp, "مدير": True, "مشرف": False, "موظف": False})
            updated_perms = pd.concat([existing_perms, pd.DataFrame(new_rows)], ignore_index=True)
            updated_perms.to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')

init_files()

# قراءة إعدادات الفاتورة الديناميكية
settings_df = pd.read_csv(SETTINGS_FILE)
SHOWROOM_NAME = settings_df.iloc[0]["اسم المعرض"]
SHOWROOM_ADDRESS = settings_df.iloc[0]["العنوان"]
INQUIRY_NUMBER = settings_df.iloc[0]["رقم الدعم"]

if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "موظف"

# دالة توليد الفاتورة HTML وميزة تحميلها التلقائي للتحميلات
def generate_a5_html_invoice(copy_title, inv_id, date, client_name, phone, address, pay_type, collect_system, collect_date, user, item, qty, price, discount, final_total):
    collect_info = f"<tr><td><b>نظام التحصيل:</b> {collect_system}</td><td><b>تاريخ التحصيل:</b> {collect_date}</td></tr>" if pay_type == "آجل (على الحساب)" else ""
    
    html_content = f"""
    <div class="print-invoice-container">
        <style>
            @page {{ size: A5 portrait; margin: 5mm; }}
            @media print {{
                body {{ direction: rtl; background: #fff; color: #000; }}
                header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-btn, .stButton {{ display: none !important; }}
                .print-invoice-container {{ border: 1px solid #000 !important; box-shadow: none !important; padding: 5mm !important; margin: 0 auto 15mm auto !important; page-break-after: always; }}
            }}
            .print-invoice-container {{ width: 140mm; max-width: 100%; border: 2px dashed #333; padding: 15px; margin: 15px auto; direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background: #fff; color: #000; border-radius: 6px; box-sizing: border-box; }}
            .invoice-header {{ text-align: center; font-weight: bold; }}
            .invoice-header h2 {{ margin: 0; color: #444; font-size: 16px; }}
            .invoice-header h1 {{ margin: 5px 0; font-size: 20px; color: #000; }}
            .invoice-header p {{ font-size: 11px; margin: 2px; color: #555; }}
            .invoice-details-table {{ width: 100%; font-size: 12px; margin-top: 10px; border-bottom: 1px solid #000; padding-bottom: 5px; }}
            .invoice-items-table {{ width: 100%; border-collapse: collapse; margin-top: 8px; border: 1px solid black; font-size: 12px; text-align: center; }}
            .invoice-items-table th {{ background: #f2f2f2; border: 1px solid black; padding: 6px; font-weight: bold; }}
            .invoice-items-table td {{ border: 1px solid black; padding: 6px; }}
            .invoice-footer-alert {{ margin-top: 10px; font-size: 10px; font-weight: bold; text-align: center; border: 1px solid #000; padding: 5px; background: #f9f9f9; }}
            .no-print-btn {{ background-color: #2beb67; color: white; padding: 8px 16px; margin: 8px 0; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: bold; }}
        </style>
        <div class="invoice-header">
            <h2>📋 {copy_title}</h2>
            <h1>🏢 {SHOWROOM_NAME}</h1>
            <p>العنوان: {SHOWROOM_ADDRESS}</p>
            <p style="font-size: 13px; color: blue; font-weight: bold;">📞 رقم الاستعلام والدعم: {INQUIRY_NUMBER}</p>
        </div>
        <hr style="border: 1px solid #000; margin: 5px 0;">
        <table class="invoice-details-table">
            <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ:</b> {date}</td></tr>
            <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>الهاتف:</b> {phone if phone else 'غير محدد'}</td></tr>
            <tr><td><b>العنوان:</b> {address if address else 'غير محدد'}</td><td><b>المسؤول:</b> {user}</td></tr>
            <tr><td><b>نوع الدفع:</b> {pay_type}</td><td></td></tr>
            {collect_info}
        </table>
        <table class="invoice-items-table">
            <tr><th>الصنف والبيان</th><th>الكمية</th><th>سعر المفرد</th><th>الخصم</th><th>الصافي الإجمالي</th></tr>
            <tr><td>{item}</td><td>{qty}</td><td>{price}</td><td>{discount}%</td><td style="font-weight: bold;">{final_total}</td></tr>
        </table>
        <div class="invoice-footer-alert">⚠️ تنبيه هام جداً: مدة الاستبدال والارتجاع 15 يوماً لا غير من تاريخ الفاتورة بشرط سلامة البضاعة وغلافها.</div>
        <center><button class="no-print-btn" onclick="window.print()">🖨️ طباعة الفاتورة بمقاس A5</button></center>
    </div>
    """
    return html_content

def get_download_link(html_content, filename="invoice.html"):
    b64 = base64.b64encode(html_content.encode('utf-8-sig')).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="display: inline-block; padding: 10px 20px; color: white; background-color: #007bff; text-decoration: none; border-radius: 5px; font-weight: bold; text-align: center; margin: 10px 0;">📥 تحميل وتنزيل الفاتورة في ملف التحميلات فوراً</a>'

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
    
    allowed_actions = perms_df[perms_df[current_role] == True]["اسم الصفحة"].tolist()
    sidebar_pages = [p for p in allowed_actions if not p.startswith("✏️") and not p.startswith("❌")]
    
    if not sidebar_pages: sidebar_pages = ["🔍 حالة المخزن"]
        
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"الرتبة: **{st.session_state.role}**")
    
    choice = st.sidebar.selectbox("الانتقال إلى", sidebar_pages)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
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
                    new_p = pd.DataFrame([{"رقم الفاتورة": pur_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "المورد": vendor, "الصنف": item, "الكمية": str(qty), "إجمالي الشراء": str(total), "المسؤول": st.session_state.user}])
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
                
                cx1, cx2 = st.columns(2)
                with cx1:
                    with st.expander("✏️ تعديل اسم المورد للفاتورة"):
                        new_v_name = st.text_input("اسم المورد الجديد", value=p_row["المورد"])
                        if st.button("حفظ تعديل المورد"):
                            p_idx = purchases_df[purchases_df["رقم الفاتورة"] == target_pur_id].index[0]
                            purchases_df.at[p_idx, "المورد"] = new_v_name
                            purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                            st.success("تم التعديل بنجاح!")
                            st.rerun()
                with cx2:
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
            
            if st.button("🧾 إصدار وطباعة وحفظ الفاتورة الثلاثية (A5)", use_container_width=True):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                if int(inv_df.at[idx, 'الكمية']) < qty: st.error("❌ الكمية لا تكفي في المخزن!")
                elif not c_name: st.error("❌ يرجى تحديد أو كتابة اسم العميل أولاً.")
                else:
                    inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) - qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    new_s = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "اسم العميل": c_name, "هاتف العميل": c_phone, "العنوان": c_address, "نوع البيع": sale_type, "نظام التحصيل": collect_system, "تاريخ التحصيل": collect_date, "الصنف": selected_item, "الكمية": str(qty), "الخصم %": str(discount), "إجمالي البيع": str(final_total), "المسؤول": st.session_state.user}])
                    sales_df = pd.concat([sales_df, new_s], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    st.success("🎉 تم حفظ الفاتورة بنجاح في النظام!")
                    
                    main_invoice_html = generate_a5_html_invoice("نسخة العميل", inv_id, datetime.now().strftime("%Y-%m-%d"), c_name, c_phone, c_address, sale_type, collect_system, collect_date, st.session_state.user, selected_item, qty, item_row['سعر البيع'], discount, final_total)
                    st.markdown(get_download_link(main_invoice_html, f"فاتورة_{inv_id}.html"), unsafe_allow_html=True)
                    
                    copies = ["نسخة العميل", "نسخة الإدارة المالية", "نسخة مسؤول المخازن"]
                    for copy in copies:
                        invoice_html = generate_a5_html_invoice(copy, inv_id, datetime.now().strftime("%Y-%m-%d"), c_name, c_phone, c_address, sale_type, collect_system, collect_date, st.session_state.user, selected_item, qty, item_row['سعر البيع'], discount, final_total)
                        st.markdown(invoice_html, unsafe_allow_html=True)

    # --- 7. صفحة البحث عن فواتير البيعوطباعتها ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 نظام البحث والمراجعة والتحكم في الفواتير السابقة")
        if sales_df.empty: st.info("لا توجد فواتير مبيعات مسجلة في النظام حتى الآن.")
        else:
            search_query = st.text_input("ابحث عن فاتورة مبيعات (أدخل رقم الفاتورة، اسم العميل أو الهاتف)").strip()
            if search_query:
                filtered_sales = sales_df[sales_df['رقم الفاتورة'].str.contains(search_query, case=False, na=False) | sales_df['اسم العميل'].str.contains(search_query, case=False, na=False) | sales_df['هاتف العميل'].str.contains(search_query, case=False, na=False)]
            else: filtered_sales = sales_df
                
            st.dataframe(filtered_sales, use_container_width=True)
            
            if not filtered_sales.empty:
                st.subheader("⚙️ الإجراءات المتاحة للفاتورة المختارة:")
                selected_inv_id = st.selectbox("اختر رقم الفاتورة للمراجعة أو التعديل/الحذف", filtered_sales['رقم الفاتورة'].unique())
                f_row = sales_df[sales_df['رقم الفاتورة'] == selected_inv_id].iloc[0]
                
                col_actions1, col_actions2 = st.columns(2)
                
                if "✏️ تعديل الفواتير السابقة" in allowed_actions:
                    with col_actions1:
                        with st.expander("✏️ تعديل بيانات هذه الفاتورة"):
                            new_cust_name = st.text_input("تعديل اسم العميل", value=f_row['اسم العميل'])
                            new_cust_phone = st.text_input("تعديل هاتف العميل", value=f_row['هاتف العميل'] if 'هاتف العميل' in f_row else "")
                            new_cust_addr = st.text_input("تعديل عنوان العميل", value=f_row['العنوان'])
                            if st.button("💾 حفظ التعديلات الفورية للفاتورة"):
                                idx = sales_df[sales_df['رقم الفاتورة'] == selected_inv_id].index[0]
                                sales_df.at[idx, 'اسم العميل'] = new_cust_name
                                sales_df.at[idx, 'هاتف العميل'] = new_cust_phone
                                sales_df.at[idx, 'العنوان'] = new_cust_addr
                                sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                                st.success("🎉 تم تعديل الفاتورة بنجاح وثبات باقي البيانات!")
                                st.rerun()
                                
                if "❌ حذف الفواتير السابقة" in allowed_actions:
                    with col_actions2:
                        if st.button("❌ حذف هذه الفاتورة نهائياً وإرجاع بضاعتها للمخزن", use_container_width=True):
                            match_item = f_row['الصنف']
                            return_qty = int(f_row['الكمية'])
                            if match_item in inv_df['اسم الصنف'].values:
                                s_idx = inv_df[inv_df['اسم الصنف'] == match_item].index[0]
                                inv_df.at[s_idx, 'الكمية'] = int(inv_df.at[s_idx, 'الكمية']) + return_qty
                                inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                            
                            sales_df = sales_df[sales_df['رقم الفاتورة'] != selected_inv_id]
                            sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                            st.success("🔥 تم حذف الفاتورة وإرجاع الكمية للمخزن بنجاح!")
                            st.rerun()

                st.markdown("---")
                st.subheader(f"📄 معاينة وسحب رابط تحميل الفاتورة (A5)")
                match_inv_item = inv_df[inv_df['اسم الصنف'] == f_row['الصنف']]
                unit_price = match_inv_item.iloc[0]['سعر البيع'] if not match_inv_item.empty else 0.0
                
                p_phone = f_row['هاتف العميل'] if 'هاتف العميل' in f_row else ""
                p_sys = f_row['نظام التحصيل'] if 'نظام التحصيل' in f_row else "كاش"
                p_date = f_row['تاريخ التحصيل'] if 'تاريخ التحصيل' in f_row else "فوراً"

                main_html = generate_a5_html_invoice("نسخة العميل", f_row['رقم الفاتورة'], f_row['التاريخ'], f_row['اسم العميل'], p_phone, f_row['العنوان'], f_row['نوع البيع'], p_sys, p_date, f_row['المسؤول'], f_row['الصنف'], int(f_row['الكمية']), unit_price, float(f_row['الخصم %']), float(f_row['إجمالي البيع']))
                st.markdown(get_download_link(main_html, f"تحميل_فاتورة_{selected_inv_id}.html"), unsafe_allow_html=True)

                copies = ["نسخة العميل", "نسخة الإدارة المالية", "نسخة مسؤول المخازن"]
                for copy in copies:
                    invoice_html = generate_a5_html_invoice(copy, f_row['رقم الفاتورة'], f_row['التاريخ'], f_row['اسم العميل'], p_phone, f_row['العنوان'], f_row['نوع البيع'], p_sys, p_date, f_row['المسؤول'], f_row['الصنف'], int(f_row['الكمية']), unit_price, float(f_row['الخصم %']), float(f_row['إجمالي البيع']))
                    st.markdown(invoice_html, unsafe_allow_html=True)

    # --- 8. صفحة التقارير ---
    elif "تقارير البيع والشراء" in choice:
        st.header(f"📈 التقارير المالية التفصيلية لـ {SHOWROOM_NAME}")
        t1, t2 = st.tabs(["📑 حركة الفواتير", "💰 الخزينة والأرباح"])
        with t1:
            st.subheader("🛒 سجل المبيعات")
            st.dataframe(sales_df, use_container_width=True)
            st.subheader("📦 سجل المشتريات")
            st.dataframe(purchases_df, use_container_width=True)
        with t2:
            s_sum = pd.to_numeric(sales_df['إجمالي البيع'], errors='coerce').sum()
            e_sum = pd.to_numeric(exp_df['المبلغ'], errors='coerce').sum()
            total_cost_of_goods_sold = 0.0
            for _, row in sales_df.dropna(subset=['الصنف', 'الكمية']).iterrows():
                match_inv = inv_df[inv_df['اسم الصنف'] == row['الصنف']]
                if not match_inv.empty: total_cost_of_goods_sold += float(match_inv.iloc[0]['سعر الشراء']) * int(row['الكمية'])
            net_profit = s_sum - (total_cost_of_goods_sold + e_sum)
            
            c_m1, c_m2, c_m3 = st.columns(3)
            c_m1.metric("إجمالي المبيعات", f"{s_sum:,.2f} جنيه")
            c_m2.metric("إجمالي المصاريف", f"{e_sum:,.2f} جنيه")
            c_m3.metric("صافي الأرباح الحقيقية", f"{net_profit:,.2f} جنيه")

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
                st.success("✅ تم الحفظ!")
                st.rerun()

    # --- 10. الحضور والانصراف ---
    elif "الحضور والانصراف" in choice:
        st.header("⏰ تسجيل حضور وانصراف موظفي المعرض")
        st.dataframe(att_df, use_container_width=True)
        today = datetime.now().strftime("%Y-%m-%d")
        now_t = datetime.now().strftime("%H:%M:%S")
        c1, c2 = st.columns(2)
        if c1.button("🟢 تسجيل حضور اليوم", use_container_width=True):
            if not att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today)].empty: st.warning("⚠️ تم تسجيل حضورك مسبقاً!")
            else:
                new_a = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": today, "وقت الحضور": now_t, "وقت الانصراف": "لم ينصرف"}])
                att_df = pd.concat([att_df, new_a], ignore_index=True)
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"📌 تم تسجيل الحضور في: {now_t}")
                st.rerun()
        if c2.button("🔴 تسجيل انصراف الآن", use_container_width=True):
            idx = att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today) & (att_df['وقت الانصراف'] == "لم ينصرف")].index
            if not idx.empty:
                att_df.at[idx[0], 'وقت الانصراف'] = now_t
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"📌 تم تسجيل انصرافك!")
                st.rerun()

    # --- 11. صفحة إدارة وتعديل الصلاحيات ---
    elif "إدارة وتعديل الصلاحيات" in choice:
        st.header("⚙️ إدارة الصلاحيات وحسابات الموظفين والمشرفين")
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        tab_add, tab_edit, tab_visibility = st.tabs(["➕ إنشاء حساب جديد", "✏️ تعديل وحذف حساب", "⚙️ التحكم في إظهار وإخفاء الصفحات والعمليات"])
        
        with tab_add:
            st.subheader("👤 إضافة مستخدم جديد للنظام")
            c1, c2, c3 = st.columns(3)
            nu = c1.text_input("اسم المستخدم الجديد", key="new_un")
            np = c2.text_input("كلمة المرور الجديدة", type="password", key="new_pw")
            nr = c3.selectbox("الصلاحية الممنوحة له", ["موظف", "مشرف", "مدير"], key="new_rl")
            if st.button("اعتماد وإنشاء الحساب", use_container_width=True):
                if nu and np:
                    if nu in u_df["username"].values: st.error("❌ اسم المستخدم هذا مسجل بالفعل!")
                    else:
                        new_u = pd.DataFrame([{"username": nu, "password": np, "role": nr}])
                        u_df = pd.concat([u_df, new_u], ignore_index=True)
                        u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                        st.success(f"🎉 تم إنشاء الحساب!")
                        st.rerun()
                else: st.error("يرجى إدخال البيانات كاملة.")
                    
        with tab_edit:
            target_user = st.selectbox("اختر الحساب الذي تريد تعديله أو حذفه", u_df["username"].unique())
            user_data = u_df[u_df["username"] == target_user].iloc[0]
            c1, c2, c3 = st.columns(3)
            edit_username = c1.text_input("تعديل اسم المستخدم", value=user_data["username"])
            edit_password = c2.text_input("تعديل كلمة المرور", value=user_data["password"])
            edit_role = c3.selectbox("تعديل الصلاحية", ["موظف", "مشرف", "مدير"], index=["موظف", "مشرف", "مدير"].index(user_data["role"]))
            
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("💾 حفظ التعديلات الجديدة"):
                idx = u_df[u_df["username"] == target_user].index[0]
                u_df.at[idx, "username"] = edit_username
                u_df.at[idx, "password"] = edit_password
                u_df.at[idx, "role"] = edit_role
                u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                st.success("🎉 تم التحديث!")
                st.rerun()
            if col_btn2.button("❌ حذف هذا الحساب نهائياً"):
                if target_user == "admin": st.error("❌ لا يمكن حذف المسؤول الحساب الرئيسي!")
                else:
                    u_df = u_df[u_df["username"] != target_user]
                    u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                    st.success("🔥 تم الحذف!")
                    st.rerun()

        with tab_visibility:
            updated_rows = []
            for idx, row in perms_df.iterrows():
                st.markdown(f"**⚙️ {row['اسم الصفحة']}**")
                col1, col2, col3 = st.columns(3)
                m_perm = col1.checkbox("تفعيل للمدير", value=bool(row['مدير']), key=f"p_dir_{idx}", disabled=True)
                s_perm = col2.checkbox("تفعيل للمشرف", value=bool(row['مشرف']), key=f"p_sh_{idx}")
                u_perm = col3.checkbox("تفعيل للموظف", value=bool(row['موظف']), key=f"p_us_{idx}")
                updated_rows.append({"اسم الصفحة": row['اسم الصفحة'], "مدير": m_perm, "مشرف": s_perm, "موظف": u_perm})
                st.markdown("---")
            if st.button("💾 حفظ خريطة الصلاحيات وتحديث النظام"):
                pd.DataFrame(updated_rows).to_csv(PERMISSIONS_FILE, index=False, encoding='utf-8-sig')
                st.success("🚀 تم التحديث بنجاح!")
                st.rerun()

    # --- 12. صفحة إعدادات بيانات الفاتورة والدعم ---
    elif "إعدادات بيانات الفاتورة والدعم" in choice:
        st.header("⚙️ تحديث وإعداد بيانات طباعة الفاتورة والدعم للشركة")
        st.info("البيانات المدخلة هنا ستظهر تلقائياً في ترويسة جميع فواتير المبيعات الصادرة مستقبلاً.")
        
        with st.form("settings_form"):
            new_showroom_name = st.text_input("اسم المعرض / الشركة المطبوع بالفاتورة", value=SHOWROOM_NAME)
            new_showroom_address = st.text_input("العنوان بالتفصيل المطبوع بالفاتورة", value=SHOWROOM_ADDRESS)
            new_inquiry_number = st.text_input("رقم استعلام الدعم الفني الثابت للفواتير", value=INQUIRY_NUMBER)
            
            save_settings = st.form_submit_button("💾 حفظ وتحديث بيانات الفاتورة الفورية")
            
            if save_settings:
                if new_showroom_name and new_inquiry_number:
                    updated_settings = pd.DataFrame([{"اسم المعرض": new_showroom_name, "العنوان": new_showroom_address, "رقم الدعم": new_inquiry_number}])
                    updated_settings.to_csv(SETTINGS_FILE, index=False, encoding='utf-8-sig')
                    st.success("🚀 تم تحديث بيانات الشركة والفاتورة بنجاح وثبات كامل في النظام!")
                    st.rerun()
                else: st.error("❌ يرجى ملء الحقول الأساسية لضمان عمل الفاتورة بنجاح.")
