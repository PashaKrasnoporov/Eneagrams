# geo_logger.py
import httpx

GEO_API_URL = "https://ipapi.co/{ip}/json/"  # сервіс GeoIP


async def print_geo_for_ip(ip: str) -> None:
    """
    Отримує приблизне місцезнаходження за IP і виводить у консоль.
    Дані ніде не зберігаються.
    """

    # Для локальних запитів (127.x / 192.168.x / 10.x) підміняємо на твій зовнішній IP
    if ip.startswith(("127.", "192.168.", "10.")):
        ip = "176.98.28.116"

    try:
        async with httpx.AsyncClient(timeout=2.5) as client:
            r = await client.get(GEO_API_URL.format(ip=ip))
            data = r.json()
    except Exception as e:
        print(f"[GEO] Error fetching geo for {ip}: {e}")
        return

    country = data.get("country_name") or "Unknown country"
    city = data.get("city") or "Unknown city"
    lat = data.get("latitude")
    lon = data.get("longitude")

    line = f"[GEO] IP {ip}: {country}, {city}"
    if lat is not None and lon is not None:
        line += f" | coords: {lat}, {lon}"
        map_line = f"{lat}, {lon}"
        print(line)
        print(f"[GEO] copy to map: {map_line}")
    else:
        print(line)
