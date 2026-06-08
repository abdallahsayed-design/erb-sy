import streamlit as st
import pandas as pd
import os
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام الإدارة والمخازن المتكامل", layout="wide")

# أسماء ملفات البيانات
INVENTORY_FILE = "inventory_data.csv"
USERS_FILE = "users_data.csv"
SALES_FILE = "sales_data.csv"
EXPENSES_FILE = "expenses_data.csv"
ATTENDANCE_FILE = "attendance_data.csv"

# دالة تهيئة الملفات
def init_files():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame([{"username": "admin", "password": "123", "role": "مدير"},
                      {"username": "user1", "password": "111", "role": "موظف"}]).to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(INVENTORY_FILE):
        pd.DataFrame(columns=["كود الصنف", "اسم الصنف", "الكمية", "سعر الشراء", "سعر البيع"]).to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(SALES_FILE):
        pd.DataFrame(columns=["رقم الفاتورة", "التاريخ", "نوع الفاتورة", "الصنف", "الكمية", "إجمالي السعر", "المسؤول"]).to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(EXPENSES_FILE):
        pd.DataFrame(columns=["التاريخ", "البيان", "المبلغ", "المسؤول"]).to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
    if not os.path.exists(ATTENDANCE_FILE):
        pd.DataFrame(columns=["الموظف", "التاريخ", "وقت الحضور", "وقت الانصراف"]).to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')

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
    # --- القائمة الجانبية بناءً على الصلاحيات ---
    st.sidebar.title(f"👤 {st.session_state.user} ({st.session_state.role})")
    
    # تحديد الخيارات المتاحة حسب نوع المستخدم
    if st.session_state.role == "مدير":
        menu = ["📦 المخزن", "🧾 الفواتير والطباعة", "📉 الأرباح والمالية", "💸 المصاريف", "⏱️ الحضور والانصراف", "👥 إدارة الصلاحيات"]
    else:
        menu = ["📦 المخزن", "🧾 الفواتير والطباعة", "⏱️ الحضور والانصراف"] # الموظف العادي محجوب عنه المالية والصلاحيات
        
    choice = st.sidebar.selectbox("الانتقال إلى", menu)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.auth = False
        st.rerun()

    # قراءة البيانات المستمرة
    inv_df = pd.read_csv(INVENTORY_FILE, dtype={"كود الصنف": str})
    sales_df = pd.read_csv(SALES_FILE)
    exp_df = pd.read_csv(EXPENSES_FILE)
    att_df = pd.read_csv(ATTENDANCE_FILE)

    # --- 1. صفحة المخزن ---
    if choice == "📦 المخزن":
        st.header("📊 إدارة بضائع المخزن")
        st.dataframe(inv_df, use_container_width=True)
        
        if st.session_state.role == "مدير":
            st.subheader("➕ إضافة صنف جديد للمستودع")
            c1, c2, c3, c4 = st.columns(4)
            iid = c1.text_input("كود الصنف")
            iname = c2.text_input("اسم الصنف")
            ipurchase = c3.number_input("سعر الشراء", min_value=0.0)
            isale = c4.number_input("سعر البيع", min_value=0.0)
            
            if st.button("حفظ الصنف"):
                if iid and iname:
                    new_item = pd.DataFrame([{"كود الصنف": iid, "اسم الصنف": iname, "الكمية": 0, "سعر الشراء": ipurchase, "سعر البيع": isale}])
                    inv_df = pd.concat([inv_df, new_item], ignore_index=True)
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    st.success("تم تسجيل الصنف!")
                    st.rerun()

    # --- 2. صفحة الفواتير والطباعة ---
    elif choice == "🧾 الفواتير والطباعة":
        st.header("🧾 إنشاء فواتير (بيع / شراء)")
        f_type = st.radio("نوع الفاتورة", ["فاتورة بيع (صادر)", "فاتورة شراء (وارد)"])
        
        if inv_df.empty:
            st.warning("يرجى إضافة أصناف في المخزن أولاً.")
        else:
            c1, c2 = st.columns(2)
            selected_item = c1.selectbox("اختر الصنف", inv_df['اسم الصنف'].unique())
            qty = c2.number_input("الكمية", min_value=1, step=1)
            
            item_row = inv_df[inv_df['اسم الصنف'] == selected_item].iloc[0]
            price = item_row['سعر البيع'] if f_type == "فاتورة بيع (صادر)" else item_row['سعر الشراء']
            total = price * qty
            
            st.info(f"💰 السعر المفرد: {price} | الإجمالي المتوقع: {total}")
            
            if st.button("إصدار الفاتورة وحفظها"):
                idx = inv_df[inv_df['اسم الصنف'] == selected_item].index[0]
                
                if f_type == "فاتورة بيع (صادر)" and inv_df.at[idx, 'الكمية'] < qty:
                    st.error("❌ الكمية في المخزن لا تكفي للبيع!")
                else:
                    # تحديث المخزن
                    if f_type == "فاتورة بيع (صادر)":
                        inv_df.at[idx, 'الكمية'] -= qty
                    else:
                        inv_df.at[idx, 'الكمية'] += qty
                        
                    inv_df.to_csv(INVENTORY_FILE, index=False, encoding='utf-8-sig')
                    
                    # حفظ الفاتورة
                    inv_id = str(int(datetime.now().timestamp()))
                    new_invoice = pd.DataFrame([{"رقم الفاتورة": inv_id, "التاريخ": datetime.now().strftime("%Y-%m-%d"), "نوع الفاتورة": f_type, "الصنف": selected_item, "الكمية": qty, "إجمالي السعر": total, "المسؤول": st.session_state.user}])
                    sales_df = pd.concat([sales_df, new_invoice], ignore_index=True)
                    sales_df.to_csv(SALES_FILE, index=False, encoding='utf-8-sig')
                    
                    st.success("✅ تم إصدار الفاتورة وتحديث المخازن!")
                    
                    # عرض الفاتورة للطباعة
                    st.markdown("---")
                    st.subheader("🖨️ نموذج الفاتورة للطباعة")
                    invoice_box = f"""
                    <div style="border:2px solid black; padding:20px; direction:rtl; text-align:right; font-family: 'Cairo';">
                        <h2>🧾 فاتورة رسمية</h2>
                        <p><b>رقم الفاتورة:</b> {inv_id}</p>
                        <p><b>التاريخ:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                        <p><b>نوع العملية:</b> {f_type}</p>
                        <hr>
                        <p><b>اسم الصنف:</b> {selected_item}</p>
                        <p><b>الكمية:</b> {qty}</p>
                        <h3><b>الإجمالي الصافي: {total} ريال/جنيه</b></h3>
                        <hr>
                        <p><b>الموظف المسؤول:</b> {st.session_state.user}</p>
                    </div>
                    """
                    st.markdown(invoice_box, unsafe_allow_html=True)
                    st.write("💡 نصيحة: للطباعة اضغط على (Ctrl + P) من لوحة المفاتيح واكتب الفاتورة.")

    # --- 3. صفحة الأرباح والمالية (للمدير فقط) ---
    elif choice == "📉 الأرباح والمالية":
        st.header("📊 التقارير المالية وصافي الأرباح")
        
        total_sales = sales_df[sales_df['نوع الفاتورة'] == "فاتورة بيع (صادر)"]['إجمالي السعر'].sum()
        total_purchases = sales_df[sales_df['نوع الفاتورة'] == "فاتورة شراء (وارد)"]['إجمالي السعر'].sum()
        total_expenses = exp_df['المبلغ'].sum()
        
        net_profit = total_sales - (total_purchases + total_expenses)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📈 إجمالي المبيعات", f"{total_sales}")
        c2.metric("📉 إجمالي المشتريات", f"{total_purchases}")
        c3.metric("💸 إجمالي المصاريف", f"{total_expenses}")
        c4.metric("💰 صافي الأرباح", f"{net_profit}", delta=float(net_profit))

    # --- 4. صفحة المصاريف (للمدير فقط) ---
    elif choice == "💸 المصاريف":
        st.header("💸 تسجيل المصاريف الإدارية والمالية")
        st.dataframe(exp_df, use_container_width=True)
        
        c1, c2 = st.columns(2)
        exp_title = c1.text_input("بيان الصرف (مثال: إيجار، كهرباء، رواتب)")
        exp_amount = c2.number_input("المبلغ المستحق", min_value=0.0)
        
        if st.button("تسجيل المصروف"):
            if exp_title and exp_amount > 0:
                new_exp = pd.DataFrame([{"التاريخ": datetime.now().strftime("%Y-%m-%d"), "البيان": exp_title, "المبلغ": exp_amount, "المسؤول": st.session_state.user}])
                exp_df = pd.concat([exp_df, new_exp], ignore_index=True)
                exp_df.to_csv(EXPENSES_FILE, index=False, encoding='utf-8-sig')
                st.success("تم تسجيل المصروف بنجاح!")
                st.rerun()

    # --- 5. صفحة الحضور والانصراف ---
    elif choice == "⏱️ الحضور والانصراف":
        st.header("⏱️ نظام إثبات الحضور والانصراف اليومي")
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")
        
        st.dataframe(att_df, use_container_width=True)
        
        c1, c2 = st.columns(2)
        if c1.button("⏰ تسجيل حضور الآن", use_container_width=True):
            if not att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today)].empty:
                st.warning("أنت مسجل حضور بالفعل اليوم!")
            else:
                new_att = pd.DataFrame([{"الموظف": st.session_state.user, "التاريخ": today, "وقت الحضور": now_time, "وقت الانصراف": "لم ينصرف"}])
                att_df = pd.concat([att_df, new_att], ignore_index=True)
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"تم تسجيل حضورك الساعة {now_time}")
                st.rerun()
                
        if c2.button("🚪 تسجيل انصراف الآن", use_container_width=True):
            idx = att_df[(att_df['الموظف'] == st.session_state.user) & (att_df['التاريخ'] == today) & (att_df['وقت الانصراف'] == "لم ينصرف")].index
            if not idx.empty:
                att_df.at[idx[0], 'وقت الانصراف'] = now_time
                att_df.to_csv(ATTENDANCE_FILE, index=False, encoding='utf-8-sig')
                st.success(f"تم تسجيل انصرافك الساعة {now_time}")
                st.rerun()
            else:
                st.error("لم يتم العثور على سجل حضور مفتوح لك اليوم أو أنك انصرفت بالفعل.")

    # --- 6. صفحة إدارة الصلاحيات (للمدير فقط) ---
    elif choice == "👥 إدارة الصلاحيات":
        st.header("👥 إضافة يوزرات وتحديد الصلاحيات")
        u_df = pd.read_csv(USERS_FILE)
        st.dataframe(u_df, use_container_width=True)
        
        st.subheader("➕ إضافة حساب موظف جديد بمرتبة محددة")
        c1, c2, c3 = st.columns(3)
        nu = c1.text_input("اسم المستخدم الجديد")
        np = c2.text_input("الباسورد", type="password")
        nrole = c3.selectbox("الصلاحية المنوحة", ["موظف", "مدير"])
        
        if st.button("اعتماد الحساب الجديد"):
            if nu and np:
                new_u_row = pd.DataFrame([{"username": nu, "password": np, "role": nrole}])
                u_df = pd.concat([u_df, new_u_row], ignore_index=True)
                u_df.to_csv(USERS_FILE, index=False, encoding='utf-8-sig')
                st.success(f"تم إنشاء حساب ({nu}) بصلاحية [{nrole}] بنجاح.")
                st.rerun()