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
RATINGS_FILE = "ratings_data.csv"

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

# دالة مطورة واحترافية لتحويل الأ
