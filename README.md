
## 🍽️ Scraper de Restaurantes de TripAdvisor con Selenium y BeautifulSoup
Este módulo forma parte de un pipeline de datos e Inteligencia Artificial diseñado para extraer, estructurar y limpiar información real sobre establecimientos gastronómicos en Tulum, México. La data obtenida se procesa y organiza en diccionarios estandarizados listos para alimentar modelos de lenguaje (LLMs) o estructuras de análisis de datos (Pandas DataFrames).

## ⚔️ La Batalla del Web Scraping: Desafíos y Soluciones
Extraer datos de plataformas globales como TripAdvisor no es una tarea lineal. A lo largo del desarrollo de este script, nos enfrentamos a fuertes mecanismos de seguridad y cambios dinámicos en la interfaz que requirieron reestructurar la estrategia de raspado varias veces.

A continuación se detallan los principales obstáculos y cómo los vencimos:

1. El Muro de Cloudflare (Sistemas Anti-Bot)
* El Problema: Al ejecutar Selenium en modo oculto (**--headless**), TripAdvisor bloqueaba la sesión inmediatamente a través de Cloudflare. El script devolvía el código HTML de la pantalla de verificación humana y el título de la página quedaba congelado en tripadvisor.com, impidiendo ver el contenido real del restaurante.

* La Solución: * Se desactivó temporalmente el modo headless para permitir que el navegador emulara un entorno con monitor real.

* Se inyectaron argumentos avanzados a las opciones de Chrome para camuflar la automatización (**--disable-blink-features=AutomationControlled, excludeSwitches**).

* Se implementó un comando CDP (**Page.addScriptToEvaluateOnNewDocument**) en caliente para borrar la huella digital del objeto **navigator.webdriver**.

* Se aumentó el tiempo de espera (**time.sleep(8)**) para permitir el handshake correcto de la página antes de capturar el árbol de elementos.

2. Redirección Involuntaria a URLs Individuales
* El Problema: Las búsquedas iniciales del agente automatizado redirigían el script hacia la página de un único restaurante específico (como Wild Tulum), lo que rompía la lógica del bucle que buscaba listar múltiples tarjetas de locales comerciales en una sola corrida.

* La Solución: Se interceptó el flujo inyectando manualmente la URL del listado general indexado de Tulum (**/Restaurants-g150813-...**), garantizando la presencia masiva de tarjetas en el HTML capturado.

3. Mutación de Clases CSS y Estructuras Dinámicas
* El Problema: Intentar capturar la información agrupando por "contenedores padre" tradicionales (divs con clases como **.card** o atributos **data-automation**) hacía que el script se clavara devolviendo **0 resultados**, ya que TripAdvisor ofusca y cambia el nombre de sus clases de diseño frecuentemente en producción.

* La Solución Estricta por Expresiones Regulares (Regex): Se migró a un filtro basado en patrones de texto que buscaran el formato de ranking clásico **(r"^\d+\.\s+[A-Za-z]")**.

* La Solución Definitiva por URLs Estructurales: Cuando TripAdvisor modificó también el renderizado de los números de ranking en pantalla, cambiamos la estrategia radicalmente hacia un enfoque inmune a cambios estéticos: indexar por patrones de URL internas. El script pasó a capturar todos los enlaces (etiqueta ancla) que apuntan de forma nativa a **/Restaurant_Review-**, asegurando el 100% de efectividad ya que la plataforma no puede alterar su arquitectura de enlaces profunda sin romper su propio sitio web.

## 📊 Estructura de Datos Final Extraída
Una vez superados los bloqueos y localizado el enlace de cada restaurante, el script navega horizontalmente por los elementos hermanos del DOM para poblar dinámicamente el siguiente esquema de diccionario para la lista **restaurantes_detalhados**:
````
Python
restaurante_info = {
    "Nombre": "Nombre Limpio extraído del enlace",
    "Calificacion": "Puntaje real extraído del componente SVG de burbujas",
    "Cantidad_Resenas": "Contador dinámico de opiniones (ej: 1,004 reviews)",
    "Tipo_Cocina": "Categoría gastronómica parseada de la tarjeta",
    "Rango_Precio": "Escala de precios detectada (ej: $$ - $$$)",
    "Estado_Funcionamiento": "Estado actual de apertura del local",
    "URL_Restaurante": "Enlace absoluto de TripAdvisor para análisis profundo",
    "URL_Imagen_Principal": "Enlace directo al CDN de la miniatura de la tarjeta"
}
````
## 🚀 Próximos Pasos en el Pipeline
Con la data real y dinámica corriendo fluidamente en la consola, este módulo queda listo para:

1- Serialización a DataFrames: Conversión directa a matrices tabulares mediante **pd.DataFrame(restaurantes_detalhados)** para auditoría o exportación a CSV/Excel.

2- Inyección en Contexto de Agentes: Formatear la lista en estructuras JSON nativas para transferir la data limpia a las ventanas de contexto de los LLMs.

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](https://github.com/cris959/orquestacion-agentes-multiagentes/blob/main/LICENSE) adjunto en este repositorio.

Copyright © 2026 [Christian Garay](https://github.com//cris959/orquestacion-agentes-multiagentes) - Backend Developer.