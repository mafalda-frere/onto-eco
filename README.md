# Ontology-Driven Ecosystem Simulation

This project demonstrates how an **OWL ontology combined with automated reasoning** can be used as the **core driver of an ecosystem simulation**.

Instead of hard-coding species behavior and trophic relations, the simulation **derives them dynamically from an ontology**, using semantic reasoning to infer:
- species traits (plant, herbivore, carnivore),
- predator–prey relationships,
- ecosystem structure.

---

## Ontology-First Approach

The project is built around the **African Wildlife Ontology (AWO)**.

### Ontology enrichment
The notebook **`enrich_AWO.ipynb`** is used to:
- extend the original ontology,
- add new species (e.g. giraffe, zebra, etc.),
- refine taxonomic hierarchies and trophic constraints.

This produces:
- **`AfricanWildlifeOntology4_enriched.owl`**

which is the ontology used by the application.

> The key idea is that **new species and behaviors can be introduced by modifying the ontology, without changing the simulation code**.

### Ontology reasoning
At runtime, the application:
- loads the enriched ontology,
- applies **OWL RL reasoning**,
- infers implicit knowledge (subclasses, trophic roles, restrictions),
- freezes reasoning during simulation steps for performance and consistency.

The inferred knowledge is then **used to drive ecosystem dynamics**.

---

## Ecosystem Simulation

The simulation models:
- plants, herbivores, and carnivores,
- energy consumption and gains,
- feeding and hunting events,
- reproduction and extinction,
- automatic detection of stability or collapse.

Predation rules are **not hard-coded**:  
they are inferred from ontology restrictions such as `eats some Herbivore`.

---

## Application

- **Backend**: Flask API
- **Frontend**: Minimal HTML + JavaScript + Chart.js
- **Visualization**:
  - individuals and trophic links,
  - population evolution per species over time.

---

## Project Structure

| File / Folder | Description |
|---------------|-------------|
| `AfricanWildlifeOntology4.owl` | Original African Wildlife Ontology |
| `AfricanWildlifeOntology4_enriched.owl` | Enriched ontology used by the simulation |
| `enrich_AWO.ipynb` | Notebook used to enrich and extend the ontology |
| `AWO_exploration.ipynb` | Notebook for ontology exploration and validation |
| `config.py` | Global configuration and simulation parameters |
| `app.py` | Flask application entry point |
| `requirements.txt` | Python dependencies |

### `ontology/`
| File | Role |
|------|------|
| `loader.py` | Loads RDF graphs and defines ontology namespaces |
| `reasoner.py` | OWL RL reasoning with caching and freeze mechanism |
| `species.py` | Species extraction, trait inference, trophic rules |

### `simulation/`
| File | Role |
|------|------|
| `state.py` | Global simulation state |
| `rules.py` | Energy, feeding, hunting, reproduction rules |
| `lifecycle.py` | Individual creation and removal |
| `stopping.py` | Stability, extinction, and timeout conditions |

### `graph/`
| File | Role |
|------|------|
| `eats.py` | Management of inferred `eats` relationships |

### `api/`
| File | Role |
|------|------|
| `species.py` | Species listing API |
| `state.py` | Current ecosystem state API |
| `simulation.py` | Simulation control endpoints |

### `ui/`
| File | Role |
|------|------|
| `index.html` | Interactive visualization (populations & relations) |

---

## Running the Project

### 1. Clone the repository

```bash
git clone git@github.com:mafalda-frere/onto-eco.git
cd onto-eco
```

### 2. Create and activate the Conda environment

```bash
conda create -n eco_env python=3.10
conda activate eco_env
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch the application

```bash
python app.py
```

Then open your browser at:
http://127.0.0.1:5000/
