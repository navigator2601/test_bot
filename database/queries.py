# database/queries.py

# Запит для отримання брендів, що мають моделі
GET_BRANDS_WITH_MODEL_COUNT = """
SELECT
    b.id AS brand_id,
    b.name AS brand_name,
    COUNT(m.id) AS model_count
FROM
    public.brands b
INNER JOIN
    public.models m ON b.id = m.brand_id
GROUP BY
    b.id, b.name
ORDER BY
    model_count DESC;
"""

# Запит для отримання типів кондиціонерів для вказаного бренду, що мають моделі
GET_TYPES_BY_BRAND_WITH_MODEL_COUNT = """
SELECT
    t.id AS type_id,
    t.name AS type_name,
    COUNT(m.id) AS model_count
FROM
    public.types t
INNER JOIN
    public.models m ON t.id = m.type_id
WHERE
    m.brand_id = $1
GROUP BY
    t.id, t.name
ORDER BY
    model_count DESC;
"""

# Запит для отримання моделей кондиціонерів за ID бренду та ID типу
GET_MODELS_BY_BRAND_AND_TYPE = """
SELECT
    m.id, -- Додано ідентифікатор моделі
    concat (LPAD(CAST(bp.value / 1000 AS TEXT), 2, '0'), t.abbreviation, ' (', b.name, ')') AS model_name,
    m.combined_model AS model_code
FROM
    public.models m
LEFT JOIN
    public.brands b ON b.id = m.brand_id
LEFT JOIN
    public.types t ON t.id = m.type_id
LEFT JOIN
    public.btu_powers bp ON bp.id = m.btu_power_id
WHERE
    m.brand_id = $1 AND m.type_id = $2
ORDER BY
    model_name;
"""

# Запит для отримання назви бренду за ID
GET_BRAND_BY_ID = """
SELECT name FROM public.brands WHERE id = $1;
"""

# Запит для отримання назви типу за ID
GET_TYPE_BY_ID = """
SELECT name FROM public.types WHERE id = $1;
"""

# Запит для отримання інформації про модель за ID
GET_MODEL_BY_ID = """
SELECT m.combined_model, b.name AS brand_name, t.abbreviation AS type_abbreviation, bp.value AS btu_value
FROM public.models m
LEFT JOIN public.brands b ON b.id = m.brand_id
LEFT JOIN public.types t ON t.id = m.type_id
LEFT JOIN public.btu_powers bp ON bp.id = m.btu_power_id
WHERE m.id = $1;
"""

# Запит для отримання розмірів внутрішнього блоку за ID моделі
GET_INDOOR_DIMENSIONS_BY_MODEL_ID = """
SELECT iud.lenght_mm, iud.depth_mm, iud.height_mm
FROM public.indoor_unit_dimensions iud
WHERE iud.model_id = $1;
"""