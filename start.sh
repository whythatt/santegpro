#!/bin/bash
echo "========================================"
echo "   СанТехПро - Запуск сервера"
echo "========================================"
echo ""
echo "1. Создание базы данных..."
python database.py
echo ""
echo "2. Запуск API сервера..."
echo "Сервер запущен на http://localhost:8000"
echo "Нажмите Ctrl+C для остановки"
echo ""
python api.py