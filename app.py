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

# دالة تهيئة الملفات للتأكد من وجود الأعمدة الجديدة والحسابات الافتراضية
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([
            {"username": "admin", "password": "123", "role": "مدير"},
            {"username": "sharaf", "password": "456", "role": "مشرف"},
            {"username": "user1", "password": "111", "role": "موظف"}
        ]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    
    # تحديث وتضمين رقم هاتف العميل والمورد في الجداول
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

init_files()

# إدارة الجلسة والمستخدمين
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "موظف"

# دالة لتوليد كود طباعة الفواتير بنمط A5
def generate_a5_invoice(inv_id, date, c_name, c_phone, c_address, sale_type, selected_item, qty, item_price, discount, final_total, user):
    copies = ["نسخة العميل", "نسخة الإدارة المالية", "نسخة مسؤول المخازن"]
    html_invoice = ""
    for copy in copies:
        # شروط إظهار هاتف الاستعلام الخاص بالمعرض في نسختي العميل والمالية فقط
        phone_section = ""
        if copy in ["نسخة العميل", "نسخة الإدارة المالية"]:
            phone_section = """
            <div style="margin-top: 5px; font-size: 13px; font-weight: bold; text-align: center; color: #111;">
                📞 هاتف استعلام المعرض: 0128958413
            </div>
            """
        
        html_invoice += f"""
        <div style="width: 148mm; min-height: 210mm; border: 2px solid #000; padding: 15px; margin: 0 auto 40px auto; direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background: #fff; color: #000; box-sizing: border-box; page-break-after: always;">
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
                <tr><td colspan="2"><b>المسؤول:</b> {user}</td></tr>
            </table>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; border: 1px solid black; font-size: 13px; text-align: center;">
                <tr style="background: #eee;">
                    <th style="border: 1px solid black; padding: 6px;">الصنف والبيان</th>
                    <th style="border: 1px solid black; padding: 6px;">الكمية</th>
                    <th style="border: 1px solid black; padding: 6px;">سعر المفرد</th>
                    <th style="border: 1px solid black; padding: 6px;">الخصم</th>
                    <th style="border: 1px solid black; padding: 6px;">الصافي المطلوب</th>
                </tr>
                <tr>
                    <td style="border: 1px solid black; padding: 6px;">{selected_item}</td>
                    <td style="border: 1px solid black; padding: 6px;">{qty}</td>
                    <td style="border: 1px solid black; padding: 6px;">{item_price}</td>
                    <td style="border: 1px solid black; padding: 6px;">{discount}%</td>
                    <td style="border: 1px solid black; padding: 6px; font-weight: bold;">{final_total}</td>
                </tr>
            </table>
            <div style="margin-top: 25px; font-size: 11px; font-weight: bold; text-align: center; border: 1px dashed #000; padding: 8px; background: #fafafa;">
                ⚠️ شروط الإرجاع: مدة الاستبدال والارجاع 15 يوم لاغير من تاريخ الفاتورة بشرط سلامة البضاعة.
            </div>
            {phone_section}
        </div>
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
    # --- بناء القائمة الجانبية والصلاحيات حسب الرتبة ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"الرتبة: **{st.session_state.role}**")
    
    if st.session_state.role == "مدير":
        menu = ["🗂️ تكويد الأصناف", "📈 رصيد أول المدة Excel", "📦 حالة المخزن", "🤝 العملاء والموردين", "🛍️ فاتورة شراء جديدة", "💰 فاتورة بيع جديدة", "🔍 بحث وإعادة طباعة الفواتير", "📊 تقارير البيع والشراء", "💸 المصاريف", "⏱️ الحضور والانصراف", "👥 إدارة الصلاحيات وتعديل الحسابات"]
    elif st.session_state.role == "مشرف":
        menu = ["📦 حالة المخزن", "🛍️ فاتورة شراء جديدة", "💰 فاتورة بيع جديدة", "🔍 بحث وإعادة طباعة الفواتير", "⏱️ الحضور والانصراف", "⚙️ إعدادات حسابي"]
    else: # موظف عادي
        menu = ["📦 حالة المخزن", "💰 فاتورة بيع جديدة", "🔍 بحث وإعادة طباعة الفواتير", "⏱️ الحضور والانصراف", "⚙️ إعدادات حسابي"]
        
    choice = st.sidebar.selectbox("الانتقال إلى", menu)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # قراءة البيانات بشكل فوري ومحدث من ملفات الـ CSV مع معالجة الأنواع النصية للهواتف
    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
    sales_df = pd.read_csv(SALES_FILE, dtype={"هاتف العميل": str, "رقم الفاتورة": str})
    purchases_df = pd.read_csv(PURCHASES_FILE, dtype={"هاتف المورد": str, "رقم الفاتورة": str})
    exp_df = pd.read_csv(EXPENSES_FILE)
    att_df = pd.read_csv(ATTENDANCE_FILE)
    contacts_df = pd.read_csv(CONTACTS_FILE, dtype=str)

    # --- 1. صفحة تكويد الأصناف (لمدير فقط) ---
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
                if iid in inv_df["كود الصنف"].values:
                    st.warning("⚠️ هذا الكود مسجل مسبقاً!")
                else:
                    new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "الكمية": 0, "سعر الشراء": ipurchase, "سعر البيع": isale}])
                    inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم تكويد المنتج بنجاح!")
                    st.rerun()

    # --- 2. صفحة رفع رصيد أول المدة عبر شيت Excel (للمدير فقط) ---
    elif choice == "📈 رصيد أول المدة Excel":
        st.header("📈 رفع بضائع ورصيد أول المدة عبر ملف Excel")
        st.write("ارفع ملف Excel يحتوي على الأعمدة التالية تماماً: `كود الصنف`, `اسم الصنف`, `الكمية`, `سعر الشراء`, `سعر البيع`")
        
        uploaded_file = st.file_uploader("اختر شيت الاكسل الخاص بالبضائع", type=["xlsx", "xls"])
        if uploaded_file is not None:
            try:
                excel_df = pd.read_excel(uploaded_file, dtype={"كود الصنف": str})
                st.subheader("👀 معاينة البيانات المرفوعة من الشيت:")
                st.dataframe(excel_df)
                
                if st.button("تأكيد ودمج الملف في رصيد أول المدة"):
                    combined_df = pd.concat([inv_df, excel_df]).drop_duplicates(subset=['كود الصنف'], keep='last')
                    combined_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم رفع وحفظ رصيد أول المدة بنجاح وتحديث المخزن!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء قراءة الملف، يرجى التأكد من أسماء الأعمدة. الخطأ: {e}")

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

    # --- 5. صفحة المشتريات (مع إضافة هاتف المورد) ---
    elif choice == "🛍️ فاتورة شراء جديدة":
        st.header("🛍️ تسجيل فاتورة مشتريات جديدة للوارد")
        if inv_df.empty: st.warning("قم بتكويد بضائع أو رفع رصيد أول مدة أولاً.")
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
                
            item = c4.selectbox("الصنف المشترى", inv_df['اسم الصنف'].unique())
            qty = st.number_input("الكمية الواردة", min_value=1, step=1)
            
            item_row = inv_df[inv_df['اسم الصنف'] == item].iloc[0]
            total = item_row['سعر الشراء'] * qty
            
            if st.button("حفظ فاتورة المشتريات وتحديث المخزن"):
                if not vendor:
                    st.error("يرجى إدخال اسم المورد.")
                else:
                    idx = inv_df[inv_df['اسم الصنف'] == item].index[0]
                    inv_df.at[idx, 'الكمية'] += qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    pur_id = "PUR-" + str(int(datetime.now().timestamp()))
                    new_p = pd.DataFrame([{"رقم الفاتورة": pur_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "المورد": vendor, "هاتف المورد": v_phone, "الصنف": item, "الكمية": qty, "إجمالي الشراء": total, "المسؤول": st.session_state.user}])
                    purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                    purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم تسجيل الوارد وإضافة الفاتورة بنجاح!")

    # --- 6. صفحة فاتورة بيع جديدة (مع إضافة هاتف العميل وتصميم الـ A5) ---
    elif choice == "💰 فاتورة بيع جديدة":
        st.header("💰 إنشاء فاتورة مبيعات جديدة - معرض الكبير")
        if inv_df.empty: st.warning("المخزن فارغ تماماً.")
        else:
            c_list = contacts_df[contacts_df['النوع'] == 'عميل']['الاسم'].unique()
            
            c1, c2, c3, c4 = st.columns(4)
            cust_type = c1.radio("نوع العميل", ["سريع / غير مسجل", "مسجل مسبقاً"])
            if cust_type == "مسجل مسبقاً" and len(c_list) > 0:
                c_name = c2.selectbox("اختر العميل", c_list)
                c_phone = contacts_df[contacts_df['الاسم'] == c_name]['الهاتف'].values[0]
                c_address = contacts_df[contacts_df['الاسم'] == c_name]['العنوان'].values[0]
            else:
                c_name = c2.text_input("اسم العميل")
                c_phone = c3.text_input("رقم هاتف العميل")
                c_address = c4.text_input("عنوان العميل")
                
            sale_type = st.selectbox("طبيعة البيع الدفع", ["نقدي (كاش)", "آجل (على الحساب)"])
            
            st.markdown("---")
            c5, c6, c7 = st.columns(3)
            selected_item = c5.selectbox("اختر المنتج للبيع", inv_df['اسم الصنف'].unique())
            qty = c6.number_input("الكمية المطلوبة", min_value=1, step=1)
            
            discount = 0.0
            if st.session_state.role in ["مدير", "مشرف"]:
                discount = c7.number_input("نسبة الخصم الممنوحة للمشرفين والمدراء (%)", min_value=0.0, max_value=100.0, step=0.5)
            else:
                c7.write("🔒 *صلاحية الخصم مغلقة للموظفين العاديين*")
                
            item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
            subtotal = item_row['سعر البيع'] * qty
            discount_amount = subtotal * (discount / 100)
            final_total = subtotal - discount_amount
            
            st.warning(f"📊 حالة الصنف: المتوفر بالمخزن {item_row['الكمية']} قطع | السعر الأساسي: {subtotal} | قيمة الخصم: {discount_amount} | الإجمالي الصافي: {final_total}")
            
            if st.button("إصدار وطباعة الفاتورة الثلاثية (حجم A5)", use_container_width=True):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                if inv_df.at[idx, 'الكمية'] < qty:
                    st.error("❌ الكمية المتوفرة في المخزن لا تكفي للبيع!")
                elif not c_name:
                    st.error("❌ يرجى كتابة أو تحديد اسم العميل أولاً.")
                else:
                    inv_df.at[idx, 'الكمية'] -= qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    
                    new_s = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": today_str, "اسم العميل": c_name, "هاتف العميل": c_phone, "العنوان": c_address, "نوع البيع": sale_type, "الصنف": selected_item, "الكمية": qty, "الخصم %": discount, "إجمالي البيع": final_total, "المسؤول": st.session_state.user}])
                    sales_df = pd.concat([sales_df, new_s], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success("✅ تم حفظ الفاتورة بنجاح في السجلات وجاهزة للطباعة!")
                    
                    # استدعاء دالة الطباعة وتصميم الـ A5
                    invoice_html = generate_a5_invoice(inv_id, today_str, c_name, c_phone, c_address, sale_type, selected_item, qty, item_row['سعر البيع'], discount, final_total, st.session_state.user)
                    st.markdown(invoice_html, unsafe_allow_html=True)
                    st.info("💡 اضغط كليك يمين بالماوس ثم اختر Print (أو اختصار Ctrl + P) لطباعة الفواتير ورقياً وحفظها.")

    # --- 7. 🔍 صفحة البحث وإعادة طباعة الفواتير السابقة بأي وقت ---
    elif choice == "🔍 بحث وإعادة طباعة الفواتير":
        st.header("🔍 محرك البحث عن الفواتير القديمة وإعادة طباعتها بحجم A5")
        search_query = st.text_input("ابحث عن الفاتورة بـ (اسم العميل أو رقم الفاتورة الكامل)").strip()
        
        if search_query:
            filtered_sales = sales_df[(sales_df['اسم العميل'].str.contains(search_query, na=False, case=False)) | (sales_df['رقم الفاتورة'].str.contains(search_query, na=False))]
            if filtered_sales.empty:
                st.warning("لم يتم العثور على أي نتائج مطابقة للبحث.")
            else:
                st.write(f"📂 تم العثور على ({len(filtered_sales)}) فاتورة:")
                for index, row in filtered_sales.iterrows():
                    with st.expander(f"📄 فاتورة رقم {row['رقم الفاتورة']} - العميل: {row['اسم العميل']} ({row['التاريخ']})"):
                        st.write(row.to_dict())
                        if st.button(f"🖨️ عرض الفاتورة الثلاثية لإعادة الطباعة لـ {row['رقم الفاتورة']}", key=f"print_{row['رقم الفاتورة']}"):
                            # جلب السعر الافتراضي الأصلي من المخزن إن وُجد لحساب السعر الفردي
                            original_price = row['إجمالي البيع'] / row['الكمية'] if row['الكمية'] > 0 else 0
                            
                            inv_html = generate_a5_invoice(
                                row['رقم الفاتورة'], row['التاريخ'], row['اسم العميل'], 
                                row.get('هاتف العميل', 'غير مسجل'), row.get('العنوان', 'غير محدد'), 
                                row['نوع البيع'], row['الصنف'], row['الكمية'], 
                                round(original_price, 2), row['الخصم %'], row['إجمالي البيع'], row['المسؤول']
                            )
                            st.markdown(inv_html, unsafe_allow_html=True)

    # --- 8. صفحة التقارير المالية ---
    elif choice == "📊 تقارير البيع والشراء":
        st.header("📊 التقارير المالية التفصيلية لمعرض الكبير")
        t1, t2 = st.tabs(["📊 حركة الفواتير السجل", "📈 الخزينة والأرباح"])
        with t1:
            st.subheader("المبيعات الصادرة")
            st.dataframe(sales_df)
            st.subheader("المشتريات والوارد")
            st.dataframe(purchases_df)
        with t2:
            s_sum = sales_df['إجمالي البيع'].astype(float).sum()
            p_sum = purchases_df['إجمالي الشراء'].astype(float).sum()
            e_sum = exp_df['المبلغ'].astype(float).sum()
            st.metric("صافي السيولة النقدية والربح الفعلي الحالي بالخزنة", f"{s_sum - (p_sum + e_sum)} جنيه")

    # --- 9. صفحة المصاريف ---
    elif choice == "💸 المصاريف":
        st.header("💸 تسجيل المصاريف الإدارية واليومية")
        st.dataframe(exp_df)
        b1 = st.text_input("بيان سبب الصرف")
        b2 = st.number_input("المبلغ المنصرف", min_value=0.0)
        if st.button("حفظ بند المصروف"):
            if b1 and b2 > 0:
                new_e = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d"), "البيان": b1, "المبلغ": b2, "المسؤول": st.session_state.user}])
                exp_df = pd.concat([exp_df, new_e], ignore_index=True)
                exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                st.success("تم الحفظ والمزامنة!")
                st.rerun()

    # --- 10. الحضور والانصراف ---
    elif choice == "⏱️ الحضور والانصراف":
        st.header("⏱️ تسجيل حضور وانصراف موظفي المعرض")
        st.dataframe(att_df)
        today = datetime.now().strftime("%Y-%m-%d")
        now_t = datetime.now().strftime("%H:%M:%S")
        
        c1, c2 = st.columns(2)
        if c1.button("⏰ تسجيل حضور اليوم"):
            if not att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today)].empty:
                st.warning("تم تسجيل حضورك بالفعل ليومنا هذا!")
            else:
                new_a = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": today, "وقت الحضور": now_t, "وقت الانصراف": "لم ينصرف"}])
                att_df = pd.concat([att_df, new_a], ignore_index=True)
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"تم تسجيل حضورك في: {now_t}")
                st.rerun()
                
        if c2.button("🚪 تسجيل انصراف الآن"):
            idx = att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today) & (att_df['وقت الانصراف'] == "لم ينصرف")].index
            if not idx.empty:
                att_df.at[idx[0], 'وقت الانصراف'] = now_t
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success("تم تسجيل انصرافك بنجاح!")
                st.rerun()

    # --- 11. 🔐 صفحة الصلاحيات الكاملة وتعديل بيانات حسابات المستخدمين (للمدير فقط) ---
    elif choice == "👥 إدارة الصلاحيات وتعديل الحسابات":
        st.header("👥 إدارة حسابات وتغيير بيانات موظفي ومشرفي معرض الكبير")
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        st.dataframe(u_df, use_container_width=True)
        
        st.subheader("🔄 تعديل وتحديث بيانات حساب الحالي")
        selected_user_to_edit = st.selectbox("اختر الحساب المراد تعديل بياناته"، u_df['username'].unique())
        
        c_edit1, c_edit2, c_edit3 = st.columns(3)
        new_username = c_edit1.text_input("اسم المستخدم الجديد أو الحالي", value=selected_user_to_edit)
        new_password = c_edit2.text_input("كلمة المرور الجديدة", value=u_df[u_df['username'] == selected_user_to_edit]['password'].values[0])
        new_role = c_edit3.selectbox("تحديث رتبة وصلاحية الحساب", ["موظف", "مشرف", "مدير"], index=["موظف", "مشرف", "مدير"].index(u_df[u_df['username'] == selected_user_to_edit]['role'].values[0]))
        
        if st.button("تأكيد وحفظ التغييرات الجديدة للمستخدم"):
            user_idx = u_df[u_df['username'] == selected_user_to_edit].index[0]
            u_df.at[user_idx, 'username'] = new_username
            u_df.at[user_idx, 'password'] = new_password
            u_df.at[user_idx, 'role'] = new_role
            u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
            st.success("✅ تم تحديث بيانات الحساب بنجاح!")
            if selected_user_to_edit == st.session_state.user:
                st.info("لقد قمت بتعديل حسابك الحالي، يرجى تسجيل الخروج والدخول بالبيانات الجديدة.")
            st.rerun()

        st.markdown("---")
        st.subheader("➕ إنشاء حساب لموظف جديد بالمعرض")
        c1, c2, c3 = st.columns(3)
        nu = c1.text_input("اسم المستخدم الجديد")
        np = c2.text_input("كلمة مرور الحساب الجديد", type="password")
        nr = c3.selectbox("الصلاحية الممنوحة له", ["موظف", "مشرف", "مدير"])
        
        if st.button("اعتماد وإنشاء الحساب"):
            if nu and np:
                if nu in u_df['username'].values:
                    st.error("اسم المستخدم هذا مأخوذ مسبقاً!")
                else:
                    new_u = pd.DataFrame([{"username": nu, "password": np, "role": nr}])
                    u_df = pd.concat([u_df, new_u], ignore_index=True)
                    u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                    st.success(f"✅ تم إنشاء حساب بنجاح للـ {nr} ({nu})")
                    st.rerun()

    # --- 12. ⚙️ واجهة تعديل حساب المشرف والموظف من داخل حسابه الخاص ---
    elif choice == "⚙️ إعدادات حسابي":
        st.header("⚙️ تعديل وتحديث بيانات حسابي الخاص")
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        user_row = u_df[u_df['username'] == st.session_state.user].iloc[0]
        
        edit_user = st.text_input("تغيير اسم المستخدم الخاص بك", value=st.session_state.user)
        edit_pass = st.text_input("تغيير كلمة المرور الخاصة بك", value=user_row['password'])
        
        if st.button("حفظ بياناتي الجديدة"):
            if edit_user and edit_pass:
                user_idx = u_df[u_df['username'] == st.session_state.user].index[0]
                # التأكد من عدم تكرار الاسم إن تم تغييره
                if edit_user != st.session_state.user and edit_user in u_df['username'].values:
                    st.error("اسم المستخدم الجديد مأخوذ من قبل موظف آخر!")
                else:
                    u_df.at[user_idx, 'username'] = edit_user
                    u_df.at[user_idx, 'password'] = edit_pass
                    u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                    st.session_state.user = edit_user
                    st.success("✅ تم تحديث بيانات حسابك الشخصي بنجاح!")
                    st.rerun()
