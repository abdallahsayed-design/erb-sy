elkabeer_system/
│
├── app.py
├── database.db
├── assets/
│   └── logo.png
│
├── pages/
│   ├── inventory.py
│   ├── sales.py
│   ├── installments.py
│   ├── purchases.py
│   ├── customers.py
│   ├── reports.py
│   └── users.py
│
├── pdf/
│   └── invoices/
│
└── backups/

    CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    item_name TEXT,
    purchase_price REAL,
    sale_price REAL,
    quantity INTEGER
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    national_id TEXT,
    address TEXT,
    guarantor_name TEXT,
    guarantor_phone TEXT
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    customer_id INTEGER,
    total_amount REAL,
    discount REAL,
    net_amount REAL,
    sale_date TEXT
);

CREATE TABLE installments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    invoice_no TEXT,
    item_name TEXT,
    total_price REAL,
    down_payment REAL,
    remaining_amount REAL,
    months INTEGER,
    monthly_installment REAL,
    start_date TEXT,
    status TEXT
);

CREATE TABLE installment_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installment_id INTEGER,
    due_date TEXT,
    amount REAL,
    paid INTEGER DEFAULT 0,
    payment_date TEXT
);

CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    address TEXT
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
);

# database.py

import sqlite3

DB_NAME = "database.db"

def create_database():
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

```
# جدول الأصناف
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    barcode TEXT UNIQUE,
    item_name TEXT NOT NULL,
    purchase_price REAL DEFAULT 0,
    sale_price REAL DEFAULT 0,
    quantity INTEGER DEFAULT 0
)
""")

# جدول العملاء
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    national_id TEXT,
    address TEXT,
    guarantor_name TEXT,
    guarantor_phone TEXT
)
""")

# جدول الموردين
cursor.execute("""
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT
)
""")

# جدول المستخدمين
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# جدول المبيعات
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_no TEXT,
    customer_id INTEGER,
    total_amount REAL,
    discount REAL,
    net_amount REAL,
    sale_date TEXT
)
""")

# جدول التقسيط
cursor.execute("""
CREATE TABLE IF NOT EXISTS installments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    invoice_no TEXT,
    item_name TEXT,
    total_price REAL,
    down_payment REAL,
    remaining_amount REAL,
    months INTEGER,
    monthly_installment REAL,
    start_date TEXT,
    status TEXT DEFAULT 'نشط'
)
""")

# تفاصيل الأقساط
cursor.execute("""
CREATE TABLE IF NOT EXISTS installment_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installment_id INTEGER,
    due_date TEXT,
    amount REAL,
    paid INTEGER DEFAULT 0,
    payment_date TEXT
)
""")

# إدخال المستخدمين الافتراضيين
cursor.execute("""
INSERT OR IGNORE INTO users
(username,password,role)
VALUES
('superadmin','789','مدير عام')
""")

cursor.execute("""
INSERT OR IGNORE INTO users
(username,password,role)
VALUES
('admin','123','مدير')
""")

cursor.execute("""
INSERT OR IGNORE INTO users
(username,password,role)
VALUES
('sharaf','456','مشرف')
""")

conn.commit()
conn.close()
```

if **name** == "**main**":
create_database()
print("تم إنشاء قاعدة البيانات بنجاح")

import streamlit as st
import sqlite3

# إعداد الصفحة

st.set_page_config(
page_title="نظام معرض الكبير",
page_icon="🏪",
layout="wide"
)

DB_NAME = "database.db"

# الاتصال بقاعدة البيانات

def get_connection():
return sqlite3.connect(DB_NAME)

# التحقق من المستخدم

def login(username, password):
conn = get_connection()
cursor = conn.cursor()

```
cursor.execute(
    "SELECT username, role FROM users WHERE username=? AND password=?",
    (username, password)
)

user = cursor.fetchone()
conn.close()

return user
```

# Session State

if "logged_in" not in st.session_state:
st.session_state.logged_in = False

if "username" not in st.session_state:
st.session_state.username = ""

if "role" not in st.session_state:
st.session_state.role = ""

# شاشة تسجيل الدخول

if not st.session_state.logged_in:

```
st.title("🏪 نظام معرض الكبير")
st.subheader("تسجيل الدخول")

username = st.text_input("اسم المستخدم")
password = st.text_input("كلمة المرور", type="password")

if st.button("دخول", use_container_width=True):

    user = login(username, password)

    if user:
        st.session_state.logged_in = True
        st.session_state.username = user[0]
        st.session_state.role = user[1]

        st.success("تم تسجيل الدخول بنجاح")
        st.rerun()

    else:
        st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
```

# بعد تسجيل الدخول

else:

```
st.sidebar.title("القائمة الرئيسية")

st.sidebar.write(
    f"👤 المستخدم: {st.session_state.username}"
)

st.sidebar.write(
    f"🔑 الصلاحية: {st.session_state.role}"
)

# قوائم حسب الصلاحية
if st.session_state.role == "مدير عام":

    menu = [
        "الرئيسية",
        "المخزن",
        "العملاء",
        "الموردون",
        "المبيعات",
        "التقسيط",
        "التقارير",
        "المستخدمون"
    ]

elif st.session_state.role == "مدير":

    menu = [
        "الرئيسية",
        "المخزن",
        "العملاء",
        "المبيعات",
        "التقسيط",
        "التقارير"
    ]

else:

    menu = [
        "الرئيسية",
        "المخزن",
        "المبيعات"
    ]

page = st.sidebar.radio("اختر الصفحة", menu)

if st.sidebar.button("تسجيل الخروج"):

    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

    st.rerun()

# محتوى الصفحات
if page == "الرئيسية":

    st.title("🏪 معرض الكبير")

    st.info(
        "معرض الكبير للأجهزة الكهربائية وجهاز العروسة وكل ما يلزم البيت الحديث"
    )

    st.write("مرحباً بك داخل النظام")

elif page == "المخزن":

    st.header("📦 إدارة المخزن")

    st.write("سيتم ربط صفحة الأصناف هنا")

elif page == "العملاء":

    st.header("👥 العملاء")

elif page == "الموردون":

    st.header("🚚 الموردون")

elif page == "المبيعات":

    st.header("💰 المبيعات")

elif page == "التقسيط":

    st.header("📅 التقسيط")

elif page == "التقارير":

    st.header("📊 التقارير")

elif page == "المستخدمون":

    st.header("🔐 إدارة المستخدمين")
```

import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "database.db"

def get_connection():
return sqlite3.connect(DB_NAME)

st.title("📦 إدارة المخزن")

# إضافة صنف جديد

with st.expander("➕ إضافة صنف جديد"):

```
barcode = st.text_input("باركود الصنف")
item_name = st.text_input("اسم الصنف")
purchase_price = st.number_input("سعر الشراء", min_value=0.0)
sale_price = st.number_input("سعر البيع", min_value=0.0)
quantity = st.number_input("الكمية", min_value=0)

if st.button("حفظ الصنف"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO inventory
        (barcode,item_name,purchase_price,sale_price,quantity)
        VALUES (?,?,?,?,?)
    """,
    (
        barcode,
        item_name,
        purchase_price,
        sale_price,
        quantity
    ))

    conn.commit()
    conn.close()

    st.success("تم حفظ الصنف بنجاح")
```

# البحث

st.subheader("🔍 البحث عن صنف")

search = st.text_input("ابحث بالاسم أو الباركود")

conn = get_connection()

query = """
SELECT *
FROM inventory
"""

df = pd.read_sql(query, conn)

if search:

```
df = df[
    df["item_name"].astype(str).str.contains(search, case=False)
    |
    df["barcode"].astype(str).str.contains(search, case=False)
]
```

st.dataframe(df, use_container_width=True)

# إجمالي قيمة المخزون

if not df.empty:

```
total_inventory_value = (
    df["purchase_price"] * df["quantity"]
).sum()

st.metric(
    "إجمالي قيمة المخزون",
    f"{total_inventory_value:,.2f} جنيه"
)
```

# الأصناف قليلة الكمية

st.subheader("⚠️ أصناف تحتاج إعادة طلب")

low_stock = df[df["quantity"] <= 5]

if not low_stock.empty:

```
st.warning(
    f"يوجد {len(low_stock)} صنف يحتاج إعادة تموين"
)

st.dataframe(
    low_stock,
    use_container_width=True
)
```

# تعديل صنف

st.subheader("✏️ تعديل صنف")

if not df.empty:

```
selected_id = st.selectbox(
    "اختر الصنف",
    df["id"]
)

selected_row = df[df["id"] == selected_id].iloc[0]

new_name = st.text_input(
    "اسم الصنف الجديد",
    selected_row["item_name"]
)

new_purchase = st.number_input(
    "سعر الشراء الجديد",
    value=float(selected_row["purchase_price"])
)

new_sale = st.number_input(
    "سعر البيع الجديد",
    value=float(selected_row["sale_price"])
)

new_qty = st.number_input(
    "الكمية الجديدة",
    value=int(selected_row["quantity"])
)

if st.button("تحديث الصنف"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE inventory
    SET item_name=?,
        purchase_price=?,
        sale_price=?,
        quantity=?
    WHERE id=?
    """,
    (
        new_name,
        new_purchase,
        new_sale,
        new_qty,
        selected_id
    ))

    conn.commit()
    conn.close()

    st.success("تم التحديث بنجاح")
    st.rerun()
```

# حذف صنف

st.subheader("🗑️ حذف صنف")

if not df.empty:

```
delete_id = st.selectbox(
    "اختر الصنف للحذف",
    df["id"],
    key="delete_item"
)

if st.button("حذف الصنف"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM inventory WHERE id=?",
        (delete_id,)
    )

    conn.commit()
    conn.close()

    st.success("تم حذف الصنف")
    st.rerun()
```

conn.close()

cursor.execute("""
CREATE TABLE IF NOT EXISTS installment_payments (
id INTEGER PRIMARY KEY AUTOINCREMENT,
installment_detail_id INTEGER,
amount_paid REAL,
payment_date TEXT,
collected_by TEXT
)
""")

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

DB_NAME = "database.db"

def get_connection():
return sqlite3.connect(DB_NAME)

st.title("📅 إدارة التقسيط")

conn = get_connection()

customers = pd.read_sql(
"SELECT * FROM customers",
conn
)

inventory = pd.read_sql(
"SELECT * FROM inventory",
conn
)

tab1, tab2, tab3 = st.tabs([
"➕ عقد تقسيط جديد",
"💵 سداد قسط",
"📋 متابعة العقود"
])

# ==================================

# عقد جديد

# ==================================

with tab1:

```
st.subheader("إنشاء عقد تقسيط جديد")

customer_name = st.text_input("اسم العميل")

phone = st.text_input("رقم الهاتف")

national_id = st.text_input("الرقم القومي")

address = st.text_area("العنوان")

guarantor = st.text_input("اسم الضامن")

guarantor_phone = st.text_input("هاتف الضامن")

item = st.selectbox(
    "الصنف",
    inventory["item_name"]
)

item_row = inventory[
    inventory["item_name"] == item
].iloc[0]

item_price = float(item_row["sale_price"])

st.info(f"سعر البيع: {item_price:,.2f} جنيه")

down_payment = st.number_input(
    "المقدم",
    min_value=0.0
)

months = st.number_input(
    "عدد الأشهر",
    min_value=1,
    max_value=60,
    value=12
)

remaining = item_price - down_payment

monthly_installment = remaining / months

st.success(
    f"القسط الشهري = {monthly_installment:,.2f} جنيه"
)

if st.button("حفظ عقد التقسيط"):

    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO customers
    (name,phone,national_id,address,
     guarantor_name,guarantor_phone)
    VALUES (?,?,?,?,?,?)
    """,
    (
        customer_name,
        phone,
        national_id,
        address,
        guarantor,
        guarantor_phone
    ))

    customer_id = cursor.lastrowid

    invoice_no = (
        "INS-" +
        datetime.now().strftime("%Y%m%d%H%M%S")
    )

    cursor.execute("""
    INSERT INTO installments
    (
        customer_id,
        invoice_no,
        item_name,
        total_price,
        down_payment,
        remaining_amount,
        months,
        monthly_installment,
        start_date,
        status
    )
    VALUES (?,?,?,?,?,?,?,?,?,?)
    """,
    (
        customer_id,
        invoice_no,
        item,
        item_price,
        down_payment,
        remaining,
        months,
        monthly_installment,
        datetime.now().strftime("%Y-%m-%d"),
        "نشط"
    ))

    installment_id = cursor.lastrowid

    for i in range(months):

        due_date = (
            datetime.now()
            + relativedelta(months=i+1)
        ).strftime("%Y-%m-%d")

        cursor.execute("""
        INSERT INTO installment_details
        (
            installment_id,
            due_date,
            amount
        )
        VALUES (?,?,?)
        """,
        (
            installment_id,
            due_date,
            monthly_installment
        ))

    conn.commit()

    st.success("تم إنشاء عقد التقسيط")
```

# ==================================

# سداد قسط

# ==================================

with tab2:

```
contracts = pd.read_sql("""
SELECT
installments.id,
customers.name,
installments.invoice_no
FROM installments
INNER JOIN customers
ON customers.id =
installments.customer_id
""", conn)

if not contracts.empty:

    contract = st.selectbox(
        "اختر العقد",
        contracts["invoice_no"]
    )

    contract_id = contracts[
        contracts["invoice_no"] == contract
    ]["id"].iloc[0]

    installments_due = pd.read_sql(f"""
    SELECT *
    FROM installment_details
    WHERE installment_id={contract_id}
    AND paid=0
    """, conn)

    st.dataframe(installments_due)
```

# ==================================

# متابعة العقود

# ==================================

with tab3:

```
contracts_report = pd.read_sql("""
SELECT
installments.invoice_no,
customers.name,
installments.item_name,
installments.remaining_amount,
installments.monthly_installment,
installments.status
FROM installments
INNER JOIN customers
ON customers.id =
installments.customer_id
""", conn)

st.dataframe(
    contracts_report,
    use_container_width=True
)
```

conn.close()

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoices (
id INTEGER PRIMARY KEY AUTOINCREMENT,
invoice_no TEXT UNIQUE,
customer_name TEXT,
customer_phone TEXT,
total_amount REAL,
discount REAL,
net_amount REAL,
profit REAL,
sale_type TEXT,
created_by TEXT,
sale_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS invoice_items (
id INTEGER PRIMARY KEY AUTOINCREMENT,
invoice_no TEXT,
barcode TEXT,
item_name TEXT,
quantity INTEGER,
purchase_price REAL,
sale_price REAL,
total REAL
)
""")

ALTER TABLE inventory
ADD COLUMN brand TEXT;

ALTER TABLE inventory
ADD COLUMN model TEXT;

ALTER TABLE inventory
ADD COLUMN serial_number TEXT;

ALTER TABLE inventory
ADD COLUMN warranty_months INTEGER;

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "database.db"

def get_connection():
return sqlite3.connect(DB_NAME)

st.title("📊 لوحة تحكم معرض الكبير")

conn = get_connection()

# ======================

# مبيعات اليوم

# ======================

today = datetime.now().strftime("%Y-%m-%d")

sales_today = pd.read_sql(f"""
SELECT IFNULL(SUM(net_amount),0) total
FROM invoices
WHERE sale_date LIKE '{today}%'
""", conn)

today_sales = float(sales_today.iloc[0]["total"])

# ======================

# أرباح اليوم

# ======================

profit_today = pd.read_sql(f"""
SELECT IFNULL(SUM(profit),0) total
FROM invoices
WHERE sale_date LIKE '{today}%'
""", conn)

today_profit = float(profit_today.iloc[0]["total"])

# ======================

# عدد الفواتير

# ======================

invoice_count = pd.read_sql(f"""
SELECT COUNT(*) total
FROM invoices
WHERE sale_date LIKE '{today}%'
""", conn)

today_invoices = int(invoice_count.iloc[0]["total"])

# ======================

# إجمالي قيمة المخزون

# ======================

inventory = pd.read_sql("""
SELECT *
FROM inventory
""", conn)

inventory_value = (
inventory["purchase_price"] *
inventory["quantity"]
).sum()

# ======================

# بطاقات المؤشرات

# ======================

c1,c2,c3,c4 = st.columns(4)

c1.metric(
"💰 مبيعات اليوم",
f"{today_sales:,.0f} ج"
)

c2.metric(
"📈 أرباح اليوم",
f"{today_profit:,.0f} ج"
)

c3.metric(
"🧾 عدد الفواتير",
today_invoices
)

c4.metric(
"📦 قيمة المخزون",
f"{inventory_value:,.0f} ج"
)

# ======================

# الأصناف قليلة الكمية

# ======================

st.subheader("⚠️ أصناف تحتاج إعادة طلب")

low_stock = inventory[
inventory["quantity"] <= 5
]

if not low_stock.empty:
st.dataframe(
low_stock[
[
"barcode",
"item_name",
"quantity"
]
],
use_container_width=True
)
else:
st.success("لا توجد أصناف ناقصة")

# ======================

# أفضل المنتجات مبيعاً

# ======================

st.subheader("🏆 أفضل المنتجات مبيعاً")

best_products = pd.read_sql("""
SELECT
item_name,
SUM(quantity) total_qty
FROM invoice_items
GROUP BY item_name
ORDER BY total_qty DESC
LIMIT 10
""", conn)

if not best_products.empty:
st.dataframe(
best_products,
use_container_width=True
)

# ======================

# الأقساط المتأخرة

# ======================

st.subheader("🚨 الأقساط المتأخرة")

late_installments = pd.read_sql("""
SELECT
customers.name,
installment_details.due_date,
installment_details.amount
FROM installment_details
INNER JOIN installments
ON installments.id =
installment_details.installment_id

INNER JOIN customers
ON customers.id =
installments.customer_id

WHERE paid = 0
""", conn)

if not late_installments.empty:
st.dataframe(
late_installments,
use_container_width=True
)

conn.close()
