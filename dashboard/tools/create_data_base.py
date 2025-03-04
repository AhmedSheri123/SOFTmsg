import psycopg2

def create_database(db_name, user, password, host='localhost', port='5432'):
    try:
        # الاتصال بخادم PostgreSQL
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        # إنشاء كائن cursor لتنفيذ الاستعلامات
        cursor = connection.cursor()
        
        # إنشاء قاعدة البيانات
        cursor.execute(f"CREATE DATABASE {db_name};")
        print(f"تم إنشاء قاعدة البيانات {db_name} بنجاح!")
        
        # إغلاق الاتصال الحالي
        cursor.close()
        connection.close()
        return True
    except Exception as error:
        print(f"حدث خطأ: {error}")
        return False
    finally:
        # اغلاق الاتصال
        if connection:
            cursor.close()
            connection.close()
            print("تم اغلاق الاتصال.")
        return False

