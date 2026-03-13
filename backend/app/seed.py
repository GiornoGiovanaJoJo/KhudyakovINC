"""
Скрипт инициализации БД и заполнения демо-данными.
Запуск: python -m app.seed
"""
import asyncio
from app.database import engine, Base, async_session
from app.models import TeamMember, Service, PortfolioProject


async def seed():
    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # ── Команда ───────────────────────────────────
        team = [
            TeamMember(
                name="Сергеева Полина Дмитриевна",
                position="Multimedia Designer",
                stack="Figma, Adobe Illustrator, Adobe Photoshop, Procreate, After Effects, SketchUp, Cinema 4D, TwinMotion, Tilda, Artivive",
                description=(
                    "Студентка РГХПУ им. С.Г. Строганова (2021–2025), кафедра «Дизайн среды», "
                    "профиль «Мультимедиа-дизайн». Специализируется на мультимедийном дизайне, "
                    "3D-визуализации и дополненной реальности."
                ),
                photo_url="/images/team/polina.jpg",
                order=1,
            ),
            TeamMember(
                name="Сурков Даниил Георгиевич",
                position="Frontend Developer (Vue / React / TypeScript)",
                stack="JavaScript, TypeScript, Python, Nuxt 3, React, Pinia, Tailwind, Ant Design, Vuetify, Webpack, REST API, Git, Vite, FastAPI, Django",
                description=(
                    "Frontend-разработчик с более чем 2-летним коммерческим опытом (общий стаж 5+ лет). "
                    "Специализируется на архитектуре клиентской части, интеграции с REST API. "
                    "Опыт работы в ООО «Центр энергетической сертификации» и Xoxlov Store."
                ),
                photo_url="",
                order=2,
            ),
            TeamMember(
                name="Худяков Даниил Владиславович",
                position="Python Developer",
                stack="Python 3.11, Django 5, FastAPI, PostgreSQL 16, Redis 7, Docker, GitLab CI/CD, Celery 5.3, SAP, Technical SEO, JavaScript, React Native, Node.js, MongoDB, SQLite, MySQL, Selenium, Pytest, Pandas, REST/JSON/SOAP API",
                description=(
                    "Python-разработчик с опытом построения микросервисной архитектуры. "
                    "Работал в ООО РЕ-СПО, где перевел легаси PHP систему на Python (Django REST + FastAPI), "
                    "увеличив скорость API на 42%. Выпускник МИРЭА (2024)."
                ),
                photo_url="",
                order=3,
            ),
        ]
        db.add_all(team)

        # ── Услуги ────────────────────────────────────
        services = [
            Service(
                title="Веб-разработка",
                description="Создание современных веб-приложений и сайтов любой сложности: от лендингов до крупных SaaS-продуктов.",
                icon="🌐",
                order=1,
            ),
            Service(
                title="Мобильная разработка",
                description="Разработка кроссплатформенных мобильных приложений на React Native и Flutter.",
                icon="📱",
                order=2,
            ),
            Service(
                title="UI/UX Дизайн",
                description="Проектирование пользовательских интерфейсов, прототипирование, создание дизайн-систем.",
                icon="🎨",
                order=3,
            ),
            Service(
                title="DevOps & Инфраструктура",
                description="Настройка CI/CD, контейнеризация, мониторинг, облачная инфраструктура (AWS, Yandex Cloud).",
                icon="⚙️",
                order=4,
            ),
            Service(
                title="Интеграция ИИ",
                description="Внедрение чат-ботов, рекомендательных систем и решений на основе машинного обучения.",
                icon="🤖",
                order=5,
            ),
            Service(
                title="IT-консалтинг",
                description="Аудит IT-инфраструктуры, выбор технологий, планирование архитектуры, оптимизация процессов.",
                icon="💼",
                order=6,
            ),
        ]
        db.add_all(services)

        # ── Портфолио ─────────────────────────────────
        portfolio = [
            PortfolioProject(
                title="E-Commerce платформа",
                short_description="Интернет-магазин с каталогом 10 000+ товаров, онлайн-оплатой и личным кабинетом.",
                full_description=(
                    "Полнофункциональная e-commerce платформа для розничной компании. "
                    "Каталог с фильтрацией и поиском, корзина, интеграция с платёжными системами (ЮKassa, СБП), "
                    "личный кабинет пользователя, панель администратора, аналитика продаж. "
                    "Стек: Nuxt 3, FastAPI, PostgreSQL, Redis, Docker."
                ),
                image_url="/images/portfolio/ecommerce.jpg",
                slug="ecommerce-platform",
                tags="Vue, Nuxt, FastAPI, PostgreSQL",
                order=1,
            ),
            PortfolioProject(
                title="CRM для логистической компании",
                short_description="Система управления заявками, отслеживания грузов и аналитики в реальном времени.",
                full_description=(
                    "CRM-система для автоматизации логистических процессов. "
                    "Управление заявками, отслеживание грузов на карте, расчёт маршрутов, "
                    "интеграция с 1С и транспортными API, дашборды с real-time аналитикой. "
                    "Стек: React, Node.js, PostgreSQL, WebSocket, Docker."
                ),
                image_url="/images/portfolio/crm.jpg",
                slug="logistics-crm",
                tags="React, Node.js, PostgreSQL, WebSocket",
                order=2,
            ),
            PortfolioProject(
                title="Мобильное приложение доставки",
                short_description="Кроссплатформенное приложение с трекингом курьера и push-уведомлениями.",
                full_description=(
                    "Мобильное приложение для сервиса доставки еды. "
                    "Два приложения: для клиентов и курьеров. Каталог ресторанов, "
                    "корзина, отслеживание курьера в реальном времени, push-уведомления, "
                    "история заказов, рейтинги и отзывы. "
                    "Стек: React Native, FastAPI, PostgreSQL, Firebase."
                ),
                image_url="/images/portfolio/delivery.jpg",
                slug="delivery-app",
                tags="React Native, FastAPI, Firebase",
                order=3,
            ),
        ]
        db.add_all(portfolio)

        await db.commit()
        print("✅ База данных создана и заполнена демо-данными!")


if __name__ == "__main__":
    asyncio.run(seed())
