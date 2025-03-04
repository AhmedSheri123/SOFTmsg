import psycopg2

def create_database(db_name, user, password, host='localhost', port='5432'):
    connection = None
    cursor = None

    try:
        # الاتصال بخادم PostgreSQL مع قاعدة بيانات موجودة مسبقًا
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database="postgres"  # الاتصال بقاعدة postgres الافتراضية
        )
        
        # ✅ تفعيل autocommit لمنع تشغيل CREATE DATABASE داخل معاملة
        connection.autocommit = True

        # إنشاء كائن cursor لتنفيذ الاستعلامات
        cursor = connection.cursor()
        
        # التحقق مما إذا كانت قاعدة البيانات موجودة مسبقًا
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name};")
            print(f"✅ تم إنشاء قاعدة البيانات '{db_name}' بنجاح!")
        else:
            print(f"⚠ قاعدة البيانات '{db_name}' موجودة بالفعل.")

        return True

    except Exception as error:
        print(f"❌ حدث خطأ: {error}")
        return False

    finally:
        # إغلاق الاتصال بأمان إذا كان مفتوحًا
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
            print("🔒 تم إغلاق الاتصال.")

