# SystemUI-OSINT-Tester
Telegram-бот, собирающий и отображающий системную информацию (CPU, RAM, сеть, процессы и т.д.) в виде текста и визуальной блок-схемы.

# Основные функции
Сбор информации о системе (имя, ОС, процессор и т.д.)
Мониторинг CPU и памяти
Отображение сетевых интерфейсов и IP
Список активных процессов
Генерация визуальной блок-схемы (изображение)
Отправка данных через Telegram-бота

# Технологии
Python 3.10+
psutil — для сбора системной информации
Pillow (PIL) — для генерации изображений
pyTelegramBotAPI (telebot) — для работы с Telegram API
platform, socket, datetime — стандартные библиотеки

# Установка и запуск
# 1.1
  git clone https://github.com/y2jakemiami/SystemUI-OSINT-Tester.git
  cd SystemUI-OSINT-Tester
# 1.2
  Замените токен бота в main.py: TOKEN = 'ВАШ_ТОКЕН_ЗДЕСЬ'
# 1.3
  python main.py | grep "SysLog" (Если играетесь в консоли)
  python main.py (запуск в фоновом режиме)

# Связь
Telegram: @kml5y
Email: is.kamil567@mail.ru
GitHub: https://y2jakemiami.github.io/kamilsky.github.io


