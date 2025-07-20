import psutil
import socket
import platform
from PIL import Image, ImageDraw, ImageFont
from telebot import *
from datetime import datetime

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

def get_system_info():
    uname = platform.uname()
    return {
        "system": uname.system,
        "node_name": uname.node,
        "release": uname.release,
        "version": str(uname.version)[:28],
        "machine": uname.machine,
        "processor": uname.processor
    }

def get_cpu_info():
    cpu_freq = psutil.cpu_freq()
    return {
        "cpu_count": psutil.cpu_count(logical=True),
        "cpu_usage": psutil.cpu_percent(interval=1),
        "cpu_freq_current": cpu_freq.current,
        "cpu_freq_min": cpu_freq.min,
        "cpu_freq_max": cpu_freq.max
    }

def get_memory_info():
    memory = psutil.virtual_memory()
    return {
        "total_memory": memory.total,
        "available_memory": memory.available,
        "used_memory": memory.used,
        "memory_percent": memory.percent
    }

def get_network_info():
    network_info = psutil.net_if_addrs()
    ip_addresses = {interface: [addr.address for addr in addresses if addr.family == socket.AF_INET] for interface, addresses in network_info.items()}
    return ip_addresses

def get_process_info():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes[:10]  # Ограничим количество процессов до 10

def create_flowchart(data):
    # Загрузка образца блок-схемы
    img = Image.open("template.png")
    draw = ImageDraw.Draw(img)

    # Установка шрифта (можно использовать стандартный шрифт)
    font = ImageFont.truetype("arialmt.ttf")

    # Параметры для размещения текста в блоках
    x_offsets = [50, 350, 650]  # Смещения по оси X для трех колонок
    y_offset = 50   # Начальное смещение по оси Y

    # Заполнение первой колонки (Системная информация)
    draw.text((x_offsets[0], y_offset), "Системная информация:", fill="white", font=font)
    y_offset += 20
    for key, value in data.items():
        if key in ["system", "node_name", "release","machine", "processor", "version"]:
            draw.text((x_offsets[0], y_offset), f"{key.capitalize()}: {value}", fill="black", font=font)
            y_offset += 20

    # Сброс смещения по Y для второй колонки
    y_offset = 50

    # Заполнение второй колонки (Информация о ЦПУ и памяти)
    draw.text((x_offsets[1], y_offset), "Информация о ЦПУ:", fill="white", font=font)
    y_offset += 20
    for key, value in data.items():
        if key in ["cpu_count", "cpu_usage", "cpu_freq_current", "cpu_freq_min", "cpu_freq_max"]:
            draw.text((x_offsets[1], y_offset), f"{key.replace('_', ' ').capitalize()}: {value}", fill="black", font=font)
            y_offset += 20

    draw.text((x_offsets[1], y_offset + 20), "Информация о памяти:", fill="white", font=font)
    y_offset += 40
    for key, value in data.items():
        if key in ["total_memory", "available_memory", "used_memory", "memory_percent"]:
            draw.text((x_offsets[1], y_offset), f"{key.replace('_', ' ').capitalize()}: {value / (1024 ** 2):.2f} MB" if 'memory' in key else f"{key.replace('_', ' ').capitalize()}: {value}", fill="black", font=font)
            y_offset += 20

    # Сброс смещения по Y для третьей колонки
    y_offset = 50

    # Заполнение третьей колонки (Информация о сети и процессах)
    draw.text((x_offsets[2], y_offset), "Информация о сети:", fill="black", font=font)
    y_offset += 20
    for interface, addresses in data['network'].items():
        draw.text((x_offsets[2], y_offset), f"{interface}: {', '.join(addresses)}", fill="black", font=font)
        y_offset += 20

    draw.text((x_offsets[2], y_offset + 20), "Процессы:", fill="white", font=font)
    y_offset += 40
    for proc in data['processes']:
        draw.text((x_offsets[2], y_offset),
                  f"{proc['pid']}: {proc['name']} | CPU: {proc['cpu_percent']}% | Память: {proc['memory_info']} MB",
                  fill="black", font=font)
        y_offset += 20

    cur = datetime.now()

    draw.text((750, 600), f"{cur}", fill="black", font=font)

    # Сохранение результата
    img.save("flowchart_output.png")


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Запустить тест 💽"), types.KeyboardButton("Завершить ❌"))
    bot.send_message(message.chat.id, f"Обнаружено устройство {str(get_system_info())[35:58]}", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "Запустить тест 💽")
def tester(message):
    bot.send_message(message.chat.id, "Запрашиваю системную информацию 💽 ...")

    sys_info = get_system_info()
    cpu_info = get_cpu_info()
    mem_info = get_memory_info()
    net_info = get_network_info()
    processes = get_process_info()

    data = {
        **sys_info,
        **cpu_info,
        **mem_info,
        "network": net_info,
        "processes": processes
    }

    # Создание блок-схемы
    create_flowchart(data)

    # Отправка текстовой информации пользователю
    report_message = (
            "=== Системная информация ===\n" +
            "\n".join([f"{key.capitalize()}: {value}" for key, value in sys_info.items()]) +
            "\n\n=== Информация о ЦПУ =⚙️=\n" +
            "\n".join([f"{key.replace('_', ' ').capitalize()}: {value}" for key, value in cpu_info.items()]) +
            "\n\n=== Информация о памяти =💾=\n" +
            "\n".join([
                f"{key.replace('_', ' ').capitalize()}: {value / (1024 ** 2):.2f} MB" if 'memory' in key else f"{key.replace('_', ' ').capitalize()}: {value}"
                for key, value in mem_info.items()]) +
            "\n\n=== Информация о сети =📡=\n" +
            "\n".join([f"{interface}: {', '.join(addresses)}" for interface, addresses in net_info.items()]) +
            "\n\n=== Процессы =🎛=\n" +
            "\n".join([
                f"{proc['pid']}: {proc['name']} | CPU: {proc['cpu_percent']}% | Память: {proc['memory_info']} MB"
                for proc in processes])
    )
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Запустить тест 💽"), types.KeyboardButton("Завершить ❌"))

    # Отправка текстового отчета
    bot.send_message(message.chat.id, report_message, reply_markup=keyboard)

    # Отправка изображения блок-схемы
    with open("flowchart_output.png", 'rb') as photo:
        bot.send_photo(message.chat.id, photo)

@bot.message_handler(func=lambda message: message.text == "Завершить ❌")
def stoper(message):
    cur = datetime.now()
    bot.send_message(message.chat.id, f'Bot was terminated at {cur} 🔒')
    bot.stop_bot()
    return

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
