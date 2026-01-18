# 🎲 OpoSim - Simulador de Sorteos de Temas de Oposición

Aplicación web para calcular probabilidades y simular sorteos de temas en oposiciones españolas.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://simulador-oposiciones.streamlit.app)

## 📋 Descripción

OpoSim te ayuda a preparar tus oposiciones permitiéndote:

- **📊 Calcular probabilidades**: Conoce la probabilidad de que salga al menos un tema que hayas estudiado
- **🎯 Simular sorteos**: Practica con simulaciones realistas del sorteo de bolas
- **⏱️ Cronómetro integrado**: Controla tu tiempo de exposición
- **📁 Importar temarios**: Carga tu temario desde archivos Excel

## 🚀 Demo en vivo

Accede a la aplicación desplegada en: [simulador-oposiciones.streamlit.app](https://simulador-oposiciones.streamlit.app)

## 💻 Instalación local

### Requisitos previos

- Python 3.11 o superior

### Pasos

1. Clona el repositorio:
```bash
git clone https://github.com/franciscosanchezn/simulador-oposiciones.git
cd simulador-oposiciones
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
streamlit run src/app.py
```

4. Abre tu navegador en `http://localhost:8501`

## 📖 Uso

### Configuración del sorteo

1. **Total de temas**: Número total de temas del temario
2. **Bolas extraídas**: Número de bolas que se sacan en el sorteo
3. **Temas estudiados**: Cantidad de temas que has preparado

### Funcionalidades

- **Calculadora de probabilidades**: Calcula automáticamente la probabilidad de éxito
- **Simulador de sorteo**: Realiza simulaciones del sorteo con animación
- **Gestión de temas**: Marca los temas estudiados y visualiza cuáles salen en cada sorteo
- **Cronómetro**: Temporizador para practicar la exposición oral

## 📊 Fórmula matemática

La probabilidad de que al menos un tema estudiado salga en el sorteo se calcula usando:

$$P = 1 - \frac{\binom{N-E}{B}}{\binom{N}{B}}$$

Donde:
- **N**: Total de temas
- **E**: Temas estudiados
- **B**: Bolas extraídas

## 🛠️ Tecnologías

- [Streamlit](https://streamlit.io/) - Framework para aplicaciones web
- [Pandas](https://pandas.pydata.org/) - Manipulación de datos
- [Python](https://www.python.org/) - Lenguaje de programación

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

Desarrollado por [Francisco Sánchez](https://github.com/franciscosanchezn)
