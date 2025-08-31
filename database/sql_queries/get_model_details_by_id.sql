WITH ModelComponentsCTE AS (
    SELECT
        mcl.model_id,
        string_agg(c.model_name_ukr, '/' ORDER BY c_type.type_name_ukr) AS "component_names"
    FROM
        conditioners.model_components_link AS mcl
    LEFT JOIN
        conditioners.components AS c ON mcl.component_id = c.component_id
    LEFT JOIN
        conditioners.component_types AS c_type ON c.component_type_id = c_type.component_type_id
    GROUP BY
        mcl.model_id
),
TechnicalDataCTE AS (
    SELECT
        cm.model_id,
        ra.area_sq_m AS "recommended_area",
        MAX(pv_comp.value) FILTER (WHERE pt_comp.parameter_name_ukr = 'Тип компресора за методом управління') AS "compressor_type_method",
        MAX(pv_comp.value) FILTER (WHERE pt_comp.parameter_name_ukr = 'Виробник компресора') AS "compressor_manufacturer",
        MAX(ct.type_name_ukr) AS "installation_type",
        MAX(ps.min_voltage) AS "min_voltage",
        MAX(ps.max_voltage) AS "max_voltage",
        MAX(power_comp_type.type_name_ukr) AS "power_source_location",
        MAX(tr_cool.min_temp) AS "outdoor_cooling_min_temp",
        MAX(tr_cool.max_temp) AS "outdoor_cooling_max_temp",
        MAX(tr_heat.min_temp) AS "outdoor_heating_min_temp",
        MAX(tr_heat.max_temp) AS "outdoor_heating_max_temp",
        MAX(CASE WHEN ft.type_name_ukr = 'Додаткові' AND func.function_name_ukr = 'WI-FI керування' THEN 'Опціонально (додатковий модуль)' ELSE NULL END) AS "wifi_control",
        MAX(p.program_name_ukr) AS "program_name"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.recommended_areas AS ra ON cm.recommended_area_id = ra.area_id
    LEFT JOIN
        conditioners.model_parameters_link AS mpl_comp ON cm.model_id = mpl_comp.model_id
    LEFT JOIN
        conditioners.parameter_values AS pv_comp ON mpl_comp.parameter_value_id = pv_comp.value_id
    LEFT JOIN
        conditioners.parameter_types AS pt_comp ON pv_comp.parameter_type_id = pt_comp.parameter_type_id
    LEFT JOIN
        conditioners.conditioner_types AS ct ON cm.conditioner_type_id = ct.conditioner_type_id
    LEFT JOIN
        conditioners.model_power_connections AS mpc ON cm.model_id = mpc.model_id
    LEFT JOIN
        conditioners.component_types AS power_comp_type ON mpc.power_component_type_id = power_comp_type.component_type_id
    LEFT JOIN
        conditioners.power_sources AS ps ON cm.power_source_id = ps.power_source_id
    LEFT JOIN
        conditioners.model_temp_range_link AS mtrl_cool ON cm.model_id = mtrl_cool.model_id
    LEFT JOIN
        conditioners.temperature_ranges AS tr_cool ON mtrl_cool.temp_range_id = tr_cool.temp_range_id
    LEFT JOIN
        conditioners.operation_modes AS om_cool ON tr_cool.mode_id = om_cool.mode_id AND om_cool.mode_name_ukr = 'Охолодження'
    LEFT JOIN
        conditioners.model_temp_range_link AS mtrl_heat ON cm.model_id = mtrl_heat.model_id
    LEFT JOIN
        conditioners.temperature_ranges AS tr_heat ON mtrl_heat.temp_range_id = tr_heat.temp_range_id
    LEFT JOIN
        conditioners.operation_modes AS om_heat ON tr_heat.mode_id = om_heat.mode_id AND om_heat.mode_name_ukr = 'Обігрів'
    LEFT JOIN
        conditioners.model_functions_link AS mfl_func ON cm.model_id = mfl_func.model_id
    LEFT JOIN
        conditioners.functions AS func ON mfl_func.function_id = func.function_id
    LEFT JOIN
        conditioners.function_types AS ft ON func.function_type_id = ft.function_type_id
    LEFT JOIN
        conditioners.model_programs_link AS mpl_prog ON cm.model_id = mpl_prog.model_id
    LEFT JOIN
        conditioners.programs AS p ON mpl_prog.program_id = p.program_id
    WHERE cm.model_id = $1
    GROUP BY
        cm.model_id, ps.min_voltage, ps.max_voltage, ra.area_sq_m
)
SELECT
    CONCAT_WS(' ', b.brand_name, s.series_name_ukr, mc.component_names) AS "Модель",
    CONCAT('до ', td."recommended_area") AS "Рекомендована пл. прим., кв.м",
    td.compressor_type_method AS "Тип компресора",
    td.compressor_manufacturer AS "Компресор",
    td.installation_type AS "Встановлення",
    CONCAT(td.min_voltage, '-', td.max_voltage) AS "Електроживлення, В",
    td.power_source_location AS "Джерело живлення",
    CONCAT('Охолодження від ', td.outdoor_cooling_min_temp, '°С до ', td.outdoor_cooling_max_temp, '°С',
           '/Обігрів від ', td.outdoor_heating_min_temp, '°С до ', td.outdoor_heating_max_temp, '°С') AS "Робочий діапазон температур, °С",
    string_agg(DISTINCT om.mode_name_ukr, '/') AS "Режими роботи",
    td.wifi_control AS "WI-FI керування",
    td.program_name AS "Програма"
FROM
    conditioners.conditioner_models AS cm
LEFT JOIN
    product_metadata.brands AS b ON cm.brand_id = b.brand_id
LEFT JOIN
    product_metadata.brand_series AS s ON cm.series_id = s.series_id
LEFT JOIN
    ModelComponentsCTE AS mc ON cm.model_id = mc.model_id
LEFT JOIN
    conditioners.model_operation_modes AS mom ON cm.model_id = mom.model_id
LEFT JOIN
    conditioners.operation_modes AS om ON mom.mode_id = om.mode_id
LEFT JOIN
    TechnicalDataCTE AS td ON cm.model_id = td.model_id
WHERE
    cm.model_id = $1
GROUP BY
    b.brand_name,
    s.series_name_ukr,
    mc.component_names,
    td."recommended_area",
    td.compressor_type_method,
    td.compressor_manufacturer,
    td.installation_type,
    td.min_voltage,
    td.max_voltage,
    td.power_source_location,
    td.outdoor_cooling_min_temp,
    td.outdoor_cooling_max_temp,
    td.outdoor_heating_min_temp,
    td.outdoor_heating_max_temp,
    td.wifi_control,
    td.program_name;
