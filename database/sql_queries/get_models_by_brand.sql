SELECT
    cm.model_id,
    b.brand_name,
    CONCAT_WS(' ', b.brand_name, s.series_name_ukr, br.btu_rating_value ) AS "Модель"
FROM
    conditioners.conditioner_models AS cm
LEFT JOIN
    product_metadata.brands AS b ON cm.brand_id = b.brand_id
LEFT JOIN
    product_metadata.brand_series AS s ON cm.series_id = s.series_id
LEFT JOIN
    conditioners.btu_ratings AS br ON cm.btu_rating_id = br.btu_rating_id
WHERE
    b.brand_name = $1
ORDER BY s.series_name_ukr;
