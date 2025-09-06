-- database/sql_queries/get_brands_with_model_count.sql
SELECT
    b.brand_id,               -- Додаємо brand_id
    b.brand_name,
    COUNT(cm.model_id) AS model_count
FROM
    product_metadata.brands AS b
LEFT JOIN
    conditioners.conditioner_models AS cm
ON
    b.brand_id = cm.brand_id
GROUP BY
    b.brand_id, b.brand_name -- Групуємо за brand_id та brand_name
HAVING
    COUNT(cm.model_id) > 0
ORDER BY
    b.brand_name;
