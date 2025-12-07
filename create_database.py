"""
📁 СКРИПТ ДЛЯ СОЗДАНИЯ БАЗЫ ДАННЫХ УТЕЧЕК
Преобразует текстовый файл с паролями в базу хешей для k-анонимности.
"""

import hashlib
import json
import os
from collections import defaultdict


def create_hash_database(input_file: str = "top_passwords.txt",
                         output_file: str = "leaks_database.json",
                         fake_counts: bool = True):
    """
    Создает базу данных хешей из текстового файла с паролями.

    Args:
        input_file: Файл с паролями (каждый пароль на новой строке)
        output_file: Файл для сохранения базы данных
        fake_counts: Генерировать ли фейковые количества утечек
    """

    print("=" * 60)
    print("СОЗДАНИЕ БАЗЫ ДАННЫХ УТЕЧЕК ДЛЯ K-АНОНИМНОСТИ")
    print("=" * 60)

    # Проверяем существование входного файла
    if not os.path.exists(input_file):
        print(f"❌ Файл {input_file} не найден.")
        print("Создайте файл top_passwords.txt с паролями (каждый на новой строке).")
        return

    # Читаем пароли из файла
    try:
        with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]

        print(f"✅ Прочитано {len(passwords)} паролей из {input_file}")

    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return

    # Создаем базу хешей
    database = defaultdict(list)

    for i, password in enumerate(passwords, 1):
        try:
            # Хешируем пароль
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().lower()

            # Разделяем на префикс и суффикс
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]

            # Генерируем фейковое количество утечек (для реалистичности)
            if fake_counts:
                # Основано на длине и сложности пароля
                if len(password) < 6:
                    count = 1000000  # Очень слабые пароли
                elif len(password) < 8:
                    count = 500000  # Слабые пароли
                elif password.isdigit():
                    count = 250000  # Только цифры
                elif password.isalpha():
                    count = 100000  # Только буквы
                else:
                    count = 50000  # Более сложные
            else:
                count = 1

            # Добавляем в базу
            database[prefix].append([suffix, count])

            # Прогресс
            if i % 100 == 0:
                print(f"  Обработано {i}/{len(passwords)} паролей...")

        except Exception as e:
            print(f"⚠ Ошибка обработки пароля '{password}': {e}")
            continue

    # Сохраняем в JSON файл
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dict(database), f, ensure_ascii=False, indent=2)

        print(f"\n✅ База данных создана успешно!")
        print(f"   Файл: {output_file}")
        print(f"   Префиксов: {len(database)}")

        # Подсчитываем общее количество записей
        total_entries = sum(len(items) for items in database.values())
        print(f"   Всего записей: {total_entries}")

        # Примеры из базы
        print(f"\n📊 Примеры префиксов в базе:")
        for i, (prefix, items) in enumerate(list(database.items())[:3]):
            print(f"   {prefix}: {len(items)} записей")

        print(f"\n💡 База готова к использованию в программе анализатора.")
        print("   Скопируйте файл в папку с основной программой.")

    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")

    print("=" * 60)


def add_passwords_to_existing_database(new_passwords_file: str,
                                       existing_database: str = "leaks_database.json"):
    """
    Добавляет новые пароли в существующую базу данных.
    """
    if not os.path.exists(existing_database):
        print(f"❌ Файл {existing_database} не найден.")
        return

    if not os.path.exists(new_passwords_file):
        print(f"❌ Файл {new_passwords_file} не найден.")
        return

    # Загружаем существующую базу
    with open(existing_database, 'r', encoding='utf-8') as f:
        database = json.load(f)

    # Читаем новые пароли
    with open(new_passwords_file, 'r', encoding='utf-8', errors='ignore') as f:
        new_passwords = [line.strip() for line in f if line.strip()]

    added_count = 0

    for password in new_passwords:
        try:
            sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().lower()
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]

            # Проверяем, есть ли уже такой суффикс
            if prefix in database:
                suffixes = [item[0] for item in database[prefix]]
                if suffix in suffixes:
                    continue  # Уже есть

            # Добавляем новую запись
            if prefix not in database:
                database[prefix] = []

            database[prefix].append([suffix, 1])  # count=1 для новых паролей
            added_count += 1

        except Exception:
            continue

    # Сохраняем обновленную базу
    with open(existing_database, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)

    print(f"✅ Добавлено {added_count} новых паролей в базу данных.")


if __name__ == "__main__":
    print("Выберите действие:")
    print("1. Создать новую базу данных из top_passwords.txt")
    print("2. Добавить пароли в существующую базу")

    choice = input("Ваш выбор (1-2): ").strip()

    if choice == "1":
        # Спрашиваем о фейковых счетчиках
        use_fake = input("Генерировать фейковые количества утечек? (да/нет): ").lower()
        fake_counts = use_fake in ['да', 'д', 'yes', 'y']

        create_hash_database(fake_counts=fake_counts)

    elif choice == "2":
        file_to_add = input("Введите имя файла с новыми паролями: ").strip()
        if not file_to_add:
            file_to_add = "new_passwords.txt"

        add_passwords_to_existing_database(file_to_add)

    else:
        print("❌ Неверный выбор.")

    input("\nНажмите Enter для выхода...")