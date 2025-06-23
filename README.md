# Телеграм бот UARO
## **Шаблон .env**

    BOT_TOKEN=ТОКЕН_БОТА
    DATABASE_FILE=ШЛЯХ_ДО_ФАЙЛУ

***Зауважте, без .env файлу бот не буде запускатись, тому не забудьте створити і заповнити його по зразу перед запуском***
***DATABASE_FILE=Data.db - Цей рядок обов'язково має бути написаний з вказанням Data.db, можливість зміни БД залишена для відладки та швидкої підміни БД
Якщо не вказана Data.db, не буде працювати автостворення та ініціалізація БД***

## **Встановлення залежностей**
```bash
pip3 install -r requirements.txt
touch .env # Створюємо .env файл
nano/vim/mousepad .env # Редагуємо .env файл
```
## **Запуск**

```bash
python3 main.py
```

## Створення сервісу в Linux
✅ 1. Скопіювати/створити файл **_uaro-bot.service_** 📄

```bash
[Unit]
Description=UARO Telegram Bot
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/uaro.bot
ExecStart=/usr/local/bin/python3.10 /var/www/uaro.bot/main.py
Restart=always
RestartSec=5
StandardOutput=file:/var/log/uaro-bot.log
StandardError=file:/var/log/uaro-bot.err.log

[Install]
WantedBy=multi-user.target

```
**Пояснення:**
- **User=www-data** — користувач, під яким запуститься процес (зміни на свого, якщо треба).
- **ExecStart** — шлях до Python 3.10 і до main.py.
- **WorkingDirectory** — каталог з ботом.
- **Restart=always** — авто-рестарт при краші.
- **StandardOutput/StandardError** — вивід у лог-файли.

✅ 2. Дозвіл на виконання та перезапуск systemd
```bash
cp service/uaro-bot.service /etc/systemd/system/uaro-bot.service
sudo chown -R www-data:www-data /var/www/uaro.bot
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
```
✅ 3. Увімкнути та запустити сервіс
```bash
sudo systemctl enable uaro-bot.service
sudo systemctl start uaro-bot.service
```
🔍 4. Перевірити статус
```bash
sudo systemctl status uaro-bot.service
```
📝 5. Перегляд логів
```bash
--Перевірка логів
tail -f /var/log/uaro-bot.log
або
sudo journalctl -u uaro-bot.service -f
```

⛔ 6. Зупинити або перезапустити сервіс
```bash
sudo systemctl stop uaro-bot.service
sudo systemctl restart uaro-bot.service
```

 # Development Road
 ● Ядро(Структура БД,SQLite Адаптер, API, Logging) ⚠️
 ● Антифлуд ⚠️
 ● Система автомодерації ❌
 ● Інструменти адміністрації(mute,warn) ⚠️
 ● ISS моніторинг ⚠️
 ● Satelite моніторинг ❌
 ● solarvhf ✅
 ● solarpic ✅
 ● Система профілів ❌
 ● Форумні фічі(подяки, репутація і т.п.) ❌
 ● Система підтвердження кваліфікації(Тести на категорії) ❌
 
