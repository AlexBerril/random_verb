# Telegram Verb Lesson Bot
Этот Telegram-бот помогает в изучении неправильных глаголов в английском языке. Бот выдает задания на перевод глаголов, проверяет ответы и управляет уроком.

## Функциональность

- **/start**: Начинает урок, выдает глаголы для перевода в случайном порядке.
- **/stop**: Заканчивает урок и отправляет сообщение "ты молодец".
- Ответы на задания должны быть введены через пробел, например: `do did done`.
- Неправильные ответы повторяются после окончания всех заданий.

Добавьте ваш Telegram токен в код. Найдите строку `TOKEN = '???` в файле `main.py`.


## Пример использования

1. Отправьте команду `/start` в чат с ботом, чтобы начать урок.
2. Бот выдает задания на перевод. Ответьте на них, введя формы глагола через пробел.
3. После окончания урока, отправьте команду `/stop`, чтобы завершить урок и получить сообщение "ты молодец".
