import streamlit as st
import pandas as pd
import os
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة المبيعات والمخازن المتكامل", layout="wide")

# أسماء ملفات البيانات
INVENTORY_FILE = "inventory_data.csv"
USERS_FILE = "users_data.csv"
SALES_FILE = "sales_data.csv"
PURCHASES_FILE = "purchases_data.csv"
EXPENSES_FILE = "expenses_data.csv"
ATTENDANCE_FILE = "attendance_data.csv"
CONTACTS_FILE = "contacts_data.csv" # ملف العملاء والموردين

# دالة تهيئة الملفات
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([{"username": "admin", "password": "123", "role": "مدير"},
                      {"username": "user1", "password": "111", "role": "موظف"}]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "اسم العميل", "العنوان", "نوع البيع", "الصنف", "الكمية", "إجمالي البيع", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(PURCHASES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "المورد", "الصنف", "الكمية", "إجمالي الشراء", "المسؤول"]).to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(EXPENSES_FILE):
        pd.DataFrame(columns=["التاريخ", "البيان", "المبلغ", "المسؤول"]).to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(ATTENDANCE_FILE):
        pd.DataFrame(columns=["الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف"]).to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(CONTACTS_FILE):
        pd.DataFrame(columns=["النوع", "الاسم", "الهاتف", "العنوان"]).to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')

init_files()

# إدارة الجلسة
if 'auth' not in st.session_state: st.session_state.auth = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "موظف"

# --- واجهة تسجيل الدخول ---
if not st.session_state.auth:
    st.title("🔐 نظام ERP الذكي - تسجيل الدخول")
    user_input = st.text_input("اسم المستخدم").strip()
    pw_input = st.text_input("كلمة المرور", type="password").strip()
    
    if st.button("دخول", use_container_width=True):
        u_df = pd.read_csv(USERS_FILE, dtype=str)
        match = u_df[(u_df['username'] == user_input) & (u_df['password'] == pw_input)]
        if not match.empty:
            st.session_state.auth = True
            st.session_state.user = user_input
            st.session_state.role = match.iloc[0]['role']
            st.success("تم الدخول بنجاح!")
            st.rerun()
        else:
            st.error("بيانات الدخول خاطئة.")
else:
    # --- القائمة الجانبية والصلاحيات ---
    st.sidebar.title(f"👤 {st.session_state.user} ({st.session_state.role})")
    
    if st.session_state.role == "مدير":
        menu = ["🗂️ تكويد الأصناف", "📦 حالة المخزن", "🤝 العملاء والموردين", "🛍️ فاتورة شراء جديدة", "💰 فاتورة بيع جديدة", "📊 تقارير البيع والشراء", "💸 المصاريف", "⏱️ الحضور والانصراف", "👥 إدارة الصلاحيات"]
    else:
        menu = ["📦 حالة المخزن", "🛍️ فاتورة شراء جديدة", "💰 فاتورة بيع جديدة", "⏱️ الحضور والانصراف"]
        
    choice = st.sidebar.selectbox("الانتقال إلى", menu)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # قراءة البيانات المستمرة
    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
    sales_df = pd.read_csv(SALES_FILE)
    purchases_df = pd.read_csv(PURCHASES_FILE)
    exp_df = pd.read_csv(EXPENSES_FILE)
    att_df = pd.read_csv(ATTENDANCE_FILE)
    contacts_df = pd.read_csv(CONTACTS_FILE, dtype=str)

    # --- 1. صفحة تكويد الأصناف ---
    if choice == "🗂️ تكويد الأصناف":
        st.header("🗂️ تكويد تعريف أصناف جديدة في النظام")
        st.dataframe(inv_df, use_container_width=True)
        
        st.subheader("➕ إضافة صنف وتكويده")
        c1, c2, c3, c4 = st.columns(4)
        iid = c1.text_input("كود الصنف (الباركود / ID)")
        iname = c2.text_input("اسم الصنف والمنتج")
        ipurchase = c3.number_input("سعر الشراء الافتراضي", min_value=0.0)
        isale = c4.number_input("سعر البيع الافتراضي", min_value=0.0)
        
        if st.button("تكويد وحفظ الصنف"):
            if iid and iname:
                if iid in inv_df["كود الصنف"].values:
                    st.warning("⚠️ هذا الكود مسجل مسبقاً!")
                else:
                    new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "الكمية": 0, "سعر الشراء": ipurchase, "سعر البيع": isale}])
                    inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("✅ تم تكويد الصنف الجديد بنجاح في المخازن!")
                    st.rerun()
            else:
                st.error("يرجى كتابة الكود والاسم.")

    # --- 2. صفحة حالة المخزن ---
    elif choice == "📦 حالة المخزن":
        st.header("📦 جرد وحالة بضائع المخزن الحالية")
        st.dataframe(inv_df, use_container_width=True)

    # --- 3. صفحة العملاء والموردين ---
    elif choice == "🤝 العملاء والموردين":
        st.header("🤝 إدارة بيانات العملاء والموردين")
        st.dataframe(contacts_df, use_container_width=True)
        
        st.subheader("➕ إضافة جهة اتصال جديدة")
        c1, c2, c3, c4 = st.columns(4)
        ctype = c1.selectbox("النوع", ["عميل", "مورد"])
        cname = c2.text_input("الاسم الكامل")
        cphone = c3.text_input("رقم الهاتف")
        caddress = c4.text_input("العنوان بالتفصيل")
        
        if st.button("حفظ البيانات"):
            if cname:
                new_contact = pd.DataFrame([{"النوع": ctype, "الاسم": cname, "الهاتف": cphone, "العنوان": caddress}])
                contacts_df = pd.concat([contacts_df, new_contact], ignore_index=True)
                contacts_df.to_csv(CONTACTS_FILE, index=False, encoding='utf-8-sig')
                st.success(f"✅ تم حفظ بيانات الـ ({ctype}) بنجاح!")
                st.rerun()
            else:
                st.error("يرجى إدخال الاسم على الأقل.")

    # --- 4. صفحة فاتورة شراء جديدة (المشتريات) ---
    elif choice == "🛍️ فاتورة شراء جديدة":
        st.header("🛍️ تسجيل فاتورة مشتريات جديدة (وارد للمخزن)")
        if inv_df.empty:
            st.warning("⚠️ يجب تكويد الأصناف أولاً في صفحة (تكويد الأصناف).")
        else:
            mوردين_list = contacts_df[contacts_df['النوع'] == 'مورد']['الاسم'].unique()
            if len(mوردين_list) == 0: mوردين_list = ["مورد عام"]
                
            c1, c2, c3 = st.columns(3)
            selected_vendor = c1.selectbox("اختر المورد", mوردين_list)
            selected_item = c2.selectbox("اختر الصنف المشترى", inv_df['اسم الصنف'].unique())
            qty = c3.number_input("الكمية المشتراة", min_value=1, step=1)
            
            item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
            total = item_row['سعر الشراء'] * qty
            st.info(f"💵 سعر شراء الصنف: {item_row['سعر الشراء']} | إجمالي الفاتورة: {total}")
            
            if st.button("تأكيد وحفظ فاتورة المشتريات"):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                inv_df.at[idx, 'الكمية'] += qty # زيادة المخزن
                inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                
                inv_id = "PUR-" + str(int(datetime.now().timestamp()))
                new_pur = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "المورد": selected_vendor, "الصنف": selected_item, "الكمية": qty, "إجمالي الشراء": total, "المسؤول": st.session_state.user}])
                purchases_df = pd.concat([purchases_df, new_pur], ignore_index=True)
                purchases_df.to_csv(PURCHASES_FILE, index=False, encoding='utf-8-sig')
                st.success("✅ تم حفظ المشتريات وزيادة بضاعة المخزن!")

    # --- 5. صفحة فاتورة بيع جديدة (المبيعات) ---
    elif choice == "💰 فاتورة بيع جديدة":
        st.header("💰 إنشاء فاتورة مبيعات جديدة (صادر من المخزن)")
        if inv_df.empty:
            st.warning("⚠️ المخزن فارغ.")
        else:
            عملاء_list = contacts_df[contacts_df['النوع'] == 'عميل']['الاسم'].unique()
            
            c1, c2, c3, c4 = st.columns(4)
            
            # ميزة اختيار عميل مسجل أو كتابة عميل جديد يدوي في الفاتورة
            cust_type = c1.radio("العميل", ["مسجل بالنظام", "عميل جديد/نقدي سريع"])
            if cust_type == "مسجل بالنظام" and len(عملاء_list) > 0:
                client_name = c2.selectbox("اختر العميل", عملاء_list)
                client_address = contacts_df[contacts_df['الاسم'] == client_name]['العنوان'].values[0]
            else:
                client_name = c2.text_input("اسم العميل الجديد")
                client_address = c3.text_input("عنوان العميل")
                
            sale_type = c4.selectbox("نوع البيع", ["نقدي (كاش)", "آجل (على الحساب)"])
            
            st.markdown("---")
            c5, c6 = st.columns(2)
            selected_item = c5.selectbox("اختر المنتج للبيع", inv_df['اسم الصنف'].unique())
            qty = c6.number_input("الكمية المباعة", min_value=1, step=1)
            
            item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
            total = item_row['سعر البيع'] * qty
            
            st.warning(f"📦 المتوفر بالمخزن: {item_row['الكمية']} | 💵 سعر البيع: {item_row['سعر البيع']} | 🧾 الإجمالي: {total}")
            
            if st.button("إصدار وطباعة فاتورة البيع"):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                if inv_df.at[idx, 'الكمية'] < qty:
                    st.error("❌ خطأ: الكمية المتوفرة في المخزن لا تكفي لإتمام هذه البيعة!")
                elif not client_name:
                    st.error("❌ يرجى كتابة اسم العميل.")
                else:
                    # خصم الكمية من المخزن
                    inv_df.at[idx, 'الكمية'] -= qty
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    inv_id = "SAL-" + str(int(datetime.now().timestamp()))
                    new_sale = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "اسم العميل": client_name, "العنوان": client_address, "نوع البيع": sale_type, "الصنف": selected_item, "الكمية": qty, "إجمالي البيع": total, "المسؤول": st.session_state.user}])
                    sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success("✅ تم تسجيل عملية البيع بنجاح!")
                    
                    # نموذج الفاتورة الجاهز للطباعة
                    st.subheader("🖨️ فاتورة جاهزة للطباعة")
                    invoice_template = f"""
                    <div style="border:3px dashed #10b981; padding:25px; direction:rtl; text-align:right; font-family:'Cairo'; background-color:#161b22; color:white; border-radius:10px;">
                        <h2 style="text-align:center; color:#10b981;">🧾 فاتورة مبيعات رسمية</h2>
                        <p><b>رقم الفاتورة:</b> {inv_id} | <b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d')}</p>
                        <p><b>اسم العميل:</b> {client_name} </p>
                        <p><b>العنوان:</b> {client_address if client_address else 'غير مسجل'}</p>
                        <p><b>طريقة الدفع وطبيعة العملية:</b> <span style="background-color:gray; padding:2px 5px; border-radius:3px;">{sale_type}</span></p>
                        <hr style="border-color:#10b981;">
                        <table style="width:100%; text-align:right; color:white;">
                            <tr><th>الصنف</th><th>الكمية</th><th>السعر</th></tr>
                            <tr><td>{selected_item}</td><td>{qty}</td><td>{item_row['سعر البيع']}</td></tr>
                        </table>
                        <hr style="border-color:#10b981;">
                        <h3 style="color:#10b981;">💰 الصافي الإجمالي: {total} ريال / جنيه</h3>
                        <p style="font-size:12px; color:gray; text-align:center;">شكراً لتعاملكم معنا | الموظف المسؤول: {st.session_state.user}</p>
                    </div>
                    """
                    st.markdown(invoice_template, unsafe_allow_html=True)
                    st.info("💡 للطباعة المباشرة بالفأرة: اضغط كليك يمين في أي مكان بالصفحة ثم اختر Print (أو Ctrl+P).")

    # --- 6. صفحة تقارير البيع والشراء (للمدير فقط) ---
    elif choice == "📊 تقارير البيع والشراء":
        st.header("📊 كشف وتقارير حركة البيع والشراء والأرباح")
        
        t1, t2 = st.tabs(["📝 سجل المبيعات", "📝 سجل المشتريات"])
        with t1:
            st.subheader("سجل مبيعات الفواتير الصادرة")
            st.dataframe(sales_df, use_container_width=True)
        with t2:
            st.subheader("سجل مشتريات البضائع الواردة")
            st.dataframe(purchases_df, use_container_width=True)
            
        st.markdown("---")
        st.subheader("📈 ملخص الأرباح والخزينة")
        total_s = sales_df['إجمالي البيع'].sum()
        total_p = purchases_df['إجمالي الشراء'].sum()
        total_e = exp_df['المبلغ'].sum()
        net = total_s - (total_p + total_e)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 إجمالي حجم المبيعات", f"{total_s}")
        c2.metric("🛍️ إجمالي المشتريات", f"{total_p}")
        c3.metric("💸 المصاريف الإدارية", f"{total_e}")
        c4.metric("📈 صافي الربح الفعلي", f"{net}", delta=float(net))

    # --- 7. صفحة المصاريف ---
    elif choice == "💸 المصاريف":
        st.header("💸 تسجيل النفقات والمصاريف الأخرى")
        st.dataframe(exp_df, use_container_width=True)
        c1, c2 = st.columns(2)
        title = c1.text_input("بيان المصروف")
        amt = c2.number_input("المبلغ", min_value=0.0)
        if st.button("حفظ المصروف"):
            if title and amt > 0:
                new_exp = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d"), "البيان": title, "المبلغ": amt, "المسؤول": st.session_state.user}])
                exp_df = pd.concat([exp_df, new_exp], ignore_index=True)
                exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                st.success("تم الحفظ!")
                st.rerun()

    # --- 8. صفحة الحضور والانصراف ---
    elif choice == "⏱️ الحضور والانصراف":
        st.header("⏱️ إثبات توقيت الحضور والانصراف")
        st.dataframe(att_df, use_container_width=True)
        today = datetime.now().strftime("%Y-%m-%d")
        now_t = datetime.now().strftime("%H:%M:%S")
        
        c1, c2 = st.columns(2)
        if c1.button("⏰ إثبات حضور", use_container_width=True):
            if not att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today)].empty:
                st.warning("مسجل حضور مسبقاً اليوم!")
            else:
                new_att = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": today, "وقت الحضور": now_t, "وقت الانصراف": "لم ينصرف"}])
                att_df = pd.concat([att_df, new_att], ignore_index=True)
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"تم تسجيل حضورك بنجاح في {now_t}")
                st.rerun()
                
        if c2.button("🚪 إثبات انصراف", use_container_width=True):
            idx = att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today) & (att_df['وقت الانصراف'] == "لم ينصرف")].index
            if not idx.empty:
                att_df.at[idx[0], 'وقت الانصراف'] = now_t
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"تم الانصراف بنجاح في {now_t}")
                st.rerun()

    # --- 9. صفحة إدارة الصلاحيات ---
    elif choice == "👥 إدارة الصلاحيات":
        st.header("👥 حسابات المستخدمين")
        u_df = pd.read_csv(USERS_FILE)
        st.dataframe(u_df, use_container_width=True)
        
        st.subheader("➕ إضافة مستخدم جديد وتخصيص صلاحيته")
        c1, c2, c3 = st.columns(3)
        nu = c1.text_input("اليوزر الجديد")
        np = c2.text_input("الباسورد", type="password")
        nr = c3.selectbox("نوع الصلاحية", ["موظف", "مدير"])
        
        if st.button("تفعيل اليوزر الجديد"):
            if nu and np:
                new_u = pd.DataFrame([{"username": nu, "password": np, "role": nr}])
                u_df = pd.concat([u_df, new_u], ignore_index=True)
                u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                st.success("تم الحفظ!")
                st.rerun()
