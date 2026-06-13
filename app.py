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

# دالة تهيئة الملفات للتأكد من وجود الحسابات الافتراضية
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
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "العنوان", "نوع البيع", "الصنف", "الكمية", "الخصم %", "إجمالي البيع", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(PURCHASES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "المورد", "الصنف", "الكمية", "إجمالي الشراء", "المسؤول"]).to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
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

# دالة لتوليد كود فاتورة بملف استايل مخصص للـ A5 والـ PDF
def generate_a5_html_invoice(copy_title, inv_id, date, client_name, address, pay_type, user, item, qty, price, discount, final_total):
    return f"""
    <div class="print-invoice-container">
        <style>
            @page {{
                size: A5 portrait;
                margin: 5mm;
            }}
            @media print {{
                body {{ direction: rtl; background: #fff; color: #000; }}
                /* إخفاء عناصر واجهة سيتريمليت تماماً عند الطباعة لحفظ الفاتورة فقط */
                header, [data-testid="stSidebar"], [data-testid="stHeader"], .no-print-btn, .stButton {{
                    display: none !important;
                }}
                .print-invoice-container {{ border: 1px solid #000 !important; box-shadow: none !important; padding: 5mm !important; margin: 0 auto 15mm auto !important; page-break-after: always; }}
            }}
            .print-invoice-container {{
                width: 140mm;
                max-width: 100%;
                border: 2px dashed #333;
                padding: 15px;
                margin: 15px auto;
                direction: rtl;
                text-align: right;
                font-family: 'Cairo', sans-serif;
                background: #fff;
                color: #000;
                border-radius: 6px;
                box-sizing: border-box;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            .invoice-header {{ text-align: center; font-weight: bold; }}
            .invoice-header h2 {{ margin: 0; color: #444; font-size: 16px; }}
            .invoice-header h1 {{ margin: 5px 0; font-size: 20px; color: #000; }}
            .invoice-header p {{ font-size: 11px; margin: 2px; color: #555; }}
            .invoice-details-table {{ width: 100%; font-size: 12px; margin-top: 10px; border-bottom: 1px solid #000; padding-bottom: 5px; }}
            .invoice-items-table {{ width: 100%; border-collapse: collapse; margin-top: 8px; border: 1px solid black; font-size: 12px; text-align: center; }}
            .invoice-items-table th {{ background: #f2f2f2; border: 1px solid black; padding: 6px; font-weight: bold; }}
            .invoice-items-table td {{ border: 1px solid black; padding: 6px; }}
            .invoice-footer-alert {{ margin-top: 10px; font-size: 10px; font-weight: bold; text-align: center; border: 1px solid #000; padding: 5px; background: #f9f9f9; }}
            .no-print-btn {{
                background-color: #2beb67;
                color: white;
                padding: 8px 16px;
                margin: 8px 0;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-family: 'Cairo', sans-serif;
                font-size: 13px;
                font-weight: bold;
            }}
            .no-print-btn:hover {{ background-color: #22c353; }}
        </style>
        
        <div class="invoice-header">
            <h2>📋 {copy_title}</h2>
            <h1>🏢 معرض الكبير</h1>
            <p>العنوان: ابوحماد - قرية العراقي - بجوار مدرسة الشهيد صلاح فتحي</p>
        </div>
        <hr style="border: 1px solid #000; margin: 5px 0;">
        <table class="invoice-details-table">
            <tr><td><b>رقم الفاتورة:</b> {inv_id}</td><td><b>التاريخ:</b> {date}</td></tr>
            <tr><td><b>اسم العميل:</b> {client_name}</td><td><b>العنوان:</b> {address if address else 'غير محدد'}</td></tr>
            <tr><td><b>نوع الدفع:</b> {pay_type}</td><td><b>المسؤول:</b> {user}</td></tr>
        </table>
        <table class="invoice-items-table">
            <tr>
                <th>الصنف والبيان</th>
                <th>الكمية</th>
                <th>سعر المفرد</th>
                <th>الخصم</th>
                <th>الصافي الإجمالي</th>
            </tr>
            <tr>
                <td>{item}</td>
                <td>{qty}</td>
                <td>{price}</td>
                <td>{discount}%</td>
                <td style="font-weight: bold;">{final_total}</td>
            </tr>
        </table>
        <div class="invoice-footer-alert">
            ⚠️ تنبيه هام جداً: مدة الاستبدال والارتجاع 15 يوماً لا غير من تاريخ الفاتورة بشرط سلامة البضاعة وغلافها.
        </div>
        <center><button class="no-print-btn" onclick="window.print()">🖨️ طباعة أو حفظ كـ PDF بمقاس A5</button></center>
    </div>
    """

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    st.title("🏢 نظام معرض الكبير - تسجيل الدخول")
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
        else:
            st.error("بيانات الدخول خاطئة.")
else:
    # --- بناء القائمة الجانبية والصلاحيات حسب الرتبة ---
    st.sidebar.title(f"👤 {st.session_state.user}")
    st.sidebar.write(f"الرتبة: **{st.session_state.role}**")
    
    # توحيد نصوص القائمة لتجنب أخطاء الشرط الشرطي (if condition)
    if st.session_state.role == "مدير":
        menu = ["📦 تكويد الأصناف", "📊 رصيد أول المدة Excel", "🔍 حالة المخزن", "🤝 العملاء والموردين", "📥 فاتورة شراء جديدة", "📤 فاتورة بيع جديدة", "🔎 البحث عن الفواتير وطباعتها", "📈 تقارير البيع والشراء", "💸 المصاريف", "⏰ الحضور والانصراف", "⚙️ إدارة وتعديل الصلاحيات"]
    elif st.session_state.role == "مشرف":
        menu = ["🔍 حالة المخزن", "📥 فاتورة شراء جديدة", "📤 فاتورة بيع جديدة", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"]
    else: # موظف عادي
        menu = ["🔍 حالة المخزن", "📤 فاتورة بيع جديدة", "🔎 البحث عن الفواتير وطباعتها", "⏰ الحضور والانصراف"]
        
    choice = st.sidebar.selectbox("الانتقال إلى", menu)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # قراءة البيانات بشكل فوري ومحدث
    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
    sales_df = pd.read_csv(SALES_FILE, dtype={"رقم الفاتورة": str, "الصنف": str})
    purchases_df = pd.read_csv(PURCHASES_FILE, dtype={"رقم الفاتورة": str})
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
                if iid in inv_df["كود الصنف"].values:
                    st.warning("⚠️ هذا الكود مسجل مسبقاً!")
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
                st.subheader("👀 معاينة البيانات المرفوعة من الشيت:")
                st.dataframe(excel_df)
                if st.button("تأكيد ودمج الملف في رصيد أول المدة"):
                    combined_df = pd.concat([inv_df, excel_df]).drop_duplicates(subset=['كود الصنف'], keep='last')
                    combined_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("🚀 تم رفع وتحديث المخزن بنجاح!")
                    st.rerun()
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")

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
        st.header("📥 تسجيل فاتورة مشتريات جديدة")
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
                new_p = pd.DataFrame([{"رقم الفاتورة": pur_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "المورد": vendor, "الصنف": item, "الكمية": qty, "إجمالي الشراء": total, "المسؤول": st.session_state.user}])
                purchases_df = pd.concat([purchases_df, new_p], ignore_index=True)
                purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم تسجيل الوارد!")
                st.rerun()

    # --- 6. صفحة فاتورة بيع جديدة ---
    elif "فاتورة بيع جديدة" in choice:
        st.header("📤 إنشاء فاتورة مبيعات جديدة - معرض الكبير")
        if inv_df.empty: st.warning("⚠️ المخزن فارغ.")
        else:
            c_list = contacts_df[contacts_df['النوع'] == 'عميل']['الاسم'].unique()
            c1, c2, c3, c4 = st.columns(4)
            cust_type = c1.radio("نوع العميل", ["سريع / غير مسجل", "مسجل مسبقاً"])
            if cust_type == "مسجل مسبقاً" and len(c_list) > 0:
                c_name = c2.selectbox("اختر العميل", c_list)
                c_address = contacts_df[contacts_df['الاسم'] == c_name]['العنوان'].values[0]
            else:
                c_name = c2.text_input("اسم العميل")
                c_address = c3.text_input("عنوان العميل")
            sale_type = c4.selectbox("طبيعة البيع", ["نقدي (كاش)", "آجل (على الحساب)"])
            
            st.markdown("---")
            c5, c6, c7 = st.columns(3)
            selected_item = c5.selectbox("اختر المنتج للبيع", inv_df['اسم الصنف'].unique())
            qty = c6.number_input("الكمية المطلوبة", min_value=1, step=1)
            
            discount = 0.0
            if st.session_state.role in ["مدير", "مشرف"]:
                discount = c7.number_input("نسبة الخصم الممنوحة (%)", min_value=0.0, max_value=100.0, step=0.5)
            else:
                c7.write("🔒 *صلاحية الخصم مغلقة للموظفين*")
                
            item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
            subtotal = float(item_row['سعر البيع']) * qty
            discount_amount = subtotal * (discount / 100)
            final_total = subtotal - discount_amount
            
            st.warning(f"📊 المتوفر: {item_row['الكمية']} | الصافي المطلوب: {final_total}")
            
            if st.button("🧾 إصدار وطباعة الفاتورة الثلاثية (A5)", use_container_width=True):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                if int(inv_df.at[idx, 'الكمية']) < qty:
                    st.error("❌ الكمية لا تكفي!")
                elif not c_name:
                    st.error("❌ يرجى كتابة اسم العميل.")
                else:
                    inv_df.at[idx, 'الكمية'] = int(inv_df.at[idx, 'الكمية']) - qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    inv_id = "INV-" + str(int(datetime.now().timestamp()))
                    new_s = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "اسم العميل": c_name, "العنوان": c_address, "نوع البيع": sale_type, "الصنف": selected_item, "الكمية": qty, "الخصم %": discount, "إجمالي البيع": final_total, "المسؤول": st.session_state.user}])
                    sales_df = pd.concat([sales_df, new_s], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success("🎉 تم حفظ الفاتورة!")
                    
                    # عرض النسخ الثلاثية بمقاس A5 وإتاحة طباعتها/حفظها PDF
                    copies = ["نسخة العميل", "نسخة الإدارة المالية", "نسخة مسؤول المخازن"]
                    for copy in copies:
                        invoice_html = generate_a5_html_invoice(copy, inv_id, datetime.now().strftime("%Y-%m-%d"), c_name, c_address, sale_type, st.session_state.user, selected_item, qty, item_row['سعر البيع'], discount, final_total)
                        st.markdown(invoice_html, unsafe_allow_html=True)

    # --- 7. صفحة البحث عن الفواتير وطباعتها ---
    elif "البحث عن الفواتير وطباعتها" in choice:
        st.header("🔎 نظام البحث ومراجعة الفواتير السابقة وطباعتها (A5)")
        if sales_df.empty:
            st.info("لا توجد فواتير مبيعات مسجلة في النظام حتى الآن.")
        else:
            search_query = st.text_input("ابحث عن فاتورة (أدخل رقم الفاتورة أو اسم العميل)").strip()
            
            if search_query:
                filtered_sales = sales_df[sales_df['رقم الفاتورة'].str.contains(search_query, case=False, na=False) | sales_df['اسم العميل'].str.contains(search_query, case=False, na=False)]
            else:
                filtered_sales = sales_df
                
            st.write(f"عدد الفواتير المكتشفة: {len(filtered_sales)}")
            st.dataframe(filtered_sales, use_container_width=True)
            
            if not filtered_sales.empty:
                st.subheader("⚙️ اختر الفاتورة المراد إعادة عرضها وطباعتها كـ PDF مقاس A5:")
                selected_inv_id = st.selectbox("اختر رقم الفاتورة", filtered_sales['رقم الفاتورة'].unique())
                
                f_row = sales_df[sales_df['رقم الفاتورة'] == selected_inv_id].iloc[0]
                
                # جلب سعر الصنف المفرد من جدول المخزن الحالي لعرضه بشكل صحيح في الفاتورة
                match_inv_item = inv_df[inv_df['اسم الصنف'] == f_row['الصنف']]
                unit_price = match_inv_item.iloc[0]['سعر البيع'] if not match_inv_item.empty else 0.0
                
                st.markdown("---")
                st.subheader(f"📄 عرض الفاتورة رقم {selected_inv_id}")
                
                copies = ["نسخة العميل", "نسخة الإدارة المالية", "نسخة مسؤول المخازن"]
                for copy in copies:
                    invoice_html = generate_a5_html_invoice(copy, f_row['رقم الفاتورة'], f_row['التاريخ'], f_row['اسم العميل'], f_row['العنوان'], f_row['نوع البيع'], f_row['المسؤول'], f_row['الصنف'], f_row['الكمية'], unit_price, f_row['الخصم %'], f_row['إجمالي البيع'])
                    st.markdown(invoice_html, unsafe_allow_html=True)

    # --- 8. صفحة التقارير ---
    elif "تقارير البيع والشراء" in choice:
        st.header("📈 التقارير المالية التفصيلية لمعرض الكبير")
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
                if not match_inv.empty:
                    total_cost_of_goods_sold += float(match_inv.iloc[0]['سعر الشراء']) * int(row['الكمية'])
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
            if not att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today)].empty:
                st.warning("⚠️ تم تسجيل حضورك مسبقاً!")
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
        st.header("⚙️ إدارة وتعديل حسابات موظفي ومشرفي معرض الكبير")
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        st.dataframe(u_df, use_container_width=True)
        
        tab_add, tab_edit = st.tabs(["➕ إنشاء حساب جديد", "✏️ تعديل وتحديث حساب حالي / حذف حساب"])
        
        with tab_add:
            st.subheader("👤 إضافة مستخدم جديد للنظام")
            c1, c2, c3 = st.columns(3)
            nu = c1.text_input("اسم المستخدم الجديد", key="new_un")
            np = c2.text_input("كلمة المرور الجديدة", type="password", key="new_pw")
            nr = c3.selectbox("الصلاحية الممنوحة له", ["موظف", "مشرف", "مدير"], key="new_rl")
            if st.button("اعتماد وإنشاء الحساب", use_container_width=True):
                if nu and np:
                    if nu in u_df["username"].values:
                        st.error("❌ اسم المستخدم هذا مسجل بالفعل!")
                    else:
                        new_u = pd.DataFrame([{"username": nu, "password": np, "role": nr}])
                        u_df = pd.concat([u_df, new_u], ignore_index=True)
                        u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                        st.success(f"🎉 تم إنشاء حساب بنجاح للـ {nr} ({nu})")
                        st.rerun()
                else:
                    st.error("يرجى إدخال البيانات كاملة.")
                    
        with tab_edit:
            st.subheader("✏️ تعديل بيانات الحسابات الحالية")
            target_user = st.selectbox("اختر الحساب الذي تريد تعديله أو حذفه", u_df["username"].unique())
            
            # جلب البيانات الحالية للحساب المختار
            user_data = u_df[u_df["username"] == target_user].iloc[0]
            
            c1, c2, c3 = st.columns(3)
            edit_username = c1.text_input("تعديل اسم المستخدم", value=user_data["username"])
            edit_password = c2.text_input("تعديل كلمة المرور", value=user_data["password"])
            edit_role = c3.selectbox("تعديل الصلاحية الرتبية", ["موظف", "مشرف", "مدير"], index=["موظف", "مشرف", "مدير"].index(user_data["role"]))
            
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("💾 حفظ التعديلات الجديدة", use_container_width=True):
                idx = u_df[u_df["username"] == target_user].index[0]
                u_df.at[idx, "username"] = edit_username
                u_df.at[idx, "password"] = edit_password
                u_df.at[idx, "role"] = edit_role
                u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                st.success("🎉 تم تحديث بيانات الحساب بنجاح!")
                st.rerun()
                
            if col_btn2.button("❌ حذف هذا الحساب نهائياً", use_container_width=True):
                if target_user == "admin":
                    st.error("❌ لا يمكن حذف الحساب الافتراضي الرئيسي (admin) لحماية النظام!")
                else:
                    u_df = u_df[u_df["username"] != target_user]
                    u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                    st.success(f"🔥 تم حذف حساب {target_user} بنجاح من النظام!")
                    st.rerun
