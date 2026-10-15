"""Sistema de recomendación sencillo basado en K vecinos más cercanos.

El archivo ``products.csv`` debe contener las columnas:
``feature1, feature2, feature3, label``.
"""

from pathlib import Path

import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler


FEATURES = ["feature1", "feature2", "feature3"]
LABEL = "label"


def load_products(csv_path: str | Path = "products.csv") -> pd.DataFrame:
    """Carga y valida el catálogo de productos."""
    products = pd.read_csv(csv_path)
    required_columns = FEATURES + [LABEL]
    missing = [column for column in required_columns if column not in products.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el CSV: {', '.join(missing)}")
    if products.empty:
        raise ValueError("El archivo CSV no contiene productos.")
    if products[FEATURES].isnull().any().any():
        raise ValueError("Las características no pueden contener valores vacíos.")
    return products


def recommend(
    products: pd.DataFrame,
    features: list[float],
    n_recommendations: int = 5,
) -> pd.DataFrame:
    """Devuelve los productos más cercanos a las características indicadas."""
    if len(features) != len(FEATURES):
        raise ValueError(f"Se requieren {len(FEATURES)} características.")
    if n_recommendations < 1:
        raise ValueError("n_recommendations debe ser mayor que cero.")

    values = products[FEATURES].astype(float)
    scaler = StandardScaler()
    scaled_values = scaler.fit_transform(values)
    query = scaler.transform(pd.DataFrame([features], columns=FEATURES))

    model = NearestNeighbors(n_neighbors=min(n_recommendations, len(products)))
    model.fit(scaled_values)
    _, indexes = model.kneighbors(query)
    return products.iloc[indexes[0]].copy()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Recomienda productos similares.")
    parser.add_argument("features", nargs=3, type=float, metavar="FEATURE")
    parser.add_argument(
        "-k",
        "--number",
        type=int,
        default=5,
        help="Número de recomendaciones",
    )
    parser.add_argument("-f", "--file", default="products.csv", help="Ruta del catálogo CSV")
    args = parser.parse_args()

    catalog = load_products(args.file)
    print(recommend(catalog, args.features, args.number).to_string(index=False))
