import asyncio
import os
from app.database import async_session
from app.models import TeamMember

async def populate_extracted_data():
    async with async_session() as db:
        # Extracted data from resumes
        new_members = [
            TeamMember(
                name="Сергеева Полина Дмитриевна",
                position="Multimedia Designer",
                stack="Figma, Adobe Illustrator, Adobe Photoshop, Procreate, After Effects, SketchUp, Cinema 4D, TwinMotion, Tilda, Artivive",
                description=(
                    "Студентка РГХПУ им. С.Г. Строганова (2021–2025), кафедра «Дизайн среды», "
                    "профиль «Мультимедиа-дизайн». Окончила подготовительные курсы академии Строганова "
                    "и Детскую художественную школу им. Репина. Специализируется на мультимедийном дизайне, "
                    "3D-визуализации и дополненной реальности."
                ),
                photo_url="", # Will be filled if images are available
                order=4,
            ),
            TeamMember(
                name="Сурков Даниил Георгиевич",
                position="Frontend Developer (Vue / React / TypeScript)",
                stack="JavaScript, TypeScript, Python, Nuxt 3, React, Pinia, Tailwind, Ant Design, Vuetify, Webpack, REST API, Git, Vite, FastAPI, Django",
                description=(
                    "Frontend-разработчик с более чем 2-летним коммерческим опытом (общий стаж 5+ лет). "
                    "Специализируется на архитектуре клиентской части, интеграции с REST API. "
                    "Опыт работы в ООО «Центр энергетической сертификации» (рефакторинг легаси, автоматизация документооборота) "
                    "и Xoxlov Store (разработка интернет-магазина на Nuxt 3). Выпускник университета «Дубна»."
                ),
                photo_url="",
                order=5,
            ),
            TeamMember(
                name="Худяков Даниил Владиславович",
                position="Python Developer",
                stack="Python 3.11, Django 5, FastAPI, PostgreSQL 16, Redis 7, Docker, GitLab CI/CD, Celery 5.3, SAP, Technical SEO, JavaScript, React Native, Node.js, MongoDB, SQLite, MySQL, Selenium, Pytest, Pandas, REST/JSON/SOAP API",
                description=(
                    "Python-разработчик с опытом построения микросервисной архитектуры. "
                    "Работал в ООО РЕ-СПО, где перевел легаси PHP систему на Python (Django REST + FastAPI), "
                    "увеличив скорость API на 42%. Имеет опыт разработки ботов, парсеров и систем мониторинга цен. "
                    "Выпускник МИРЭА (2024)."
                ),
                photo_url="",
                order=6,
            )
        ]
        
        db.add_all(new_members)
        await db.commit()
        print(f"✅ Успешно добавлено {len(new_members)} новых сотрудников в базу данных!")

if __name__ == "__main__":
    asyncio.run(populate_extracted_data())
