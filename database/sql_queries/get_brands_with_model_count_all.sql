--get_brands_with_model_count_all.sql
select
	b.brand_id ,
	b.brand_name,
	bs.series_id ,
	bs.series_name_ukr,
	COUNT(cm.model_id) AS model_count
from product_metadata.brands b
    left join product_metadata.brand_series bs on b.brand_id = bs.brand_id 
    left join conditioners.conditioner_models cm on bs.series_id = cm.series_id 
group by b.brand_id,bs.series_id
order by
	b.brand_name ASC, -- Сортування за брендом (за алфавітом)
    bs.series_name_ukr ASC; -- Сортування за серією (за алфавітом)
    ;
