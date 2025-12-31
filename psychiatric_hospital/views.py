# psychiatric_hospital/views.py
from django.shortcuts import render
from django.http import HttpResponse

def home_page(request):
    """Простая домашняя страница"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Психиатрическая клиника</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                text-align: center;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
            }
            .links {
                margin-top: 30px;
            }
            .links a {
                display: inline-block;
                margin: 10px;
                padding: 12px 24px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }
            .links a:hover {
                background-color: #45a049;
            }
            .links a.admin {
                background-color: #2196F3;
            }
            .links a.admin:hover {
                background-color: #1976D2;
            }
            .message {
                background-color: #e8f5e9;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                color: #2e7d32;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Добро пожаловать в систему психиатрической клиники</h1>
            
            <div class="message">
                <p>Система успешно запущена и работает!</p>
                <p>Вы можете перейти в административную панель для управления данными.</p>
            </div>
            
            <div class="links">
                <a href="/admin/" class="admin">Войти в админ-панель</a>
                <a href="/admin/logout/">Выйти</a>
            </div>
            
            <div style="margin-top: 40px; color: #666; font-size: 14px;">
                <p>Разработка и тестирование системы</p>
                <p>Django 6.0 | Python 3.13</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)