# WH Booking · Prueba Técnica Wynwood

Aplicación Django para revisar el flujo de reserva de una propiedad: home, búsqueda, resultados, detalle, servicios adicionales, checkout, mock de pago, confirmación y APIs DRF.

## Stack

- Python 3.11+
- Django 5.2
- Django REST Framework
- SQLite para revisión local rápida
- PostgreSQL soportado vía `.env`
- Pillow para optimización de imágenes WebP
- Pytest para pruebas

## Instalación

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
Copy-Item .env.example .env
```

### Git Bash o shells Unix

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements/dev.txt
cp .env.example .env
```

## Configuración local con SQLite

`.env.example` ya viene configurado para SQLite. Con esa configuración:

```bash
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` y prueba una reserva con fechas futuras. El seed carga propiedades, servicios, contenido administrable de la home e imágenes demo. También repara imágenes de propiedades si la base apunta a archivos que ya no existen en `media/`.

## Configuración con PostgreSQL

Edita `.env`:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=wynwood
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

Crea la base y ejecuta la preparacion:

```bash
createdb wynwood
python manage.py migrate
python manage.py seed_demo_data
```

## Variables de entorno

Variables principales:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
DATABASE_URL=
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=reservas@wynwood-house.test
```

## Despliegue en Railway

Para desplegar en Railway, prepara el repositorio con los siguientes archivos y ajustes:

- `requirements.txt` en la raíz del proyecto.
- `runtime.txt` con la versión de Python.
- `Procfile` para iniciar el servidor con `gunicorn`.
- Variables de entorno configuradas en Railway.

### Variables de entorno recomendadas

- `DJANGO_SETTINGS_MODULE=config.settings.base`
- `DEBUG=False`
- `SECRET_KEY=<tu-secret-key-segura>`
- `ALLOWED_HOSTS=<tu-app>.railway.app`
- `CSRF_TRUSTED_ORIGINS=https://<tu-app>.railway.app`
- `DATABASE_URL=${{Postgres.DATABASE_URL}}` si usas el plugin de Postgres de Railway
- `DB_ENGINE=django.db.backends.postgresql`
- `DB_NAME=<db-name>`
- `DB_USER=<db-user>`
- `DB_PASSWORD=<db-password>`
- `DB_HOST=<db-host>`
- `DB_PORT=<db-port>`
- `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
- `DEFAULT_FROM_EMAIL=reservas@wynwood-house.test`

Si usas `DATABASE_URL`, no necesitas definir `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` ni `DB_PORT`.

### Comandos de despliegue

En Railway, configura el pre-deploy command como:

```bash
python manage.py migrate && python manage.py collectstatic --noinput
```

Y configura el custom start command como:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

El comando de inicio debe arrancar el servidor web. No uses `collectstatic` como custom start command, porque el contenedor termina después de copiar estáticos y Railway responde 502 al no encontrar un proceso escuchando en el puerto.

### Nota sobre media

El almacenamiento de `media/` en Railway es efímero. Las imágenes de demo incluidas en el repositorio funcionarán, pero las subidas no se mantendrán entre reinicios o nuevos despliegues.

## Flujo de prueba

1. Entra a `http://127.0.0.1:8000/`.
2. Busca ciudad, fechas futuras y huéspedes.
3. Abre una propiedad, por ejemplo `/properties/modern-duplex-parque-virrey/`.
4. Selecciona fechas disponibles y continúa a servicios.
5. Agrega servicios opcionales o continúa al checkout.
6. Registra un correo nuevo en la vista de checkout, como indica el prototipo. No hay pantalla independiente de registro porque el alta manual está integrada antes de confirmar la reserva.
7. Confirma el mock de pago y revisa la confirmación.

## Registro y pago

El registro manual de un usuario nuevo ocurre dentro del checkout. Al enviar el formulario con un correo no existente se crea el usuario, se inicia sesión y se genera la reserva.

El pago es simulado para la prueba técnica: la UI lo presenta como un mock de pasarela, no procesa cargos reales ni llama a un proveedor externo. Al confirmar, la aplicación crea un `Payment` con estado `paid`, referencia interna `WH-*`, monto total de la reserva y envía el correo de confirmación.

Todas las imágenes subidas a propiedades se normalizan a WebP y se redimensionan con lado máximo de 1200 px, incluyendo archivos que ya llegan como `.webp`.

## Endpoints

Versionados recomendados:

- `GET /api/v1/properties/`
- `GET /api/v1/properties/<slug>/`
- `GET /api/v1/bookings/my-bookings/`
- `GET /api/v1/bookings/my-bookings/<id>/`

Rutas legacy mantenidas por compatibilidad:

- `GET /properties/api/properties/`
- `GET /properties/api/properties/<slug>/`
- `GET /api/my-bookings/`
- `GET /api/my-bookings/<id>/`

Las rutas de reservas requieren autenticación.

## Verificación

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py seed_demo_data
pytest -q
```

Health checks manuales:

- Home: `http://127.0.0.1:8000/`
- Resultados: `http://127.0.0.1:8000/properties/search/`
- Detalle demo: `http://127.0.0.1:8000/properties/modern-duplex-parque-virrey/`
- API propiedades: `http://127.0.0.1:8000/api/v1/properties/`

## Admin

```bash
python manage.py createsuperuser
```

Luego entra a `http://127.0.0.1:8000/admin/` para administrar ciudades, propiedades, imágenes, servicios, reservas, pagos y contenido de landing.
