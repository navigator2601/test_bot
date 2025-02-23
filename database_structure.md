# Database Structure

## Tables

### Марка кондиціонера (cond_brand)
| Column | Data Type | Constraints |
|--------|-----------|-------------|
| id     | integer   | NOT NULL    |
| name   | text      |             |
| abbr   | text      |             |
| note   | text      |             |

### Тип кондиціонера (cond_type)
| Column | Data Type     | Constraints |
|--------|---------------|-------------|
| id     | integer       | NOT NULL DEFAULT nextval('cond_type_id_seq'::regclass) |
| name   | varchar(100)  | NOT NULL    |
| abbr   | varchar(10)   | NOT NULL    |
| note   | text          |             |

### Потужність (cond_btu)
| Column | Data Type | Constraints |
|--------|-----------|-------------|
| id     | integer   | NOT NULL DEFAULT nextval('cond_btu_id_seq'::regclass) |
| power  | integer   | NOT NULL    |
| abbr   | varchar(10) |          |
| note   | text      |             |

### Маркування блоків (cond_models)
| Column              | Data Type     | Constraints |
|---------------------|---------------|-------------|
| id                  | integer       | NOT NULL DEFAULT nextval('cond_models_id_seq'::regclass) |
| indoor_unit_model   | varchar(100)  | NOT NULL    |
| outdoor_unit_model  | varchar(100)  | NOT NULL    |
| abbr                | varchar(210)  |             |
| note                | text          |             |

### Габарити внутрішнього блоку (cond_dim_indoor)
| Column    | Data Type | Constraints |
|-----------|-----------|-------------|
| id        | integer   | NOT NULL DEFAULT nextval('cond_dim_indoor_id_seq'::regclass) |
| length_mm | integer   |             |
| width_mm  | integer   |             |
| depth_mm  | integer   |             |
| weight_kg | integer   |             |

### Габарити зовнішнього блоку (cond_dim_outdoor)
| Column    | Data Type | Constraints |
|-----------|-----------|-------------|
| id        | integer   | NOT NULL DEFAULT nextval('cond_dim_oudoor_id_seq'::regclass) |
| length_mm | integer   |             |
| width_mm  | integer   |             |
| depth_mm  | integer   |             |
| size_a_mm | integer   |             |
| size_b_mm | integer   |             |
| weight_kg | integer   |             |

### Потужність пристрою (device_power)
| Column         | Data Type     | Constraints |
|----------------|---------------|-------------|
| id             | integer       | NOT NULL DEFAULT nextval('device_power_id_seq'::regclass) |
| power_kw       | integer       |             |
| current_a      | integer       |             |
| cond_model_id  | integer       |             |
| cable_section  | double precision |         |
| note           | varchar       |             |

### Характеристики силових кабелів (cable_sections)
| Column       | Data Type        | Constraints |
|--------------|------------------|-------------|
| min_current  | integer          | NOT NULL    |
| max_current  | integer          | NOT NULL    |
| cable_section| double precision | NOT NULL    |

### Характеристики типу підключення (connect_type)
| Column     | Data Type | Constraints |
|------------|-----------|-------------|
| id         | integer   | NOT NULL DEFAULT nextval('connect_type_id_seq'::regclass) |
| cable_type | integer   |             |
| phase      | integer   |             |
| voltage    | integer   |             |

### Відступи внутрішнього блоку (inner_block_indents)
| Column   | Data Type | Constraints |
|----------|-----------|-------------|
| id       | integer   | NOT NULL DEFAULT nextval('inner_block_indents_id_seq'::regclass) |
| above_mm | integer   |             |
| left_mm  | integer   |             |
| case_mm  | integer   |             |
| below_mm | integer   |             |
| front_m  | integer   |             |

### Відступи зовнішнього блоку (external_block_indents)
| Column   | Data Type | Constraints |
|----------|-----------|-------------|
| id       | integer   | NOT NULL DEFAULT nextval('external_block_indents_id_seq'::regclass) |
| above_mm | integer   |             |
| left_mm  | integer   |             |
| case_mm  | integer   |             |
| below_mm | integer   |             |
| butt_mm  | integer   |             |
| front_m  | integer   |             |

### Діаметри труб (pipe_diameters)
| Column           | Data Type      | Constraints |
|------------------|----------------|-------------|
| id               | integer        | NOT NULL DEFAULT nextval('pipe_diameters_id_seq'::regclass) |
| diameter_inches  | numeric        |             |
| diameter_mm      | numeric        |             |
| diameter_fraction| varchar(10)    | NOT NULL    |

### Фреони (freons)
| Column                  | Data Type      | Constraints |
|-------------------------|----------------|-------------|
| id                      | integer        | NOT NULL DEFAULT nextval('freons_id_seq'::regclass) |
| global_warming_potential| numeric        |             |
| ozone_depletion_potential| numeric       |             |
| boiling_point           | numeric        |             |
| critical_temperature    | numeric        |             |
| critical_pressure       | numeric        |             |
| density_liquid          | numeric        |             |
| density_vapor           | numeric        |             |
| molecular_weight        | numeric        |             |
| cas_number              | varchar(20)    |             |
| name                    | varchar(50)    | NOT NULL    |
| class                   | varchar(20)    | NOT NULL    |
| chemical_name           | varchar(100)   |             |
| chemical_formula        | varchar(50)    |             |
| toxicity                | varchar(20)    |             |
| compatible_oils         | varchar(255)   |             |
| flammability            | varchar(20)    |             |

### Довжини трас та перепади (track_limits)
| Column               | Data Type | Constraints |
|----------------------|-----------|-------------|
| id                   | integer   | NOT NULL DEFAULT nextval('track_limits_id_seq'::regclass) |
| power_min            | integer   | NOT NULL    |
| power_max            | integer   | NOT NULL    |
| min_track_length     | integer   | NOT NULL    |
| max_track_length     | integer   | NOT NULL    |
| max_height_difference| integer   | NOT NULL    |

## Relationships

- **device_power** is connected to **cond_models** through `cond_model_id`.

## SQL Queries

### Join device_power with cond_models
```sql
SELECT * FROM device_power
JOIN cond_models ON device_power.cond_model_id = cond_models.id;
```