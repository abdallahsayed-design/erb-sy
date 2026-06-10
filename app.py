import streamlit as st
import pandas as pd
import os
from datetime import datetime

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
RATINGS_FILE = "ratings_data.csv"  # ملف التقييمات الجديد

# دالة تهيئة الملفات للتأكد من وجود الأعمدة الجديدة والحسابات الافتراضية
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([
            {"username": "superadmin", "password": "789", "role": "مدير عام"},
            {"username": "admin", "password": "123", "role": "مدير"},
            {"username": "sharaf", "password": "456", "role": "مشرف"},
            {"username": "user1", "password": "111", "role": "موظف"}
        ]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
        
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "هاتف العميل", "العنوان", "نوع البيع", "الصنف", "الكمية", "الخصم %", "إجمالي البيع", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(PURCHASES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "المورد", "هاتف المورد", "الصنف", "الكمية", "إجمالي الشراء", "المسؤول"]).to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(EXPENSES_FILE):
        pd.DataFrame(columns=["التاريخ", "البيان", "المبلغ", "المسؤول"]).to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(ATTENDANCE_FILE):
        pd.DataFrame(columns=["الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف"]).to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(CONTACTS_FILE):
        pd.DataFrame(columns=["النوع", "الاسم", "الهاتف", "العنوان"]).to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(RATINGS_FILE):
        pd.DataFrame(columns=["التاريخ", "المسؤول المراد تقييمه", "التقييم بالنجوم", "ملاحظات المدير العام"]).to_csv(RATINGS_FILE, index=False, encoding='utf-8-sig')

init_files()

# إدارة الجلسة والمستخدمين
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "موظف"

# دالة برمجية مبسطة لتحويل الأرقام إلى مبالغ مكتوبة باللغة العربية (تفقيط)
def number_to_arabic_words(amount):
    try:
        val = int(float(amount))
        if val == 0: return "صفر جنيهاً"
        
        ones = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة"]
        teens = ["عشر", "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
        tens = ["", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
        hundreds = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]
        thousands = ["", "ألف", "ألفان", "ثلاثة آلاف", "أربعة آلاف", "خمسة آلاف", "ستة آلاف", "سبعة آلاف", "ثمانية آلاف", "تسعة آلاف"]
        
        words = []
        
        # آلاف
        th = val // 1000
        if th > 0 and th <= 9: words.append(thousands[th])
        val %= 1000
        
        # مئات
        h = val // 100
        if h > 0: words.append(hundreds[h])
        val %= 100
        
        # آحاد وعشرات
        if val > 0:
            if val <= 10:
                words.append(ones[val])
            elif val < 20:
                words.append(teens[val-10])
            else:
                o = val % 10
                t = val // 10
                if o > 0:
                    words.append(f"{ones[o]} و {tens[t]}")
                else:
                    words.append(tens[t])
                    
        result = " و ".join([w for w in words if w != ""])
        return f"فقط {result} جنيهاً مصرياً لا غير"
    except:
        return "إجمالي السعر الموضح أعلاه"

# دالة لتوليد كود طباعة الفواتير بنمط A5 المحسن مع الحفظ التلقائي كـ PDF
def generate_a5_invoice(inv_id, date, c_name, c_phone, c_address, sale_type, selected_item, qty, item_price, discount, final_total, user):
    copies = ["نسخة العميل", "نسخة الإدارة المالية", "نسخة مسؤول المخازن"]
    html_invoice = ""
    arabic_text_amount = number_to_arabic_words(final_total)
    
    for copy in copies:
        is_warehouse = (copy == "نسخة مسؤول المخازن")
        
        # إعدادات العرض لنسخة المخزن (إخفاء المبالغ)
        phone_section = ""
        if not is_warehouse:
            phone_section = """<div style="margin-top: 5px; font-size: 13px; font-weight: bold; text-align: center; color: #111;">📞 هاتف استعلام المعرض: 0128958413</div>"""
            
        html_invoice += f"""
        <div style="width: 148mm; min-height: 210mm; border: 2px solid #000; padding: 15px; margin: 0 auto 40px auto; direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background: #fff; color: #000; box-sizing: border-box; page-break-after: always; position: relative;">
            <div style="text-align: center;">
                <span style="border: 1px solid #000; padding: 3px 10px; font-weight: bold; font-size: 14px;">{copy}</span>
                <h1 style="margin: 5px 0 2px 0; font-size: 24px;">🏢 معرض الكبير</h1>
                <p style="font-size: 11px; margin: 0;">أبو حماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي</p>
            </div>
            <hr style="border: 1px solid #000; margin: 8px 0;">
            <table style="width: 100%; font-size: 13px; line-height: 1.6;">
                <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ:</b> {date}</td></tr>
                <tr><td><b>اسم العميل:</b> {c_name}</td><td><b>هاتف العميل:</b> {c_phone if c_phone else 'غير مسجل'}</td></tr>
                <tr><td><b>العنوان:</b> {c_address if c_address else 'غير محدد'}</td><td><b>طبيعة الدفع:</b> {sale_type}</td></tr>
                <tr><td colspan="2"><b>المسؤول الصادر:</b> {user}</td></tr>
            </table>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; border: 1px solid black; font-size: 13px; text-align: center;">
                <tr style="background: #eee;">
                    <th style="border: 1px solid black; padding: 6px;">الصنف والبيان</th>
                    <th style="border: 1px solid black; padding: 6px;">الكمية المطلوبة</th>
                    {" " if is_warehouse else f'<th style="border: 1px solid black; padding: 6px;">سعر المفرد</th>'}
                    {" " if is_warehouse else f'<th style="border: 1px solid black; padding: 6px;">الخصم</th>'}
                    {" " if is_warehouse else f'<th style="border: 1px solid black; padding: 6px;">الصافي الإجمالي</th>'}
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 6px; font-weight: bold;">{selected_item}</td>
                    <td style="border: 1px solid black; padding: 6px; font-size: 16px; font-weight: bold;">{qty} قطعة</td>
                    {" " if is_warehouse else f'<td style="border: 1px solid black; padding: 6px;">{item_price}</td>'}
                    {" " if is_warehouse else f'<td style="border: 1px solid black; padding: 6px;">{discount}%</td>'}
                    {" " if is_warehouse else f'<td style="border: 1px solid black; padding: 6px; font-weight: bold; font-size:15px;">{final_total}</td>'}
                </tr>
            </table>
            
            {" " if is_warehouse else f'<div style="margin-top: 10px; font-size: 13px; font-weight: bold; background: #f9f9f9; padding: 5px; border-right: 4px solid #000;">✍️ المبلغ الإجمالي كتابةً: <span style="color:#c00;">{arabic_text_amount}</span></div>'}
            
            <div style="margin-top: 25px; font-size: 11px; font-weight: bold; text-align: center; border: 1px dashed #000; padding: 8px; background: #fafafa;">
                ⚠️ تنبيه: مدة الاستبدال والارجاع 15 يوم لاغير من تاريخ الفاتورة بشرط سلامة البضاعة تماماً.
            </div>
            {phone_section}
        </div>
        """
        
    # إضافة سكريبت جافا سكريبت يقوم بتحويل الشاشة بالكامل للطباعة وحفظها كـ PDF تلقائياً فوراً
    html_invoice += """
    <script>
        setTimeout(function(){
            window.print();
        }, 500);
    </script>
    """
    return html_invoice

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    st.title("🔐 نظام معرض الكبير - تسجيل الدخول")
    user_input = st.text_input("اسم المستخدم").strip()
    pw_input = st.text_input("كلمة المرور", type="password").strip()
    
    if st.button("دخول للنظام", use_container_width=True):
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        match = u_df[(u_df['username'] == user_input) & (u_df['password'] == pw_input)]
        if not match.empty:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.session_state.role = match.iloc[0]['role']
            st.success(f"مرحباً بك يا {user_input} ({st.session_state.role})")
            st.rerun()
        else:
            st.error("بيانات الدخول خاطئة.")
else:
    # --- بناء القائمة الجانبية والصلاحيات حسب الرتبة الجديدة ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"الرتبة: **{st.session_state.role}**")
    
    if st.session_state.role == "مدير عام":
        menu = ["🗂️ تكويد الأصناف", "📈 رصيد أول المدة Excel", "📦 حالة المخزن", "🤝 العملاء والموردين", "🛍️ فاتورة شراء جديدة", "💰 فاتورة بيع جديدة", "🔍 بحث وإعادة طباعة الفواتير", "📊 تقارير البيع والشراء والأرباح والتقييم", "💸 المصاريف", "⏱️ الحضور والانصراف للعاملين", "👥 إدارة الصلاحيات وتعديل الحسابات"]
    elif st.session_state.role == "مدير":
        menu = ["🗂️ تكويد الأصناف", "📈 رصيد أول المدة Excel", "📦 حالة المخزن", "🤝 العملاء والموردين", "🛍️ فاتورة شراء جديدة", "💰 فاتورة بيع جديدة", "🔍 بحث وإعادة طباعة الفواتير", "📊 تقارير البيع والشراء والأرباح والتقييم", "💸 المصاريف", "⏱️ الحضور والانصراف للعاملين"]
    elif st.session_state.role == "مشرف":
        menu = ["📦 حالة المخزن", "🛍️ فاتورة شراء جديدة", "💰 فاتورة بيع جديدة", "🔍 بحث وإعادة طباعة الفواتير", "⏱️ الحضور والانصراف للعاملين", "⚙️ إعدادات حسابي"]
    else: # موظف عادي
        menu = ["📦 حالة المخزن", "💰 فاتورة بيع جديدة", "🔍 بحث وإعادة طباعة الفواتير", "⏱️ الحضور والانصراف للعاملين", "⚙️ إعدادات حسابي"]
        
    choice = st.sidebar.selectbox("الانتقال إلى", menu)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # قراءة البيانات بشكل فوري ومحدث
    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
    sales_df = pd.read_csv(SALES_FILE, dtype={"هاتف العميل": str, "رقم الفاتورة": str})
    purchases_df = pd.read_csv(PURCHASES_FILE, dtype={"هاتف المورد": str, "رقم الفاتورة": str})
    exp_df = pd.read_csv(EXPENSES_FILE)
    att_df = pd.read_csv(ATTENDANCE_FILE)
    contacts_df = pd.read_csv(CONTACTS_FILE, dtype=str)
    ratings_df = pd.read_csv(RATINGS_FILE, dtype=str)

    # --- 1. صفحة تكويد الأصناف ---
    if choice == "🗂️ تكويد الأصناف":
        st.header("🗂️ تكويد وتسجيل أصناف جديدة")
        st.dataframe(inv_df, use_container_width=True)
        st.subheader("➕ إضافة صنف جديد")
        c1, c2, c3, c4 = st.columns(4)
        iid = c1.text_input("كود الصنف (الباركود / ID)")
        iname = c2.text_input("اسم المنتج")
        ipurchase = c3.number_input("سعر الشراء الافتراضي", min_value=0.0)
        isale = c4.number_input("سعر البيع الافتراضي", min_value=0.0)
        
        if st.button("تكويد وحفظ"):
            if iid and iname:
                if iid in inv_df["كود الصنف"].values: st.warning("⚠️ هذا الكود مسجل مسبقاً!")
                else:
                    new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "الكمية": 0, "سعر الشراء": ipurchase, "سعر البيع": isale}])
                    inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم التكويد بنجاح!")
                    st.rerun()

    # --- 2. صفحة رصيد أول المدة ---
    elif choice == "📈 رصيد أول المدة Excel":
        st.header("📈 رفع بضائع ورصيد أول المدة عبر ملف Excel")
        uploaded_file = st.file_uploader("اختر شيت الاكسل الخاص بالبضائع", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                excel_df = pd.read_excel(uploaded_file, dtype={"كود الصنف": str})
                st.dataframe(excel_df)
                if st.button("تأكيد ودمج الملف في رصيد أول المدة"):
                    combined_df = pd.concat([inv_df, excel_df]).drop_duplicates(subset=['كود الصنف'], keep='last')
                    combined_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم رفع وتحديث المخزن بنجاح!")
                    st.rerun()
            except Exception as e: st.error(f"❌ خطأ بالملف: {e}")

    # --- 3. صفحة حالة المخزن ---
    elif choice == "📦 حالة المخزن":
        st.header("📦 جرد بضائع المخزن الحالية")
        st.dataframe(inv_df, use_container_width=True)

    # --- 4. صفحة العملاء والموردين ---
    elif choice == "🤝 العملاء والموردين":
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
                st.success("تم الحفظ!")
                st.rerun()

    # --- 5. صفحة المشتريات ---
    elif choice == "🛍️ فاتورة شراء جديدة":
        st.header("🛍️ تسجيل فاتورة مشتريات جديدة للوارد")
        if inv_df.empty: st.warning("قم بتكويد بضائع أولاً.")
        else:
            m_list = contacts_df[contacts_df['النوع'] == 'مورد']['الاسم'].unique()
            c1, c2, c3, c4 = st.columns(4)
            vendor_type = c1.radio("نوع المورد", ["مورد جديد / نقدي سريع", "مسجل مسبقاً"])
            if vendor_type == "مسجل مسبقاً" and len(m_list) > 0:
                vendor = c2.selectbox("اختر المورد", m_list)
                v_phone = contacts_df[contacts_df['الاسم'] == vendor]['الهاتف'].values[0]
            else:
                vendor = c2.text_input("اسم الشركة / المورد")
                v_phone = c3.text_input("رقم هاتف المورد")
