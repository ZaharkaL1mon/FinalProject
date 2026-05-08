import sqlite3  # Исправленный импорт

def init_db():
    conn = sqlite3.connect('careers.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS careers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            skills TEXT,
            education TEXT,
            salary_range TEXT,
            growth TEXT,
            category TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            age TEXT,
            experience TEXT,
            interests TEXT,
            recommendations TEXT
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM careers")
    if cursor.fetchone()[0] == 0:
        demo_careers = [
            ("Программист",
             "Разработка ПО, веб‑приложений, мобильных приложений.",
             "логика, алгоритмы, языки программирования",
             "Высшее техн. или курсы",
             "80–300 тыс. руб.",
             "Быстрый рост, фриланс",
             "IT"),
            ("Графический дизайнер",
             "Создание визуальных концепций, логотипов, интерфейсов.",
             "креативность, чувство стиля, Adobe Photoshop",
             "Художественное образование или курсы",
             "50–150 тыс. руб.",
             "Рост в арт‑директоры",
             "Дизайн"),
            ("Маркетолог",
             "Продвижение товаров и услуг, анализ рынка.",
             "аналитика, коммуникация, креативность",
             "Высшее экономическое или курсы",
             "40–200 тыс. руб.",
             "Карьерный рост в топ‑менеджмент",
             "Маркетинг"),
            ("Инженер",
             "Проектирование и конструирование технических систем и устройств.",
             "технические знания, математика, физика, AutoCAD",
             "Высшее техническое",
             "60–250 тыс. руб.",
             "Рост до ведущего инженера или руководителя проектов",
             "Инженерия"),
            ("Авиаконструктор",
             "Разработка и проектирование летательных аппаратов.",
             "аэродинамика, материаловедение, CAD‑системы",
             "Высшее авиационное или техническое",
             "100–350 тыс. руб.",
             "Карьерный рост в ведущих авиационных компаниях",
             "Авиация"),
            ("Врач",
             "Диагностика, лечение и профилактика заболеваний.",
             "медицинские знания, анатомия, диагностика, эмпатия",
             "Высшее медицинское",
             "50–400 тыс. руб.",
             "Специализация, научная карьера, руководящие должности",
             "Медицина"),
            ("Учитель",
             "Обучение и воспитание учащихся разных возрастов.",
             "педагогика, предметные знания, коммуникация",
             "Высшее педагогическое",
             "30–120 тыс. руб.",
             "Рост до завуча, директора школы, методиста",
             "Образование"),
            ("Архитектор",
             "Проектирование зданий и сооружений, создание архитектурных решений.",
             "архитектура, черчение, AutoCAD, 3D‑моделирование",
             "Высшее архитектурное",
             "70–220 тыс. руб.",
             "Открытие собственной студии, работа в международных бюро",
             "Архитектура")
        ]
        cursor.executemany('''
            INSERT INTO careers (name, description, skills, education, salary_range, growth, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', demo_careers)
        print(f"✅ Добавлены {len(demo_careers)} демонстрационных профессий в пустую базу данных")

    conn.commit()
    conn.close()
    print("💾 База данных инициализирована успешно")

def get_careers():
    try:
        conn = sqlite3.connect('careers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM careers")
        careers = [row[0] for row in cursor.fetchall()]
        conn.close()
        return careers
    except Exception as e:
        print(f"❌ Ошибка при получении профессий: {e}")
        return []

def get_career(name):
    """Получает полную информацию о профессии по названию (с частичным совпадением)"""
    try:
        conn = sqlite3.connect('careers.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, description, skills, education, salary_range, growth, category FROM careers WHERE name LIKE ?",
            (f"%{name}%",)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                'название': row[0],
                'описание': row[1],
                'навыки': row[2],
                'образование': row[3],
                'зарплата': row[4],
                'перспективы': row[5],
                'категория': row[6]
            }
        else:
            print(f"⚠️ Профессия '{name}' не найдена в базе данных")
            return None
    except Exception as e:
        print(f"❌ Ошибка при поиске профессии: {e}")
        return None

def save_user(user_id, age, experience, interests, recommendations):
    """Сохраняет данные пользователя в БД"""
    try:
        conn = sqlite3.connect('careers.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, age, experience, interests, recommendations)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, age, experience, interests, recommendations))
        conn.commit()
        conn.close()
        print(f"✅ Пользователь {user_id} успешно сохранён в БД")
    except Exception as e:
        print(f"❌ Ошибка сохранения пользователя: {e}")

def get_recommendations(user_id):
    try:
        conn = sqlite3.connect('careers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT recommendations FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        else:
            print(f"⚠️ Рекомендации для пользователя {user_id} не найдены")
            return None
    except Exception as e:
        print(f"❌ Ошибка получения рекомендаций: {e}")
        return None

init_db()