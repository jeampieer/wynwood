# WH Booking · Prueba Técnica

Proyecto Django para el flujo completo de reserva de una propiedad en Wynwood House.

## Incluye

- Home page responsive inspirada en el Figma de WH.
- Buscador por ciudad, fechas y huéspedes.
- Resultados con filtros, cards y panel visual tipo mapa.
- Detalle de propiedad con galería, amenities y formulario de disponibilidad.
- Checkout con registro manual, email único y validadores de contraseña.
- Pago simulado, reserva confirmada y correo de confirmación.
- Admin para ciudades, propiedades, imágenes, servicios, reservas y pagos.
- Optimización automática de imágenes a WebP con máximo 1200px.
- Seed de datos demo.
- Endpoints DRF ligeros para propiedades y reservas del usuario.

## Stack

- Python 3.11+
- Django 5.2
- PostgreSQL como base principal
- SQLite como fallback para revisión rápida
- Bootstrap 5 + DTL
- Pillow para optimización de imágenes

## Instalación

```bash
cd /Users/jeamp/Documents/Proyectos/Wynwood
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cp .env.example .env
```

## Configuración PostgreSQL

Edita `.env`:

```bash
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=wynwood
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=reservas@wynwood-house.test
```

Crea la base de datos:

```bash
createdb wynwood
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

## Fallback SQLite

Para revisar sin configurar PostgreSQL, usa:

```bash
DB_ENGINE=django.db.backends.sqlite3 DB_NAME=db.sqlite3 python manage.py migrate
DB_ENGINE=django.db.backends.sqlite3 DB_NAME=db.sqlite3 python manage.py seed_demo_data
DB_ENGINE=django.db.backends.sqlite3 DB_NAME=db.sqlite3 python manage.py runserver
```

## Flujo De Prueba

1. Abre `http://127.0.0.1:8000/`.
2. Busca una ciudad, fechas futuras y huéspedes.
3. Entra al detalle de una propiedad.
4. Selecciona fechas disponibles.
5. Completa checkout con un correo nuevo y una contraseña segura.
6. Confirma el pago simulado.
7. Revisa la pantalla de confirmación y el correo en consola.

## Endpoints

- `GET /properties/api/properties/`
- `GET /properties/api/properties/<slug>/`
- `GET /api/my-bookings/` requiere sesión/auth DRF
- `GET /api/my-bookings/<id>/` requiere sesión/auth DRF

## Tests

```bash
pytest -q
```

Cobertura funcional actual:

- Validaciones de fechas, capacidad y solapamiento de reservas.
- Cálculo de totales.
- Conversión de imágenes a WebP.
- Home, búsqueda, detalle, checkout y email.
- Rechazo de email duplicado.

## Notas De Diseño

El Figma/prototipo fue accesible desde navegador. La implementación replica sus señales principales: logo Wynwood, promo bar celeste, hero fotográfico, titular condensado, buscador horizontal, resultados con cards y detalle/checkout con resumen lateral.
