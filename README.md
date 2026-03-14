# 🕊️ IPL-CR | Índice de Paz Legislativa de Costa Rica

Aplicación web para la codificación colaborativa de proyectos de ley según el Índice de Paz Legislativa (IPL-CR) 2010-2024.

## 📋 Características

- ✅ Formulario completo con los 23 indicadores (PN1-PN9, PP10-PP23)
- ✅ Cálculo automático de puntuaciones y clasificación
- ✅ Base de datos persistente en sesión
- ✅ Dashboard con visualizaciones
- ✅ Exportación a Excel (formato idéntico al template original)
- ✅ Sistema de backup/importación en JSON
- ✅ Filtros y búsqueda de proyectos
- ✅ Edición y eliminación de registros

## 🚀 Cómo usar

### Opción 1: Usar en línea (Streamlit Cloud) - GRATIS

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Despliega esta app
4. ¡Listo! Comparte la URL con tus colegas

### Opción 2: Usar localmente en tu computadora

1. **Instalar Python** (versión 3.8 o superior) desde [python.org](https://python.org)

2. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**:
   ```bash
   streamlit run app_ipl_cr.py
   ```

4. **Abrir en navegador**: La app se abrirá automáticamente en `http://localhost:8501`

## 📊 Estructura de la App

### Páginas disponibles:

1. **📋 Nuevo Proyecto**: Formulario de codificación con:
   - Información general (título, expediente, año, etc.)
   - 9 indicadores de Paz Negativa (sección roja)
   - 14 indicadores de Paz Positiva (sección verde)
   - Cálculo en tiempo real de totales y clasificación

2. **📊 Ver Proyectos**: 
   - Tabla completa de proyectos registrados
   - Filtros por año, tipo de paz y búsqueda por texto
   - Opciones para editar o eliminar proyectos

3. **📈 Dashboard**:
   - Métricas generales (promedios, totales)
   - Gráficos de distribución por tipo de paz
   - Evolución temporal por año
   - Análisis por indicador
   - Scatter plot PN vs PP

4. **💾 Exportar Datos**:
   - Descarga en formato Excel (.xlsx) - compatible con tu template original
   - Backup en JSON para seguridad
   - Importación de datos previos

## 🎯 Metodología de Codificación

### Escala de puntuación:
- **0** = No aparece
- **1** = Aparece indirectamente / Mención general
- **2** = Aparece explícitamente con mecanismos concretos

### Clasificación automática:
- **Negativa**: PN ≥ 67% y PP < 34%
- **Positiva**: PP ≥ 67% y PN < 34%
- **Mixta**: Ambos ≥ 34%
- **Baja incidencia**: Ambos < 34%

## 💡 Tips de uso

1. **Trabajo colaborativo**: Cada persona puede codificar en su propia sesión y luego combinar los archivos Excel.

2. **Backup frecuente**: Descarga el JSON regularmente como copia de seguridad.

3. **Edición**: Para editar un proyecto, anota su ID, ve a "Ver Proyectos", ingresa el ID y haz clic en "Cargar para editar", luego ve a "Nuevo Proyecto" donde se cargarán los datos.

4. **Pre-codificación**: Si tienes muchos proyectos, considera hacer una pre-codificación automática con procesamiento de texto (¡pregúntame cómo!)

## 🔒 Nota importante

Los datos se almacenan temporalmente en la sesión del navegador. **Recuerda exportar tu trabajo antes de cerrar la pestaña** para no perder los datos.

Para persistencia permanente, usa la opción de Streamlit Cloud o guarda los backups JSON regularmente.

## 📚 Referencias teóricas

- Johan Galtung: Paz negativa y paz positiva
- Institute for Economics & Peace: Positive Peace Framework
- Asamblea Legislativa de Costa Rica: Proyectos de ley 2010-2024

---

**Desarrollado para investigación académica** | 2024
