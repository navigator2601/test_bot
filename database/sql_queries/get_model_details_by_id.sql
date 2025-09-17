WITH DimensionsCTE AS (
    SELECT
        mdl.model_id,
        csd.component_type_id,
        dt.type_name_ukr,
        pt.parameter_name_ukr,
        csd.value_mm
    FROM
        conditioners.model_dimensions_link AS mdl
    LEFT JOIN
        conditioners.component_specific_dimensions AS csd ON mdl.dimension_id = csd.specific_dimension_id
    LEFT JOIN
        conditioners.dimension_types AS dt ON csd.dimension_type_id = dt.dimension_type_id
    LEFT JOIN
        conditioners.parameter_types AS pt ON mdl.parameter_type_id = pt.parameter_type_id
    WHERE
        mdl.model_id = 1
),
AirFlowAndNoiseCTE AS (
    SELECT
        cm.model_id,
        MAX(CONCAT(CONCAT_WS('/', afr.hi_value, afr.mi_value, afr.lo_value), ' (Hi/Mi/Lo) ', uom_afr.short_name_ukr)) FILTER (WHERE pt_afr.parameter_name_ukr = 'Витрати повітря' AND afr.component_type_id = 1) AS "air_flow_internal",
        MAX(CONCAT(CONCAT_WS('/', afr.hi_value, afr.mi_value, afr.lo_value, afr.sl_value), ' (Hi/Mi/Lo/Sl) ', uom_afr.short_name_ukr)) FILTER (WHERE pt_afr.parameter_name_ukr = 'Рівень шуму' AND afr.component_type_id = 1) AS "noise_level_internal",
        MAX(CONCAT(afr.hi_value, ' ', uom_afr.short_name_ukr)) FILTER (WHERE pt_afr.parameter_name_ukr = 'Витрати повітря' AND afr.component_type_id = 2) AS "air_flow_external",
        MAX(CONCAT(afr.hi_value, ' ', uom_afr.short_name_ukr)) FILTER (WHERE pt_afr.parameter_name_ukr = 'Рівень шуму' AND afr.component_type_id = 2) AS "noise_level_external"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.model_air_flow_and_noise_link AS mafl ON cm.model_id = mafl.model_id
    LEFT JOIN
        conditioners.air_flow_and_noise_ratings AS afr ON mafl.rating_id = afr.rating_id
    LEFT JOIN
        conditioners.parameter_types AS pt_afr ON afr.parameter_type_id = pt_afr.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_afr ON pt_afr.unit_id = uom_afr.unit_id
    WHERE
        cm.model_id = $1
    GROUP BY cm.model_id
),
TechnicalParametersCTE AS (
    SELECT
        cm.model_id,
        MAX(pv_comp.value) FILTER (WHERE pt_comp.parameter_name_ukr = 'Тип компресора за методом управління') AS "Тип компр за методом управління",
        MAX(pv_comp.value) FILTER (WHERE pt_comp.parameter_name_ukr = 'Тип компресора за принципом роботи') AS "Тип компр за принципом роботи",
        MAX(pv_comp.value) FILTER (WHERE pt_comp.parameter_name_ukr = 'Виробник компресора') AS "compressor_manufacturer",
        MAX(pv_comp.value) FILTER (WHERE pt_comp.parameter_name_ukr = 'Тип мастила') AS "oil_type",
        MAX(CONCAT(pv_comp.value, ' ', uom_pv.short_name_ukr)) FILTER (WHERE pt_comp.parameter_name_ukr = 'Обсяг мастила') AS "oil_volume",
        MAX(r.refrigerant_name) AS "refrigerant_name",
        MAX(CONCAT(cm.refrigerant_charge_value, ' ', uom_charge.short_name_ukr)) AS "refrigerant_charge",
        MAX(CONCAT(cp.discharge_pressure_mpa, '/', cp.suction_pressure_mpa, ' ', uom_press.short_name_ukr)) AS "pressure_range",
        string_agg(DISTINCT CONCAT(pd.diameter_mm, '(', pd.diameter_inch_ukr, ')'), '/') FILTER (WHERE pt_pipes.parameter_name_ukr IN ('Діаметр труби рідинна', 'Діаметр труби газова')) AS "pipe_diameters",
        MAX(CONCAT(pd.diameter_mm, ' (', pd.diameter_inch_ukr, ')') ) FILTER (WHERE pt_pipes.parameter_name_ukr = 'Діаметр дренажної труби') AS "drain_pipe_diameter",
        MAX(pip.parameter_value) FILTER (WHERE pt_inst.parameter_name_ukr = 'Мінімальна довжина магістралі') AS "min_length",
        MAX(pip.parameter_value) FILTER (WHERE pt_inst.parameter_name_ukr = 'Максимальна довжина магістралі') AS "max_length",
        MAX(uom_inst.short_name_ukr) FILTER (WHERE pt_inst.parameter_name_ukr = 'Мінімальна довжина магістралі') AS "length_unit",
        MAX(CONCAT(pip.parameter_value, ' ', uom_inst.short_name_ukr)) FILTER (WHERE pt_inst.parameter_name_ukr = 'Максимальний перепад висот') AS "max_height_diff",
        MAX(CONCAT(tr.min_temp, '-', tr.max_temp, ' ', uom_temp.short_name_ukr)) FILTER (WHERE pt_temp.parameter_name_ukr = 'Діапазон встановлення температури') AS "Діапазон встановлення темп."
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.model_parameters_link AS mpl_comp ON cm.model_id = mpl_comp.model_id
    LEFT JOIN
        conditioners.parameter_values AS pv_comp ON mpl_comp.parameter_value_id = pv_comp.value_id
    LEFT JOIN
        conditioners.parameter_types AS pt_comp ON pv_comp.parameter_type_id = pt_comp.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_pv ON pt_comp.unit_id = uom_pv.unit_id
    LEFT JOIN
        conditioners.refrigerants AS r ON cm.refrigerant_id = r.refrigerant_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_charge ON cm.refrigerant_charge_unit_id = uom_charge.unit_id
    LEFT JOIN
        conditioners.calculated_pressures AS cp ON cm.pressure_id = cp.pressure_id
    LEFT JOIN
        conditioners.parameter_types AS pt_press ON cp.pressure_type_id = pt_press.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_press ON pt_press.unit_id = uom_press.unit_id
    LEFT JOIN
        conditioners.model_pipe_diameters_link AS mpdl ON cm.model_id = mpdl.model_id
    LEFT JOIN
        conditioners.pipe_diameters AS pd ON mpdl.pipe_diameter_id = pd.pipe_diameter_id
    LEFT JOIN
        conditioners.parameter_types AS pt_pipes ON mpdl.parameter_type_id = pt_pipes.parameter_type_id
    LEFT JOIN
        conditioners.model_installation_link AS mil ON cm.model_id = mil.model_id
    LEFT JOIN
        conditioners.pipe_installation_parameters AS pip ON mil.installation_parameter_id = pip.installation_parameter_id
    LEFT JOIN
        conditioners.parameter_types AS pt_inst ON pip.parameter_type_id = pt_inst.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_inst ON pt_inst.unit_id = uom_inst.unit_id
    LEFT JOIN
        conditioners.model_temp_range_link AS mtrl ON cm.model_id = mtrl.model_id
    LEFT JOIN
        conditioners.temperature_ranges AS tr ON mtrl.temp_range_id = tr.temp_range_id
    LEFT JOIN
        conditioners.parameter_types AS pt_temp ON tr.parameter_type_id = pt_temp.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_temp ON pt_temp.unit_id = uom_temp.unit_id
    LEFT JOIN
        conditioners.operation_modes AS om_temp ON tr.mode_id = om_temp.mode_id
    WHERE
        cm.model_id = $1
    GROUP BY
        cm.model_id
),
FeaturesAndFunctionsCTE AS (
    SELECT
        cm.model_id,
        string_agg(DISTINCT f.filter_name_ukr, ', ') AS "filters",
        string_agg(DISTINCT func.function_name_ukr, ', ') FILTER (WHERE ft.type_name_ukr = 'Основні') AS "main_functions",
        string_agg(DISTINCT CONCAT(func.function_name_ukr, ' (додатковий модуль)'), ', ') FILTER (WHERE ft.type_name_ukr = 'Додаткові') AS "additional_functions",
        string_agg(DISTINCT p.program_name_ukr, ', ') AS "programs"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.model_filters_link AS mfl ON cm.model_id = mfl.model_id
    LEFT JOIN
        conditioners.filters AS f ON mfl.filter_id = f.filter_id
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
    WHERE
        cm.model_id = $1
    GROUP BY
        cm.model_id
),
IndoorTempRangesCTE AS (
    SELECT
        cm.model_id,
        MAX(CONCAT(tr.min_temp, '~', tr.max_temp, ' ', uom_temp.short_name_ukr)) FILTER (WHERE pt_temp.parameter_name_ukr = 'Робочий діапазон температур внутрішнього блоку' AND om_temp.mode_name_ukr = 'Охолодження') AS "indoor_cooling_range",
        MAX(CONCAT(tr.min_temp, '~', tr.max_temp, ' ', uom_temp.short_name_ukr)) FILTER (WHERE pt_temp.parameter_name_ukr = 'Робочий діапазон температур внутрішнього блоку' AND om_temp.mode_name_ukr = 'Обігрів') AS "indoor_heating_range"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN conditioners.model_temp_range_link AS mtrl ON cm.model_id = mtrl.model_id
    LEFT JOIN conditioners.temperature_ranges AS tr ON mtrl.temp_range_id = tr.temp_range_id
    LEFT JOIN conditioners.parameter_types AS pt_temp ON tr.parameter_type_id = pt_temp.parameter_type_id
    LEFT JOIN conditioners.units_of_measurement AS uom_temp ON pt_temp.unit_id = uom_temp.unit_id
    LEFT JOIN conditioners.operation_modes AS om_temp ON tr.mode_id = om_temp.mode_id
    WHERE
        cm.model_id = $1
    GROUP BY cm.model_id
),
OutdoorTempRangesCTE AS (
    SELECT
        cm.model_id,
        MAX(CONCAT(tr.min_temp, '~', tr.max_temp, ' ', uom_temp.short_name_ukr)) FILTER (WHERE pt_temp.parameter_name_ukr = 'Робочий діапазон температур зовнішнього блоку' AND om_temp.mode_name_ukr = 'Охолодження') AS "outdoor_cooling_range",
        MAX(CONCAT(tr.min_temp, '~', tr.max_temp, ' ', uom_temp.short_name_ukr)) FILTER (WHERE pt_temp.parameter_name_ukr = 'Робочий діапазон температур зовнішнього блоку' AND om_temp.mode_name_ukr = 'Обігрів') AS "outdoor_heating_range"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN conditioners.model_temp_range_link AS mtrl ON cm.model_id = mtrl.model_id
    LEFT JOIN conditioners.temperature_ranges AS tr ON mtrl.temp_range_id = tr.temp_range_id
    LEFT JOIN conditioners.parameter_types AS pt_temp ON tr.parameter_type_id = pt_temp.parameter_type_id
    LEFT JOIN conditioners.units_of_measurement AS uom_temp ON pt_temp.unit_id = uom_temp.unit_id
    LEFT JOIN conditioners.operation_modes AS om_temp ON tr.mode_id = om_temp.mode_id
    WHERE
        cm.model_id = $1
    GROUP BY cm.model_id
),
PowerParametersCTE AS (
    SELECT
        cm.model_id,
        MAX(power_comp_type.type_name_ukr) AS "power_connection",
        CONCAT(
            CONCAT_WS('/', CONCAT(ps.min_voltage, '-', ps.max_voltage), ps.phase, ps.frequency),
            ' ',
            CONCAT_WS('/', uom_volt.short_name_ukr, uom_phase.short_name_ukr, uom_freq.short_name_ukr)
        ) AS "power_supply",
        CONCAT(vr.min_voltage, '~', vr.max_voltage, ' ', uom_vr.short_name_ukr) AS "voltage_range",
        MAX(CONCAT(cbl.cores, 'x', cbl.cross_section, ' ', uom_cbl.short_name_ukr)) FILTER (WHERE pt_cbl.parameter_name_ukr = 'Кабель живлення') AS "power_cable",
        MAX(CONCAT(cbl.cores, 'x', cbl.cross_section, ' ', uom_cbl.short_name_ukr)) FILTER (WHERE pt_cbl.parameter_name_ukr = 'Кабель міжблочного з''єднання') AS "inter_unit_cable",
        MAX(CONCAT(mp.value, ' ', uom_mp.short_name_ukr)) FILTER (WHERE pt_mp.parameter_name_ukr = 'Максимальна споживана потужність') AS "max_power_consumption",
        MAX(CONCAT(mp.value, ' ', uom_mp.short_name_ukr)) FILTER (WHERE pt_mp.parameter_name_ukr = 'Максимальний споживаний струм') AS "max_current_consumption"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.model_power_connections AS mpc ON cm.model_id = mpc.model_id
    LEFT JOIN
        conditioners.component_types AS power_comp_type ON mpc.power_component_type_id = power_comp_type.component_type_id
    LEFT JOIN
        conditioners.power_sources AS ps ON cm.power_source_id = ps.power_source_id
    LEFT JOIN
        conditioners.parameter_types AS pt_volt ON ps.voltage_parameter_type_id = pt_volt.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_volt ON pt_volt.unit_id = uom_volt.unit_id
    LEFT JOIN
        conditioners.parameter_types AS pt_freq ON ps.frequency_parameter_type_id = pt_freq.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_freq ON pt_freq.unit_id = uom_freq.unit_id
    LEFT JOIN
        conditioners.parameter_types AS pt_phase ON ps.phase_parameter_type_id = pt_phase.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_phase ON pt_phase.unit_id = uom_phase.unit_id
    LEFT JOIN
        conditioners.voltage_ranges AS vr ON cm.voltage_range_id = vr.voltage_range_id
    LEFT JOIN
        conditioners.parameter_types AS pt_vr ON vr.parameter_type_id = pt_vr.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_vr ON pt_vr.unit_id = uom_vr.unit_id
    LEFT JOIN
        conditioners.model_cables_link AS mcl_cbl ON cm.model_id = mcl_cbl.model_id
    LEFT JOIN
        conditioners.cables AS cbl ON mcl_cbl.cable_id = cbl.cable_id
    LEFT JOIN
        conditioners.parameter_types AS pt_cbl ON mcl_cbl.parameter_type_id = pt_cbl.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_cbl ON pt_cbl.unit_id = uom_cbl.unit_id
    LEFT JOIN
        conditioners.model_maximum_parameters_link AS mmpl ON cm.model_id = mmpl.model_id
    LEFT JOIN
        conditioners.maximum_parameters AS mp ON mmpl.maximum_parameter_id = mp.maximum_parameter_id
    LEFT JOIN
        conditioners.parameter_types AS pt_mp ON mmpl.parameter_type_id = pt_mp.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_mp ON pt_mp.unit_id = uom_mp.unit_id
    WHERE
        cm.model_id = $1
    GROUP BY
        cm.model_id,
        ps.min_voltage,
        ps.max_voltage,
        ps.phase,
        ps.frequency,
        uom_volt.short_name_ukr,
        uom_phase.short_name_ukr,
        uom_freq.short_name_ukr,
        vr.min_voltage,
        vr.max_voltage,
        uom_vr.short_name_ukr
),
WeightsCTE AS (
    SELECT
        cm.model_id,
        MAX(CONCAT(wgt.net_weight, ' (', wgt.gross_weight, ') ', uom_wgt.short_name_ukr)) FILTER (WHERE pt_wgt.parameter_name_ukr = 'Вага внутрішнього блоку нетто (брутто)') AS "Вага внутр. бл. нетто (брутто)",
        MAX(CONCAT(wgt.net_weight, ' (', wgt.gross_weight, ') ', uom_wgt.short_name_ukr)) FILTER (WHERE pt_wgt.parameter_name_ukr = 'Вага зовнішнього блоку нетто (брутто)') AS "Вага зовн. бл. нетто (брутто)"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.model_weights_link AS mwl_wgt ON cm.model_id = mwl_wgt.model_id
    LEFT JOIN
        conditioners.weights AS wgt ON mwl_wgt.weight_id = wgt.weight_id
    LEFT JOIN
        conditioners.parameter_types AS pt_wgt ON mwl_wgt.parameter_type_id = pt_wgt.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_wgt ON pt_wgt.unit_id = uom_wgt.unit_id
    WHERE
        cm.model_id = $1
    GROUP BY
        cm.model_id
),
PerformanceAndEfficiencyCTE AS (
    SELECT
        cm.model_id,
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Теплова потужність' AND om_pp_mode.mode_name_ukr = 'Охолодження') AS "cooling_heat_capacity",
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Потужність' AND om_pp_mode.mode_name_ukr = 'Охолодження') AS "cooling_power",
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Номінальна споживана потужність' AND om_pp_mode.mode_name_ukr = 'Охолодження') AS "Ном. спож. пот. (охол.)",
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Номінальний струм' AND om_pp_mode.mode_name_ukr = 'Охолодження') AS "cooling_nominal_current",
        MAX(CONCAT(eer.rating_value, ' (', eec.class_name, ')') ) FILTER (WHERE pt_eer.parameter_name_ukr = 'SEER') AS "seer",
        MAX(CONCAT(eer.rating_value) ) FILTER (WHERE pt_eer.parameter_name_ukr = 'EER') AS "eer",
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Теплова потужність' AND om_pp_mode.mode_name_ukr = 'Обігрів') AS "heating_heat_capacity",
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Потужність' AND om_pp_mode.mode_name_ukr = 'Обігрів') AS "heating_power",
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Номінальна споживана потужність' AND om_pp_mode.mode_name_ukr = 'Обігрів') AS "Ном. спож. пот. (об.)",
        MAX(CONCAT(pp.nominal_value, ' (', pp.min_value, '~', pp.max_value, ') ', uom_pp.short_name_ukr)) FILTER (WHERE pt_pp.parameter_name_ukr = 'Номінальний струм' AND om_pp_mode.mode_name_ukr = 'Обігрів') AS "heating_nominal_current",
        MAX(CONCAT(eer.rating_value, ' (', eec.class_name, ')') ) FILTER (WHERE pt_eer.parameter_name_ukr = 'SCOP') AS "scop",
        MAX(CONCAT(eer.rating_value) ) FILTER (WHERE pt_eer.parameter_name_ukr = 'COP') AS "cop"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.performance_parameters AS pp ON cm.model_id = pp.model_id
    LEFT JOIN
        conditioners.parameter_types AS pt_pp ON pp.parameter_type_id = pt_pp.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom_pp ON pt_pp.unit_id = uom_pp.unit_id
    LEFT JOIN
        conditioners.operation_modes AS om_pp_mode ON pp.mode_id = om_pp_mode.mode_id
    LEFT JOIN
        conditioners.model_ratings_link AS mrl ON cm.model_id = mrl.model_id
    LEFT JOIN
        conditioners.energy_efficiency_ratings AS eer ON mrl.rating_id = eer.rating_id
    LEFT JOIN
        conditioners.parameter_types AS pt_eer ON eer.parameter_type_id = pt_eer.parameter_type_id
    LEFT JOIN
        conditioners.energy_efficiency_classes AS eec ON eer.class_id = eec.class_id
    WHERE
        cm.model_id = $1
    GROUP BY
        cm.model_id
),
MountingDimensionsCTE AS (
    SELECT
        mdl.model_id,
        MAX(CONCAT(csd.value_mm, ' ', uom.short_name_ukr)) FILTER (WHERE pt.parameter_name_ukr = 'Монтажні розміри' AND dt.type_name_ukr = 'Висота до нижнього крану') AS "height_to_lower_faucet",
        MAX(CONCAT(csd.value_mm, ' ', uom.short_name_ukr)) FILTER (WHERE pt.parameter_name_ukr = 'Монтажні розміри' AND dt.type_name_ukr = 'Виступ захисної кришки кранів') AS "protective_cover_protrusion",
        MAX(CONCAT(csd.value_mm, ' ', uom.short_name_ukr)) FILTER (WHERE pt.parameter_name_ukr = 'Монтажні розміри' AND dt.type_name_ukr = 'Відстань між кранами') AS "distance_between_faucets",
        MAX(CONCAT(csd.value_mm, ' ', uom.short_name_ukr)) FILTER (WHERE pt.parameter_name_ukr = 'Монтажні розміри' AND dt.type_name_ukr = 'Відстань між кронштейнами') AS "distance_between_brackets",
        MAX(CONCAT(csd.value_mm, ' ', uom.short_name_ukr)) FILTER (WHERE pt.parameter_name_ukr = 'Монтажні розміри' AND dt.type_name_ukr = 'Глибина по кронштейну') AS "depth_along_bracket"
    FROM
        conditioners.model_dimensions_link AS mdl
    LEFT JOIN
        conditioners.component_specific_dimensions AS csd ON mdl.dimension_id = csd.specific_dimension_id
    LEFT JOIN
        conditioners.dimension_types AS dt ON csd.dimension_type_id = dt.dimension_type_id
    LEFT JOIN
        conditioners.parameter_types AS pt ON mdl.parameter_type_id = pt.parameter_type_id
    LEFT JOIN
        conditioners.units_of_measurement AS uom ON pt.unit_id = uom.unit_id
    WHERE
        mdl.model_id = 1
    GROUP BY
        mdl.model_id
),
ProtectionClassCTE AS (
    SELECT
        cm.model_id,
        MAX(pv.value) FILTER (WHERE pt.parameter_name_ukr = 'Клас захисту') AS "protection_class"
    FROM
        conditioners.conditioner_models AS cm
    LEFT JOIN
        conditioners.model_parameters_link AS mpl ON cm.model_id = mpl.model_id
    LEFT JOIN
        conditioners.parameter_values AS pv ON mpl.parameter_value_id = pv.value_id
    LEFT JOIN
        conditioners.parameter_types AS pt ON pv.parameter_type_id = pt.parameter_type_id
    WHERE
        cm.model_id = $1
    GROUP BY
        cm.model_id
),
TemplatesCTE AS (
    SELECT
        mtl.model_id,
        mt.template_text_ukr AS template_text,
        tt.type_name_ukr AS template_type,
        tt.type_id
    FROM
        conditioners.model_templates_link AS mtl
    LEFT JOIN
        conditioners.message_templates AS mt ON mtl.template_id = mt.template_id
    LEFT JOIN
        conditioners.template_types AS tt ON mtl.template_type_id = tt.type_id
    WHERE mtl.model_id = 1
)
SELECT
    st.series_name_ukr AS "TypeSeries",
    b.brand_name AS "Brand",
    s.series_name_ukr AS "Series",
    CONCAT(b.brand_name, ' ', s.series_name_ukr, ' ', br.btu_rating_value) AS "Model",
    CONCAT(ra.area_sq_m, ' ', uom_ra.short_name_ukr) AS "RecommendedArea",
    CONCAT(w.warranty_period_value, ' ', uom_w.short_name_ukr) AS "Гарантія",
    ct.type_name_ukr AS "Тип встановлення",
    string_agg(DISTINCT c.model_name_ukr, ', ') FILTER (WHERE c_type.type_name_ukr = 'Внутрішній блок') AS "InternalUnit",
    string_agg(DISTINCT c.model_name_ukr, ', ') FILTER (WHERE c_type.type_name_ukr = 'Зовнішній блок') AS "ExternalUnit",
    string_agg(DISTINCT c.model_name_ukr, ', ') FILTER (WHERE c_type.type_name_ukr = 'Декоративна панель') AS "Декоративна панель",
    string_agg(DISTINCT om.mode_name_ukr, ', ') AS "Режими роботи",
    ppc.power_connection AS "Підключення живлення",
    ppc.power_supply AS "Електроживлення",
    ppc.voltage_range AS "Допустимий перепад напруги",
    ppc.power_cable AS "Кабель живлення",
    ppc.inter_unit_cable AS "Кабель міжблочного з'єднання",
    ppc.max_power_consumption AS "Максимальна споживана потужність",
    ppc.max_current_consumption AS "Максимальний споживчий струм А",
    pne.cooling_heat_capacity AS "Теплова потужність (охолодження)",
    pne.cooling_power AS "Потужність (охолодження)",
    pne."Ном. спож. пот. (охол.)" AS "Ном. спож. пот. (охол.)",
    pne.cooling_nominal_current AS "Номінальний струм (охолодження)",
    pne.seer AS "SEER",
    pne.eer AS "EER",
    pne.heating_heat_capacity AS "Теплова потужність (обігрів)",
    pne.heating_power AS "Потужність (обігрів)",
    pne."Ном. спож. пот. (об.)" AS "Ном. спож. пот. (об.)",
    pne.heating_nominal_current AS "Номінальний струм (обігрів)",
    pne.scop AS "SCOP",
    pne.cop AS "COP",
    afn.air_flow_internal AS "Витрата повітря (внутрішній блок)",
    afn.noise_level_internal AS "Рівень шуму (внутрішній блок)",
    CONCAT(CONCAT_WS('x', MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри внутрішнього блоку' AND dim.type_name_ukr = 'Довжина'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри внутрішнього блоку' AND dim.type_name_ukr = 'Ширина'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри внутрішнього блоку' AND dim.type_name_ukr = 'Висота')), ' мм') AS "Розміри внутрішнього блоку",
    CONCAT(CONCAT_WS('x', MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри внутрішнього блоку в упаковці' AND dim.type_name_ukr = 'Довжина в упаковці'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри внутрішнього блоку в упаковці' AND dim.type_name_ukr = 'Ширина в упаковці'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри внутрішнього блоку в упаковці' AND dim.type_name_ukr = 'Висота в упаковці')), ' мм') AS "Розм. внутр. бл. в упаковці",
    wgt."Вага внутр. бл. нетто (брутто)" AS "Вага внутр. бл. нетто (брутто)",
    afn.air_flow_external AS "Витрата повітря (зовнішній блок)",
    afn.noise_level_external AS "Рівень шуму (зовнішній блок)",
    CONCAT(CONCAT_WS('x', MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри зовнішнього блоку' AND dim.type_name_ukr = 'Довжина'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри зовнішнього блоку' AND dim.type_name_ukr = 'Ширина'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри зовнішнього блоку' AND dim.type_name_ukr = 'Висота')), ' мм') AS "Розміри зовнішнього блоку",
    CONCAT(CONCAT_WS('x', MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри зовнішнього блоку в упаковці' AND dim.type_name_ukr = 'Довжина в упаковці'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри зовнішнього блоку в упаковці' AND dim.type_name_ukr = 'Ширина в упаковці'), MAX(dim.value_mm) FILTER (WHERE dim.parameter_name_ukr = 'Розміри зовнішнього блоку в упаковці' AND dim.type_name_ukr = 'Висота в упаковці')), ' мм') AS "Розм. зовн. бл. в упаковці",
    wgt."Вага зовн. бл. нетто (брутто)" AS "Вага зовн. бл. нетто (брутто)",
    md.height_to_lower_faucet AS "Висота до нижнього крану",
    md.protective_cover_protrusion AS "Виступ захисної кришки кранів",
    md.distance_between_faucets AS "Відстань між кранами",
    md.distance_between_brackets AS "Відстань між кронштейнами",
    md.depth_along_bracket AS "Глибина по кронштейну",
    tp."Тип компр за методом управління" AS "Тип компр за методом управління",
    tp."Тип компр за принципом роботи" AS "Тип компр за принципом роботи",
    tp.compressor_manufacturer AS "Компресор",
    tp.oil_type AS "Тип мастила",
    tp.oil_volume AS "Обсяг мастила",
    tp.refrigerant_name AS "Холодоагент",
    tp.refrigerant_charge AS "Вага холодоагенту",
    tp.pressure_range AS "Розрахунковий тиск",
    tp.pipe_diameters AS "Сполучні труби",
    tp.drain_pipe_diameter AS "Діаметр дренажної труби",
    CONCAT(tp.min_length, ' / ', tp.max_length, ' ', tp.length_unit) AS "Мінімальна / максимальна траса",
    tp.max_height_diff AS "Максимальний перепад висот",
    tp."Діапазон встановлення темп." AS "Діапазон встановлення темп.",
    CONCAT(itr.indoor_cooling_range, '/', itr.indoor_heating_range) AS "Роб діапазон темп внутр бл охол/об",
    CONCAT(otr.outdoor_cooling_range, '/', otr.outdoor_heating_range) AS "Роб діапазон темп зовн бл охол/об",
    ff.filters AS "Фільтри",
    ff.main_functions AS "Основні функції",
    pc.protection_class AS "Клас захисту",
    ff.additional_functions AS "Додаткові функції",
    ff.programs AS "Програма",
    MAX(t.template_text) FILTER (WHERE t.template_type = 'Основна інформація') AS "Основна інформація",
    MAX(t.template_text) FILTER (WHERE t.template_type = 'Компресор') AS "Компресор",
    MAX(t.template_text) FILTER (WHERE t.template_type = 'Функції WiFi') AS "Функції WiFi",
    MAX(t.template_text) FILTER (WHERE t.template_type = 'Іонізація') AS "Іонізація",
    MAX(t.template_text) FILTER (WHERE t.template_type = 'Витрати ресурсів') AS "Витрати ресурсів"
FROM
    conditioners.conditioner_models AS cm
LEFT JOIN
    product_metadata.brands AS b ON cm.brand_id = b.brand_id
LEFT JOIN
    product_metadata.brand_series AS s ON cm.series_id = s.series_id
LEFT JOIN
    conditioners.conditioner_types AS ct ON cm.conditioner_type_id = ct.conditioner_type_id
LEFT JOIN
    conditioners.series_types AS st ON ct.series_type_id = st.series_type_id
LEFT JOIN
    conditioners.btu_ratings AS br ON cm.btu_rating_id = br.btu_rating_id
LEFT JOIN
    conditioners.recommended_areas AS ra ON cm.recommended_area_id = ra.area_id
LEFT JOIN
    conditioners.units_of_measurement AS uom_ra ON ra.unit_id = uom_ra.unit_id
LEFT JOIN
    conditioners.warranties AS w ON cm.warranty_id = w.warranty_id
LEFT JOIN
    conditioners.parameter_types AS pt_w ON w.parameter_type_id = pt_w.parameter_type_id
LEFT JOIN
    conditioners.units_of_measurement AS uom_w ON pt_w.unit_id = uom_w.unit_id
LEFT JOIN
    conditioners.model_components_link AS mcl ON cm.model_id = mcl.model_id
LEFT JOIN
    conditioners.components AS c ON mcl.component_id = c.component_id
LEFT JOIN
    conditioners.component_types AS c_type ON c.component_type_id = c_type.component_type_id
LEFT JOIN
    conditioners.model_operation_modes AS mom ON cm.model_id = mom.model_id
LEFT JOIN
    conditioners.operation_modes AS om ON mom.mode_id = om.mode_id
LEFT JOIN
    DimensionsCTE AS dim ON cm.model_id = dim.model_id
LEFT JOIN
    AirFlowAndNoiseCTE AS afn ON cm.model_id = afn.model_id
LEFT JOIN
    TechnicalParametersCTE AS tp ON cm.model_id = tp.model_id
LEFT JOIN
    FeaturesAndFunctionsCTE AS ff ON cm.model_id = ff.model_id
LEFT JOIN
    IndoorTempRangesCTE AS itr ON cm.model_id = itr.model_id
LEFT JOIN
    OutdoorTempRangesCTE AS otr ON cm.model_id = otr.model_id
LEFT JOIN
    PowerParametersCTE AS ppc ON cm.model_id = ppc.model_id
LEFT JOIN
    WeightsCTE AS wgt ON cm.model_id = wgt.model_id
LEFT JOIN
    PerformanceAndEfficiencyCTE AS pne ON cm.model_id = pne.model_id
LEFT JOIN
    MountingDimensionsCTE AS md ON cm.model_id = md.model_id
LEFT JOIN
    ProtectionClassCTE AS pc ON cm.model_id = pc.model_id
LEFT JOIN
    TemplatesCTE AS t ON cm.model_id = t.model_id
WHERE
    cm.model_id = $1
GROUP BY
    st.series_name_ukr,
    b.brand_name,
    s.series_name_ukr,
    br.btu_rating_value,
    ct.type_name_ukr,
    w.warranty_period_value,
    uom_w.short_name_ukr,
    afn.air_flow_internal,
    afn.noise_level_internal,
    afn.air_flow_external,
    afn.noise_level_external,
    tp."Тип компр за методом управління",
    tp."Тип компр за принципом роботи",
    tp.compressor_manufacturer,
    tp.oil_type,
    tp.oil_volume,
    tp.refrigerant_name,
    tp.refrigerant_charge,
    tp.pressure_range,
    tp.pipe_diameters,
    tp.drain_pipe_diameter,
    tp.min_length,
    tp.max_length,
    tp.length_unit,
    tp.max_height_diff,
    tp."Діапазон встановлення темп.",
    ff.filters,
    ff.main_functions,
    ff.additional_functions,
    ff.programs,
    itr.indoor_cooling_range,
    itr.indoor_heating_range,
    otr.outdoor_cooling_range,
    otr.outdoor_heating_range,
    ppc.power_connection,
    ppc.power_supply,
    ppc.voltage_range,
    ppc.power_cable,
    ppc.inter_unit_cable,
    ppc.max_power_consumption,
    ppc.max_current_consumption,
    wgt."Вага внутр. бл. нетто (брутто)",
    wgt."Вага зовн. бл. нетто (брутто)",
    pne."Ном. спож. пот. (охол.)",
    pne.cooling_heat_capacity,
    pne.cooling_power,
    pne.cooling_nominal_current,
    pne.seer,
    pne.eer,
    pne."Ном. спож. пот. (об.)",
    pne.heating_heat_capacity,
    pne.heating_power,
    pne.heating_nominal_current,
    pne.scop,
    pne.cop,
    md.height_to_lower_faucet,
    md.protective_cover_protrusion,
    md.distance_between_faucets,
    md.distance_between_brackets,
    md.depth_along_bracket,
    pc.protection_class,
    ra.area_sq_m,
    uom_ra.short_name_ukr;
