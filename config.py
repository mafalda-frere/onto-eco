# config.py

ONTO_PATH = "AfricanWildlifeOntology4_enriched.owl"

SIMULATION_PARAMS = {
    "E_MAX": 10,
    "E_INIT": 6,
    "COST_STEP": 1,

    "GAIN_PLANT": 4,
    "GAIN_PREY": 5,

    "E_REPRO": 8,
    "REPRO_COST": 4,

    "P_REPRO_PLANT": 0.20,
    "K_PLANT": 30,

    "P_REPRO_HERB": 0.25,
    "P_REPRO_CARN": 0.20,

    "HUNT_PROB": 0.55,

    "stable_window": 10,
    "stable_range": 1,
    "max_steps": 300
}
