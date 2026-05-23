# 🇨🇴 Análisis de Mortalidad en Colombia — 2019

## 8.1 Introducción del proyecto

Esta aplicación web interactiva permite explorar y analizar los datos de mortalidad no fetal en Colombia correspondientes al año 2019, publicados por el DANE (Departamento Administrativo Nacional de Estadística). A través de visualizaciones dinámicas construidas con Streamlit y Plotly, el usuario puede identificar patrones de mortalidad por territorio, mes, causa, sexo y grupo de edad.

---

## 8.2 Objetivo

Analizar e interpretar los datos de mortalidad no fetal de Colombia para el año 2019, identificando las principales causas de muerte, las regiones con mayor incidencia, la distribución temporal y demográfica, y las ciudades con mayor índice de violencia por homicidios con armas de fuego.

---

## 8.3 Estructura del proyecto

```
mortalidad-colombia-2019/
├── main.py                  # Aplicación principal de Streamlit
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Documentación del proyecto
└── datos/
    ├── NoFetal2019.xlsx      # Datos de mortalidad no fetal DANE 2019
    ├── CodigosDeMuerte.xlsx  # Catálogo CIE-10 de causas de muerte
    └── Divipola.xlsx         # División Político-Administrativa de Colombia
```

---

## 8.4 Requisitos

Instalar las dependencias con:

```bash
pip install -r requirements.txt
```

Librerías utilizadas:

```
streamlit==1.35.0
pandas==2.2.2
plotly==5.22.0
openpyxl==3.1.2
requests==2.31.0
```

Para ejecutar localmente:

```bash
streamlit run main.py
```

---

## 8.5 Despliegue en Azure App Service

1. Crear un recurso **App Service** en el portal de Azure con runtime Python 3.11.
2. Crear un archivo `startup.sh` en la raíz del proyecto con el siguiente contenido:
   ```bash
   python -m streamlit run main.py --server.port 8000 --server.address 0.0.0.0
   ```
3. En la configuración del App Service → **Configuración general**, establecer el comando de inicio:
   ```
   bash startup.sh
   ```
4. Subir el proyecto usando **GitHub Actions** o mediante el CLI de Azure:
   ```bash
   az webapp up --name <nombre-app> --resource-group <grupo> --runtime "PYTHON:3.11"
   ```
5. Verificar que la URL pública del App Service responde correctamente.

---

## 8.6 Software utilizado

- **Python 3.11** — Lenguaje de programación principal
- **Streamlit** — Framework para construir la aplicación web
- **Plotly** — Librería de visualizaciones interactivas
- **Pandas** — Manipulación y análisis de datos
- **Visual Studio Code** — Editor de código
- **GitHub** — Control de versiones y repositorio del proyecto
- **Azure App Service** — Plataforma de despliegue en la nube

---

## 8.7 Visualizaciones e interpretación de resultados

### 🗺️ Mapa — Distribución de muertes por departamento
Muestra la concentración geográfica de muertes en Colombia. Los departamentos con mayor actividad económica y poblacional como Bogotá D.C., Antioquia y Valle del Cauca registran el mayor número de defunciones, lo cual es consistente con su densidad poblacional.

### 📈 Gráfico de líneas — Muertes por mes
Permite identificar variaciones estacionales en la mortalidad. Se observan picos en ciertos meses que pueden estar relacionados con temporadas de enfermedades respiratorias o eventos climáticos.

### 🔫 Gráfico de barras — 5 ciudades más violentas
Usando los registros con código CIE-10 X95 (agresión con disparo de arma de fuego), se identifican los municipios con mayor número de homicidios por esta causa. Ciudades como Medellín, Cali y Bogotá suelen encabezar esta lista.

### 🥧 Gráfico circular — 10 municipios con menor mortalidad
Muestra los municipios con menor número de defunciones registradas en 2019, reflejando zonas con baja densidad poblacional o mejor acceso a servicios de salud.

### 📋 Tabla — Top 10 causas de muerte
Las principales causas de muerte en Colombia en 2019 están lideradas por enfermedades cardiovasculares (I219 — Infarto agudo de miocardio) y enfermedades respiratorias crónicas, lo que señala la importancia de las enfermedades no transmisibles como principal carga de mortalidad en el país.

### ⚥ Barras apiladas — Muertes por sexo y departamento
La comparación por sexo evidencia que en la mayoría de los departamentos la mortalidad masculina supera a la femenina, diferencia más pronunciada en departamentos con altos índices de violencia.

### 👶👴 Histograma — Distribución por grupo de edad
La mayoría de las muertes se concentran en los grupos de vejez (65 años en adelante), lo cual es esperado en una distribución de mortalidad adulta. Sin embargo, se observan cifras relevantes en mortalidad neonatal e infantil que representan una alerta en salud pública.

---

*Fuente de datos: DANE — Estadísticas Vitales EEVV 2019*
*https://microdatos.dane.gov.co/index.php/catalog/696*
