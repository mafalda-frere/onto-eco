# config.py

ONTO_PATH = "AfricanWildlifeOntology4_enriched.owl"

SIMULATION_PARAMS = {
    "E_MAX": 10,
    "E_INIT": 6,
    "COST_STEP": 1,

    "GAIN_PLANT": 4,
    "GAIN_PREY": 5,

    "E_REPRO": 9,
    "REPRO_COST": 5,

    "P_REPRO_PLANT": 0.70,
    "K_PLANT": 50,

    "P_REPRO_HERB": 0.22,
    "P_REPRO_CARN": 0.10,

    "HUNT_PROB": 0.35,

    "stable_window": 15,
    "stable_range": 1,
    "max_steps": 300
}
