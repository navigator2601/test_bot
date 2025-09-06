SELECT
    cm.model_id,
    CONCAT_WS(' ', b.brand_name, s.series_name_ukr, br.btu_rating_value) AS "Модель",
    s.series_name_ukr
FROM
    conditioners.conditioner_models AS cm
LEFT JOIN
    product_metadata.brands AS b ON cm.brand_id = b.brand_id
LEFT JOIN
    product_metadata.brand_series AS s ON cm.series_id = s.series_id
LEFT JOIN
    conditioners.btu_ratings AS br ON cm.btu_rating_id = br.btu_rating_id
WHERE
    cm.brand_id = $1
ORDER BY
    "Модель";
