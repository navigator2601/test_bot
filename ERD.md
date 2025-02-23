```mermaid
erDiagram
    PLAYING_WITH_NEON {
        INTEGER id
        REAL value
        TEXT name
    }
    COND_BTU {
        INTEGER id
        INTEGER power
        VARCHAR(10) abbr
        TEXT note
    }
    COND_DIM_INDOOR {
        INTEGER id
        INTEGER length_mm
        INTEGER width_mm
        INTEGER depth_mm
        INTEGER weight_kg
    }
    COND_MODELS {
        INTEGER id
        VARCHAR(100) indoor_unit_model
        VARCHAR(100) outdoor_unit_model
        VARCHAR(210) abbr
        TEXT note
    }
    DEVICE_POWER {
        INTEGER id
        INTEGER power_kw
        INTEGER current_a
        INTEGER cond_model_id
        DOUBLE PRECISION cable_section
        VARCHAR note
    }
    CABLE_SECTIONS {
        INTEGER min_current
        INTEGER max_current
        DOUBLE PRECISION cable_section
    }
    CONNECT_TYPE {
        INTEGER id
        INTEGER cable_type
        INTEGER phase
        INTEGER voltage
    }
    PIPE_DIAMETERS {
        INTEGER id
        NUMERIC diameter_inches
        NUMERIC diameter_mm
        VARCHAR(10) diameter_fraction
    }
    FREONS {
        INTEGER id
        NUMERIC global_warming_potential
        NUMERIC ozone_depletion_potential
        NUMERIC boiling_point
        NUMERIC critical_temperature
        NUMERIC critical_pressure
        NUMERIC density_liquid
        NUMERIC density_vapor
        NUMERIC molecular_weight
        VARCHAR(20) cas_number
        VARCHAR(50) name
        VARCHAR(20) class
        VARCHAR(100) chemical_name
        VARCHAR(50) chemical_formula
        VARCHAR(20) toxicity
        VARCHAR(255) compatible_oils
        VARCHAR(20) flammability
    }
    COND_DIM_OUDOOR {
        INTEGER id
        INTEGER length_mm
        INTEGER width_mm
        INTEGER depth_mm
        INTEGER size_a_mm
        INTEGER size_b_mm
        INTEGER weight_kg
    }
    INNER_BLOCK_INDENTS {
        INTEGER id
        INTEGER above_mm
        INTEGER left_mm
        INTEGER case_mm
        INTEGER below_mm
        INTEGER front_m
    }
    EXTERNAL_BLOCK_INDENTS {
        INTEGER id
        INTEGER above_mm
        INTEGER left_mm
        INTEGER case_mm
        INTEGER below_mm
        INTEGER butt_mm
        INTEGER front_m
    }
    TRACK_LIMITS {
        INTEGER id
        INTEGER power_min
        INTEGER power_max
        INTEGER min_track_length
        INTEGER max_track_length
        INTEGER max_height_difference
    }
    COND_BRAND {
        INTEGER id
        TEXT name
        TEXT abbr
        TEXT note
    }
    COND_TYPE {
        INTEGER id
        VARCHAR(100) name
        VARCHAR(10) abbr
        TEXT note
    }

    COND_MODELS ||--o{ DEVICE_POWER : "cond_model_id"
    COND_MODELS ||--|{ COND_BTU : "abbr"
    COND_MODELS ||--o{ COND_DIM_INDOOR : "id"
    COND_MODELS ||--o{ COND_DIM_OUDOOR : "id"
    COND_MODELS ||--o{ COND_BRAND : "id"
    CABLE_SECTIONS ||--o{ DEVICE_POWER : "cable_section"
    FREONS ||--o{ COND_TYPE : "id"
    CONNECT_TYPE ||--o{ DEVICE_POWER : "id"
```