# Файл: database/db_search_functions.py
# Призначення: Функції для взаємодії з базою даних.

import asyncpg
from typing import List, Dict, Optional
from aiogram.utils.markdown import hbold, hcode

# Функції для пошуку та форматування даних з БД

async def get_brands_with_model_count(db_pool: asyncpg.Pool) -> List[Dict]:
    """
    Повертає список брендів з кількістю моделей для кожного.
    (Адаптовано під структуру вашої БД: conditioners.brands)
    """
    sql_query = """
    SELECT
        cb.brand_name AS "Бренд",
        COUNT(cm.model_id) AS "Кількість моделей"
    FROM
        conditioners.brands cb
    JOIN
        conditioners.conditioner_models cm ON cb.brand_id = cm.brand_id
    GROUP BY
        cb.brand_name
    ORDER BY
        cb.brand_name;
    """
    async with db_pool.acquire() as connection:
        records = await connection.fetch(sql_query)
        return [dict(record) for record in records]

async def get_models_by_brand(db_pool: asyncpg.Pool, brand_name: str) -> List[Dict]:
    """
    Повертає список моделей для заданого бренду.
    (Адаптовано під структуру вашої БД: conditioners.brands та conditioner_model_names)
    """
    sql_query = """
    SELECT
        cmn.model_name_ukr AS "Модель"
    FROM
        conditioners.conditioner_models cm
    JOIN
        conditioners.brands cb ON cm.brand_id = cb.brand_id
    JOIN
        conditioners.conditioner_model_names cmn ON cm.model_name_id = cmn.model_name_id
    WHERE
        cb.brand_name ILIKE $1
    ORDER BY
        cmn.model_name_ukr;
    """
    async with db_pool.acquire() as connection:
        records = await connection.fetch(sql_query, brand_name)
        return [dict(record) for record in records]

async def find_in_database(db_pool: asyncpg.Pool, query: str) -> List[Dict]:
    """
    Виконує пошук у базі даних за ключовим словом і повертає список моделей.
    (Адаптовано під структуру вашої БД)
    """
    try:
        sql_query = """
        SELECT
            cmn.model_name_ukr AS "Модель",
            ct.type_name_ukr AS "Тип кондиціонера",
            ws_cool.nominal_watt_value AS "Потужність охолодження, Вт",
            ws_heat.nominal_watt_value AS "Потужність обігріву, Вт",
            (rps.liquid_line_mm || 'мм/' || rps.gas_line_mm || 'мм') AS "Діаметр труб (р/г)",
            rt.type_name AS "Тип холодоагенту",
            rc.weight_kg AS "Вага холодоагенту, кг"
        FROM
            conditioners.conditioner_models cm
        LEFT JOIN
            conditioners.conditioner_model_names cmn ON cm.model_name_id = cmn.model_name_id
        LEFT JOIN
            conditioners.conditioner_types ct ON cm.conditioner_type_id = ct.conditioner_type_id
        LEFT JOIN
            conditioners.watt_specs ws_cool ON cm.cooling_watt_specs_id = ws_cool.watt_specs_id
        LEFT JOIN
            conditioners.watt_specs ws_heat ON cm.heating_watt_specs_id = ws_heat.watt_specs_id
        LEFT JOIN
            conditioners.refrigerant_pipe_specs rps ON cm.refrigerant_pipe_specs_id = rps.pipe_specs_id
        LEFT JOIN
            conditioners.refrigerant_types rt ON cm.refrigerant_type_id = rt.refrigerant_type_id
        LEFT JOIN
            conditioners.refrigerant_charges rc ON cm.refrigerant_charge_id = rc.charge_id
        WHERE
            cmn.model_name_ukr ILIKE $1
            OR ct.type_name_ukr ILIKE $1
            OR ws_cool.nominal_watt_value::text ILIKE $1
            OR ws_heat.nominal_watt_value::text ILIKE $1
            OR rt.type_name ILIKE $1
        ORDER BY
            cmn.model_name_ukr
        LIMIT 10;
        """
        async with db_pool.acquire() as connection:
            records = await connection.fetch(sql_query, f"%{query}%")
            return [dict(record) for record in records]
    except Exception as e:
        print(f"Помилка при виконанні пошуку: {e}")
        return []

def format_search_results(results: List[Dict]) -> str:
    """
    Форматує результати пошуку в читабельний рядок для виведення в Telegram.
    """
    if not results:
        return "Нічого не знайдено."
        
    formatted_text = ""
    for data in results:
        formatted_text += hbold(data.get("Модель", "N/A")) + "\n"
        for key, value in data.items():
            if key != "Модель" and value:
                formatted_text += f"{hbold(key)}: {hcode(str(value))}\n"
        formatted_text += "\n"
    return formatted_text

async def get_model_details_by_name(db_pool: asyncpg.Pool, model_name: str) -> Optional[Dict]:
    """
    Виконує точний пошук однієї моделі в базі даних та повертає її деталі, використовуючи повний SQL-запит.
    (Адаптовано під структуру вашої БД)
    Оновлено: додано JOIN для отримання назви бренду.
    """
    try:
        sql_query = """
        SELECT
            cb.brand_name AS "Бренд",
            cmn.model_name_ukr AS "Модель",
            ct.type_name_ukr AS "Тип кондиціонера",
            'Внутрішній блок' AS "Категорія_Внутрішній_блок",
            iu.unit_name AS "Внутрішній блок",
            'Електроживлення' AS "Категорія_Електроживлення",
            CONCAT_WS('/', vf.voltage_range, vf.phase, vf.frequency_hz) AS "Електроживлення В/Ф/Гц",
            'Охолодження' AS "Категорія_Охолодження",
            REPLACE(CONCAT(ws_cool.nominal_watt_value, '(', ws_cool.min_watt_value, '-', ws_cool.max_watt_value, ')'), '.', ',') AS "Потужність охолодження Вт",
            REPLACE(CONCAT(pcs_cool.nominal_consumption_watt, '(', pcs_cool.min_consumption_watt, '~', pcs_cool.max_consumption_watt, ')'), '.', ',') AS "Номінальна споживана потужність Вт",
            REPLACE(CONCAT(cs_cool.nominal_current_amp, '(', cs_cool.min_current_amp, '~', cs_cool.max_current_amp, ')'), '.', ',') AS "Номінальний струм А (Охолодження)",
            REPLACE(
                COALESCE(
                    TO_CHAR(ees_cool.seer, 'FM9999999.0'),
                    TO_CHAR(ees_cool.eer, 'FM9999999.0')
                ), '.', ','
            ) || '(' || REPLACE(cee_cool.class_name, 'A', 'А') || ')' AS "Енергоефективність SEER/EER (клас)",
            'Нагрівання' AS "Категорія_Нагрівання",
            REPLACE(CONCAT(ws_heat.nominal_watt_value, '(', ws_heat.min_watt_value, '-', ws_heat.max_watt_value, ')'), '.', ',') AS "Потужність обігріву Вт",
            REPLACE(CONCAT(pcs_heat.nominal_consumption_watt, '(', pcs_heat.min_consumption_watt, '~', pcs_heat.max_consumption_watt, ')'), '.', ',') AS "Номінальна споживана потужність Вт (Обігрів)",
            REPLACE(CONCAT(cs_heat.nominal_current_amp, '(', cs_heat.min_current_amp, '~', cs_heat.max_current_amp, ')'), '.', ',') AS "Номінальний струм А (Обігрів)",
            REPLACE(
                COALESCE(
                    TO_CHAR(ees_heat.scop, 'FM9999999.0'),
                    TO_CHAR(ees_heat.cop, 'FM9999999.0')
                ), '.', ','
            ) || '(' || REPLACE(cee_heat.class_name, 'A', 'А') || ')' AS "Енергоефективність SCOP/COP (клас)",
            REPLACE(CONCAT(avr.min_voltage, '~', avr.max_voltage), '.', ',') AS "Допустимий перепад напруги В",
            mes.max_power_consumption_watt AS "Максимальна споживана потужність Вт",
            TRIM(TRAILING '.000' FROM TO_CHAR(mes.max_current_amp, 'FM9999999.000')) AS "Максимальний споживний струм А",
            CONCAT_WS('/', iaf.high_cmh, iaf.medium_cmh, iaf.low_cmh) AS "Витрати повітря внутрішнього блоку (Hi/Mi/Lo) м3/год",
            REPLACE(CONCAT_WS('/', inl.high_db, inl.medium_db, inl.low_db, inl.sleep_db), '.', ',') AS "Рівень шуму внутрішнього блоку (Hi/Mi/Lo) дБ (A)",
            CONCAT_WS('x', iu_prop.length_mm, iu_prop.depth_mm, iu_prop.height_mm) AS "Розміри Внутрішнього блоку (Д*Г*В) мм",
            CONCAT_WS('x', iu_prop.packed_length_mm, iu_prop.packed_depth_mm, iu_prop.packed_height_mm) AS "Розміри Внутр. блоку в упаковці (Д*Г*В) мм",
            REPLACE(TRIM(TRAILING '.00' FROM TO_CHAR(iw.net_kg, 'FM9999999.00')) || '(' || TRIM(TRAILING '.00' FROM TO_CHAR(iw.gross_kg, 'FM9999999.00')) || ')', '.', ',') AS "Вага Внутрішнього блоку Нетто / Брутто кг",
            'Зовнішній блок' AS "Категорія_Зовнішній_блок",
            eu.unit_name AS "Зовнішній блок",
            oaf.volume_cmh AS "Витрати повітря зовнішнього блоку м3/год",
            TRIM(TRAILING '.0' FROM TO_CHAR(onl.db_value, 'FM9999999.0')) AS "Рівень шуму зовнішнього блоку дБ (A)",
            CONCAT_WS('x', ou_prop.length_mm, ou_prop.depth_mm, ou_prop.height_mm) AS "Розміри Зовнішнього блоку (Д*Г*В) мм",
            CONCAT_WS('x', ou_prop.packed_length_mm, ou_prop.packed_depth_mm, ou_prop.packed_height_mm) AS "Розміри Зовн. блоку в упаковці (Д*Г*В) мм",
            REPLACE(TRIM(TRAILING '.00' FROM TO_CHAR(ow.net_kg, 'FM9999999.00')) || '(' || TRIM(TRAILING '.00' FROM TO_CHAR(ow.gross_kg, 'FM9999999.00')) || ')', '.', ',') AS "Вага Зовнішнього блоку Нетто / Брутто кг",
            cm_m.manufacturer_name AS "Компресор",
            rt.type_name AS "Холодоагент Тип",
            REPLACE(TRIM(LEADING ' ' FROM TO_CHAR(rc.weight_kg, 'FM0.000')), '.', ',') AS "Вага холодоагенту кг",
            CONCAT_WS('/',
                REPLACE(TO_CHAR(rps.liquid_line_mm, 'FM9999999.00'), '.', ',') || 'mm(' ||
                    CASE
                        WHEN (rps.liquid_line_mm / 25.4)::numeric(5,2) = 0.25 THEN '1/4in'
                        WHEN (rps.liquid_line_mm / 25.4)::numeric(5,2) = 0.375 THEN '3/8in'
                        WHEN (rps.liquid_line_mm / 25.4)::numeric(5,2) = 0.50 THEN '1/2in'
                        WHEN (rps.liquid_line_mm / 25.4)::numeric(5,2) = 0.625 THEN '5/8in'
                        WHEN (rps.liquid_line_mm / 25.4)::numeric(5,2) = 0.75 THEN '3/4in'
                        WHEN (rps.gas_line_mm / 25.4)::numeric(5,2) = 0.875 THEN '7/8in'
                        ELSE REPLACE(TO_CHAR((rps.liquid_line_mm / 25.4)::numeric(5,2), 'FM9999999.00'), '.', ',') || 'in'
                    END || ')',
                REPLACE(TO_CHAR(rps.gas_line_mm, 'FM9999999.00'), '.', ',') || 'mm(' ||
                    CASE
                        WHEN (rps.gas_line_mm / 25.4)::numeric(5,2) = 0.25 THEN '1/4in'
                        WHEN (rps.gas_line_mm / 25.4)::numeric(5,2) = 0.375 THEN '3/8in'
                        WHEN (rps.gas_line_mm / 25.4)::numeric(5,2) = 0.50 THEN '1/2in'
                        WHEN (rps.gas_line_mm / 25.4)::numeric(5,2) = 0.625 THEN '5/8in'
                        WHEN (rps.gas_line_mm / 25.4)::numeric(5,2) = 0.75 THEN '3/4in'
                        WHEN (rps.gas_line_mm / 25.4)::numeric(5,2) = 0.875 THEN '7/8in'
                        ELSE REPLACE(TO_CHAR((rps.gas_line_mm / 25.4)::numeric(5,2), 'FM9999999.00'), '.', ',') || 'in'
                    END || ')'
            ) AS "Сполучні труби Рідина / Газ мм (дюйм)",
            pls.max_length_m AS "Максимальна довжина магістралі м",
            pls.max_height_diff_m AS "Максимальний перепад висот м",
            pls.min_length_m AS "Мінімальна довжина магістралі м",
            psl.location_name_ukr AS "Джерело живлення",
            REPLACE(REPLACE(pcs.power_cable_mm2, 'x', '×'), 'mm2', 'mm²') AS "Кабель живлення мм²",
            REPLACE(REPLACE(pcs.interconnect_cable_mm2, 'x', '×'), 'mm2', 'mm²') AS "Міжблочні з'єднання мм²",
            tsr.min_temp_celsius || '~' || tsr.max_temp_celsius AS "Діапазон встановлення температури °С",
            iort.cooling_min_celsius || '~' || iort.cooling_max_celsius || '/' || iort.heating_min_celsius || '~' || iort.heating_max_celsius AS "Діапазон робочих температур Внутрішній блок (охолодження / обігрів) °С",
            oort.cooling_min_celsius || '~' || oort.cooling_max_celsius || '/' || oort.heating_min_celsius || '~' || oort.heating_max_celsius AS "Діапазон робочих температур Зовнішній блок (охолодження / обігрів) °С"
        FROM
            conditioners.conditioner_models cm
        LEFT JOIN
            conditioners.brands cb ON cm.brand_id = cb.brand_id
        LEFT JOIN
            conditioners.conditioner_types ct ON cm.conditioner_type_id = ct.conditioner_type_id
        LEFT JOIN
            conditioners.internal_units iu ON cm.internal_unit_id = iu.internal_unit_id
        LEFT JOIN
            conditioners.external_units eu ON cm.external_unit_id = eu.external_unit_id
        LEFT JOIN
            conditioners.voltage_frequency_phases vf ON cm.indoor_power_supply_vfp_id = vf.vfp_id
        LEFT JOIN
            conditioners.conditioner_model_names cmn ON cm.model_name_id = cmn.model_name_id
        LEFT JOIN
            conditioners.watt_specs ws_cool ON cm.cooling_watt_specs_id = ws_cool.watt_specs_id
        LEFT JOIN
            conditioners.power_consumption_specs pcs_cool ON cm.cooling_power_consumption_specs_id = pcs_cool.power_consumption_specs_id
        LEFT JOIN
            conditioners.current_specs cs_cool ON cm.cooling_current_specs_id = cs_cool.current_specs_id
        LEFT JOIN
            conditioners.energy_efficiency_specs ees_cool ON cm.cooling_energy_efficiency_specs_id = ees_cool.energy_efficiency_specs_id
        LEFT JOIN
            conditioners.conditioner_energy_efficiency cee_cool ON ees_cool.energy_efficiency_class_id = cee_cool.energy_efficiency_id
        LEFT JOIN
            conditioners.watt_specs ws_heat ON cm.heating_watt_specs_id = ws_heat.watt_specs_id
        LEFT JOIN
            conditioners.power_consumption_specs pcs_heat ON cm.heating_power_consumption_specs_id = pcs_heat.power_consumption_specs_id
        LEFT JOIN
            conditioners.current_specs cs_heat ON cm.heating_current_specs_id = cs_heat.current_specs_id
        LEFT JOIN
            conditioners.energy_efficiency_specs ees_heat ON cm.heating_energy_efficiency_specs_id = ees_heat.energy_efficiency_specs_id
        LEFT JOIN
            conditioners.conditioner_energy_efficiency cee_heat ON ees_heat.energy_efficiency_class_id = cee_heat.energy_efficiency_id
        LEFT JOIN
            conditioners.allowed_voltage_ranges avr ON cm.allowed_voltage_range_id = avr.voltage_range_id
        LEFT JOIN
            conditioners.max_electrical_specs mes ON cm.max_electrical_specs_id = mes.max_electrical_specs_id
        LEFT JOIN
            conditioners.indoor_air_flow_specs iaf ON cm.indoor_air_flow_id = iaf.air_flow_id
        LEFT JOIN
            conditioners.outdoor_air_flow_specs oaf ON cm.outdoor_air_flow_id = oaf.air_flow_id
        LEFT JOIN
            conditioners.indoor_noise_levels inl ON cm.indoor_noise_level_id = inl.indoor_noise_level_id
        LEFT JOIN
            conditioners.outdoor_noise_levels onl ON cm.outdoor_noise_level_id = onl.outdoor_noise_level_id
        LEFT JOIN
            conditioners.unit_component_properties iu_prop ON cm.indoor_unit_properties_id = iu_prop.property_id
        LEFT JOIN
            conditioners.unit_component_properties ou_prop ON cm.outdoor_unit_properties_id = ou_prop.property_id
        LEFT JOIN
            conditioners.unit_weights iw ON cm.indoor_weight_id = iw.weight_id
        LEFT JOIN
            conditioners.unit_weights ow ON cm.outdoor_weight_id = ow.weight_id
        LEFT JOIN
            conditioners.compressor_manufacturers cm_m ON cm.compressor_manufacturer_id = cm_m.compressor_manufacturer_id
        LEFT JOIN
            conditioners.refrigerant_types rt ON cm.refrigerant_type_id = rt.refrigerant_type_id
        LEFT JOIN
            conditioners.refrigerant_charges rc ON cm.refrigerant_charge_id = rc.charge_id
        LEFT JOIN
            conditioners.refrigerant_pipe_specs rps ON cm.refrigerant_pipe_specs_id = rps.pipe_specs_id
        LEFT JOIN
            conditioners.pipe_length_specs pls ON cm.pipe_length_id = pls.pipe_length_id
        LEFT JOIN
            conditioners.power_supply_locations psl ON cm.primary_power_supply_location_id = psl.location_id
        LEFT JOIN
            conditioners.power_cables_specs pcs ON cm.power_cables_specs_id = pcs.cable_specs_id
        LEFT JOIN
            conditioners.temperature_setting_ranges tsr ON cm.temperature_setting_range_id = tsr.temp_setting_id
        LEFT JOIN
            conditioners.indoor_operating_temp_ranges iort ON cm.indoor_operating_temp_range_id = iort.op_temp_range_id
        LEFT JOIN
            conditioners.outdoor_operating_temp_ranges oort ON cm.outdoor_operating_temp_range_id = oort.op_temp_range_id
        WHERE
            LOWER(cmn.model_name_ukr) = LOWER($1)
        LIMIT 1;
        """
        async with db_pool.acquire() as connection:
            result = await connection.fetchrow(sql_query, model_name)
            return dict(result) if result else None
    except Exception as e:
        print(f"Помилка при отриманні деталей моделі '{model_name}': {e}")
        return None

def format_general_info(data: Dict) -> str:
    """Форматує загальну інформацію про модель."""
    # Ці поля беруться з основного запиту
    brand = data.get('Бренд', 'N/A')
    model = data.get('Модель', 'N/A')
    model_type = data.get('Тип кондиціонера', 'N/A')
    compressor = data.get('Компресор', 'N/A')
    return (
        f"{hbold('Основна інформація:')}\n\n"
        f"{hbold('Бренд:')} {hcode(brand)}\n"
        f"{hbold('Модель:')} {hcode(model)}\n"
        f"{hbold('Тип:')} {hcode(model_type)}\n"
        f"{hbold('Компресор:')} {hcode(compressor)}\n"
    )

def format_tech_info(data: Dict) -> str:
    """Форматує технічні параметри моделі."""
    cooling_power = data.get('Потужність охолодження Вт', 'N/A')
    heating_power = data.get('Потужність обігріву Вт', 'N/A')
    cooling_consumption = data.get('Номінальна споживана потужність Вт', 'N/A')
    heating_consumption = data.get('Номінальна споживана потужність Вт (Обігрів)', 'N/A')
    cooling_class = data.get('Енергоефективність SEER/EER (клас)', 'N/A')
    heating_class = data.get('Енергоефективність SCOP/COP (клас)', 'N/A')
    pipes = data.get('Сполучні труби Рідина / Газ мм (дюйм)', 'N/A')
    refrigerant = data.get('Холодоагент Тип', 'N/A')
    refrigerant_weight = data.get('Вага холодоагенту кг', 'N/A')
    return (
        f"{hbold('Технічні параметри:')}\n\n"
        f"{hbold('Охолодження (Вт):')} {hcode(str(cooling_power))}\n"
        f"{hbold('Обігрів (Вт):')} {hcode(str(heating_power))}\n"
        f"{hbold('Споживання (охол.):')} {hcode(str(cooling_consumption))}\n"
        f"{hbold('Споживання (обігр.):')} {hcode(str(heating_consumption))}\n"
        f"{hbold('Енергоефективність (охол.):')} {hcode(str(cooling_class))}\n"
        f"{hbold('Енергоефективність (обігр.):')} {hcode(str(heating_class))}\n"
        f"{hbold('Холодоагент:')} {hcode(str(refrigerant))} ({hcode(str(refrigerant_weight))})\n"
        f"{hbold('Сполучні труби:')} {hcode(str(pipes))}\n"
    )

def format_full_info(data: Dict) -> str:
    """
    Форматує повну інформацію про модель.
    Оновлено: Використовує hbold для заголовків та hcode для значень.
    Проблема з "Can't find end of the entity" може виникати через некоректні
    символи у значеннях, тому використання hcode є безпечним рішенням.
    """
    formatted_text = f"{hbold('Повна інформація про модель:')}\n\n"
    
    # Визначення порядку категорій
    category_order = [
        'Основна інформація',
        'Внутрішній блок',
        'Електроживлення',
        'Охолодження',
        'Нагрівання',
        'Зовнішній блок',
        'Інше' # Категорія для решти полів
    ]
    
    current_category = None
    
    # Виведення полів згідно з категоріями
    for key, value in data.items():
        if value is not None:
            if key.startswith('Категорія_'):
                category_name = value
                if current_category:
                    # Якщо це нова категорія, додаємо пробіл
                    formatted_text += "\n"
                formatted_text += hbold(f"{category_name}:") + "\n"
                current_category = category_name
            elif not key.startswith('Категорія_'):
                formatted_text += f"{hbold(key)}: {hcode(str(value))}\n"
    
    return formatted_text

def format_functions_info(data: Dict) -> str:
    # Заглушка, оскільки ця інформація потребує більш складних запитів.
    # TODO: доопрацювати, щоб отримувати дані з conditioners.conditioner_model_features
    return (
        f"{hbold('Додаткові функції:')}\n\n"
        f"На жаль, детальна інформація про функції для цієї моделі не завантажена."
    )