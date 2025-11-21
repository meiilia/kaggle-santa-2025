"""Santa 2025 – Christmas Tree Packing Challenge - Collision-Free Solution""""""Santa 2025 – Christmas Tree Packing Challenge baseline solution."""

from __future__ import annotationsfrom __future__ import annotations



import argparseimport argparse

import mathimport math

import osimport os

import randomimport random

from dataclasses import dataclassfrom dataclasses import dataclass

from decimal import Decimal, getcontextfrom pathlib import Path

from pathlib import Pathfrom typing import Dict, Iterable, List, Tuple

from typing import Dict, List, Tuple

import numpy as np

import numpy as npimport pandas as pd

import pandas as pd

from shapely import affinityPoint = Tuple[float, float]

from shapely.geometry import PolygonMetaValue = float | int | str | List[float] | List[int] | Dict[str, float]

from shapely.strtree import STRtreeMetaDict = Dict[str, MetaValue]



# Set high precision for Decimal calculations

getcontext().prec = 50@dataclass

class Params:

Point = Tuple[float, float]    seed: int = 42

    small_n_threshold: int = 12

    medium_n_threshold: int = 80

@dataclass    margin_init: float = 0.15

class Params:    global_scale_min: float = 0.4

    seed: int = 42    binary_search_tol: float = 1e-3

    scale_factor: int = 1000  # Scale factor for high-precision geometry    iterations_small: int = 300

    iterations_medium: int = 500

    iterations_large: int = 800

def set_global_seed(seed: int) -> None:    sa_T0: float = 0.1

    random.seed(seed)    sa_alpha: float = 0.995

    np.random.seed(seed)    move_std_small: float = 0.02

    move_std_medium: float = 0.03

    move_std_large: float = 0.04

class ChristmasTree:    micro_compress_min_factor: float = 0.96

    """    micro_compress_max_factor: float = 1.0

    High-precision Christmas tree representation using shapely Polygon.    micro_compress_steps: int = 8

    Built with Decimal arithmetic and scaled for accurate collision detection.    micro_jitter_std: float = 0.005

    """    max_smallN_pattern: int = 12

        use_partitioned_tiling: bool = False

    def __init__(self, center_x: float, center_y: float, angle: float, scale_factor: int = 1000):    max_runtime_per_shipment: float | None = None

        self.center_x = center_x    

        self.center_y = center_y    # Advanced move sets (probabilities must sum to <= 1.0)

        self.angle = angle    prob_position_move: float = 0.85  # Standard position translation

        self.scale_factor = scale_factor    prob_swap_move: float = 0.10      # Swap two trees

            prob_cluster_move: float = 0.05   # Move a cluster of trees together

        # Define tree shape as a circle (can be customized to actual tree shape)    cluster_size: int = 3              # Size of cluster for cluster moves

        # Using radius = 1.0 as standard    

        radius = Decimal('1.0')    # Annealing schedules: "none", "exp", "linear", "two_stage"

            annealing_schedule: str = "exp"

        # Create circle polygon with high precision    two_stage_transition: float = 0.5  # Fraction of iterations before stage 2

        num_points = 32    

        points = []    # Adaptive iteration counts

        for i in range(num_points):    use_adaptive_iters: bool = False

            theta = Decimal(2 * math.pi * i) / Decimal(num_points)    adaptive_iters_min: int = 200

            x = radius * Decimal(str(math.cos(float(theta))))    adaptive_iters_max: int = 1000

            y = radius * Decimal(str(math.sin(float(theta))))    adaptive_iters_per_tree: float = 5.0  # Base iterations per tree

            points.append((x, y))

        

        # Scale up for precision@dataclass

        scaled_points = [(float(x) * scale_factor, float(y) * scale_factor) for x, y in points]class TreeSpecs:

            footprint_radius: float | None = None

        # Create polygon    half_width: float | None = None

        polygon = Polygon(scaled_points)    half_height: float | None = None

            per_tree_radius: Dict[int, float] | None = None

        # Rotate    safety_margin: float = 0.0

        polygon = affinity.rotate(polygon, angle, origin=(0, 0))

        

        # Translate to center@dataclass

        polygon = affinity.translate(class Shipment:

            polygon,    shipment_id: str

            xoff=center_x * scale_factor,    tree_ids: List[int]

            yoff=center_y * scale_factor    N: int

        )    meta: Dict[str, float] | None = None

        

        self.polygon = polygon

    @dataclass

    def intersects(self, other: 'ChristmasTree') -> bool:class Layout:

        """Check if this tree intersects (overlaps) with another tree."""    shipment_id: str

        return self.polygon.intersects(other.polygon) and not self.polygon.touches(other.polygon)    positions: np.ndarray

    angles: np.ndarray

    box_side: float

def generate_weighted_angle() -> float:    N: int

    """Generate a random angle with weighted distribution."""    tree_ids: List[int]

    if random.random() < 0.7:    meta: MetaDict | None = None

        # 70% chance: angles near multiples of 90 degrees

        base = random.choice([0, 90, 180, 270])

        return (base + random.gauss(0, 5)) % 360def init_default_params() -> Params:

    else:    return Params()

        # 30% chance: uniform random

        return random.uniform(0, 360)

def set_global_seed(seed: int) -> None:

    random.seed(seed)

def initialize_trees(num_trees: int, existing_trees: List[ChristmasTree] | None = None, scale_factor: int = 1000) -> Tuple[List[ChristmasTree], float]:    np.random.seed(seed)

    """

    Initialize trees incrementally with collision-free placement.

    def _derive_trees_from_submission(submission_df: pd.DataFrame) -> pd.DataFrame:

    Args:    ids = submission_df.get("id")

        num_trees: Number of trees to place    if ids is None:

        existing_trees: Previously placed trees to build upon        raise FileNotFoundError("No trees CSV found and submission template lacks 'id' column for fallback")

        scale_factor: Precision scaling factor for geometry    parts = ids.astype(str).str.split("_", expand=True)

        if parts.shape[1] >= 2:

    Returns:        shipment_ids = parts[0]

        Tuple of (list of placed trees, bounding box side length)        tree_tokens = parts[1]

    """    else:

    if existing_trees is None:        shipment_ids = ids.astype(str)

        trees = []        tree_tokens = pd.Series(range(len(ids)), index=ids.index)

    else:    shipment_ids = shipment_ids.astype(str)

        trees = list(existing_trees)    tree_ids = pd.factorize(tree_tokens.astype(str))[0]

        placeholder = pd.DataFrame(

    # Build STRtree for efficient spatial queries        {

    if trees:            "shipment_id": shipment_ids,

        tree_index = STRtree([tree.polygon for tree in trees])            "tree_id": tree_ids,

    else:        }

        tree_index = None    )

        placeholder.sort_values(["shipment_id", "tree_id"], inplace=True)

    # Start radius for new tree placement    placeholder.reset_index(drop=True, inplace=True)

    start_radius = 20.0    return placeholder

    

    for i in range(len(trees), num_trees):

        placed = Falsedef load_data(input_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:

        attempts = 0    input_path = Path(input_dir)

        max_attempts = 1000    submission_candidates = ["sample_submission.csv", "submission_sample.csv"]

            submission_df = None

        while not placed and attempts < max_attempts:    for name in submission_candidates:

            # Generate random angle        file_path = input_path / name

            angle = generate_weighted_angle()        if file_path.exists():

                        submission_df = pd.read_csv(file_path)

            # Start from outer radius and move inward            break

            radius = start_radius    if submission_df is None:

                    submission_df = pd.DataFrame(columns=["id", "x", "y", "deg"])  # TODO: replace with actual template

            while radius > 0 and not placed:

                # Random direction    trees_candidates = ["trees.csv", "train.csv", "train_trees.csv"]

                theta = random.uniform(0, 2 * math.pi)    trees_df = None

                center_x = radius * math.cos(theta)    for name in trees_candidates:

                center_y = radius * math.sin(theta)        file_path = input_path / name

                        if file_path.exists():

                # Create candidate tree            trees_df = pd.read_csv(file_path)

                candidate = ChristmasTree(center_x, center_y, angle, scale_factor)            break

                    if trees_df is None:

                # Check for collisions using STRtree        if submission_df is not None and not submission_df.empty:

                has_collision = False            trees_df = _derive_trees_from_submission(submission_df)

                if tree_index is not None:        else:

                    # Query nearby trees            raise FileNotFoundError("Could not locate trees data CSV in input directory")

                    nearby_polygons = list(tree_index.query(candidate.polygon))

                    for nearby_polygon in nearby_polygons:    return trees_df, submission_df

                        # Find the corresponding tree

                        for existing_tree in trees:

                            if existing_tree.polygon == nearby_polygon:def build_tree_specs(trees_df: pd.DataFrame) -> TreeSpecs:

                                if candidate.intersects(existing_tree):    radius_cols = ["radius", "canopy_radius", "footprint_radius"]

                                    has_collision = True    radius_series = None

                                    break    for col in radius_cols:

                        if has_collision:        if col in trees_df.columns:

                            break            radius_series = trees_df[col].astype(float)

                            break

                if not has_collision:

                    # Found a valid position! Fine-tune by backing off if needed    per_tree_radius: Dict[int, float] | None = None

                    # Move towards origin in small steps to pack tighter    footprint_radius: float | None = None

                    step_size = 0.05

                    while radius > 0:    if radius_series is not None:

                        # Try moving closer        footprint_radius = float(radius_series.max())

                        new_radius = max(0, radius - step_size)        if "tree_id" in trees_df.columns:

                        new_center_x = new_radius * math.cos(theta)            per_tree_radius = dict(zip(trees_df["tree_id"], radius_series))

                        new_center_y = new_radius * math.sin(theta)    else:

                                width_col = next((c for c in ["width", "tree_width"] if c in trees_df.columns), None)

                        test_candidate = ChristmasTree(new_center_x, new_center_y, angle, scale_factor)        height_col = next((c for c in ["height", "tree_height"] if c in trees_df.columns), None)

                                if width_col and height_col:

                        # Check if still collision-free            half_width = float(trees_df[width_col].astype(float).max() / 2)

                        test_collision = False            half_height = float(trees_df[height_col].astype(float).max() / 2)

                        if tree_index is not None:            return TreeSpecs(

                            nearby_polygons = list(tree_index.query(test_candidate.polygon))                footprint_radius=None,

                            for nearby_polygon in nearby_polygons:                half_width=half_width,

                                for existing_tree in trees:                half_height=half_height,

                                    if existing_tree.polygon == nearby_polygon:                per_tree_radius=None,

                                        if test_candidate.intersects(existing_tree):                safety_margin=0.02,

                                            test_collision = True            )

                                            break        # Fallback radius estimate

                                if test_collision:        footprint_radius = 0.5

                                    break

                            return TreeSpecs(

                        if test_collision:        footprint_radius=footprint_radius,

                            # Can't move closer, use previous position        per_tree_radius=per_tree_radius,

                            break        safety_margin=0.02,

                        else:    )

                            # Can move closer

                            candidate = test_candidate

                            radius = new_radiusdef group_trees_into_shipments(trees_df: pd.DataFrame) -> List[Shipment]:

                        if "shipment_id" not in trees_df.columns:

                    # Place the tree        raise KeyError("trees_df must contain a shipment_id column")

                    trees.append(candidate)    if "tree_id" not in trees_df.columns:

                            raise KeyError("trees_df must contain a tree_id column")

                    # Rebuild index with new tree    shipments: List[Shipment] = []

                    tree_index = STRtree([t.polygon for t in trees])    for shipment_id, group in trees_df.groupby("shipment_id"):

                            tree_ids = group["tree_id"].tolist()

                    placed = True        shipments.append(Shipment(shipment_id=str(shipment_id), tree_ids=tree_ids, N=len(tree_ids)))

                else:    shipments.sort(key=lambda s: s.N)

                    # Move inward and try again    return shipments

                    radius -= 0.5

            

            attempts += 1def compute_tree_radius(tree_specs: TreeSpecs, tree_id: int | None = None) -> float:

            if tree_id is not None and tree_specs.per_tree_radius is not None:

        if not placed:        radius = tree_specs.per_tree_radius.get(tree_id)

            # Fallback: place at origin with random perturbation        if radius is not None:

            angle = generate_weighted_angle()            return float(radius + tree_specs.safety_margin)

            center_x = random.uniform(-2, 2)    if tree_specs.footprint_radius is not None:

            center_y = random.uniform(-2, 2)        return float(tree_specs.footprint_radius + tree_specs.safety_margin)

            fallback_tree = ChristmasTree(center_x, center_y, angle, scale_factor)    if tree_specs.half_width is not None and tree_specs.half_height is not None:

            trees.append(fallback_tree)        return float(max(tree_specs.half_width, tree_specs.half_height) + tree_specs.safety_margin)

            tree_index = STRtree([t.polygon for t in trees])    return 0.5 + tree_specs.safety_margin

    

    # Compute bounding box

    min_x = min(t.center_x - 1.0 for t in trees)def vector_distance(p1: np.ndarray, p2: np.ndarray) -> float:

    max_x = max(t.center_x + 1.0 for t in trees)    # Optimized distance calculation avoiding sqrt when possible

    min_y = min(t.center_y - 1.0 for t in trees)    dx = float(p1[0] - p2[0])

    max_y = max(t.center_y + 1.0 for t in trees)    dy = float(p1[1] - p2[1])

        return float(np.sqrt(dx * dx + dy * dy))

    side = max(max_x - min_x, max_y - min_y)

    

    return trees, sidedef trees_overlap(pos1: np.ndarray, pos2: np.ndarray, r1: float, r2: float) -> bool:

    # Optimized: compute squared distance to avoid sqrt

    dx = float(pos1[0] - pos2[0])

def generate_all_configurations(seed: int = 42, scale_factor: int = 1000) -> pd.DataFrame:    dy = float(pos1[1] - pos2[1])

    """    dist_squared = dx * dx + dy * dy

    Generate collision-free configurations for all tree counts (1 to 200).    threshold = (r1 + r2) ** 2

        return dist_squared < threshold

    Args:

        seed: Random seed for reproducibility

        scale_factor: Precision scaling factordef layout_has_collisions(layout: Layout, tree_specs: TreeSpecs) -> bool:

        # Optimized collision detection using vectorized operations and spatial grid

    Returns:    if layout.N < 2:

        DataFrame with columns ['x', 'y', 'deg'] and index as tree ids        return False

    """    

    set_global_seed(seed)    # Pre-compute all radii once (caching optimization)

        radii = np.array([compute_tree_radius(tree_specs, tid) for tid in layout.tree_ids])

    # Build global index    

    index = [f'{n:03d}_{t}' for n in range(1, 201) for t in range(n)]    # For small N, use the original algorithm with pre-computed radii

        if layout.N < 50:

    # Storage for all placements        for i in range(layout.N):

    all_x = []            for j in range(i + 1, layout.N):

    all_y = []                if trees_overlap(layout.positions[i], layout.positions[j], radii[i], radii[j]):

    all_deg = []                    return True

            return False

    existing_trees = None    

        # For larger N, use a spatial grid approach

    for n in range(1, 201):    max_radius = radii.max()

        if n % 20 == 0:    

            print(f"Processing configuration {n}/200...")    # Create spatial grid

            grid_size = max(2.0 * max_radius, layout.box_side / max(10, int(np.sqrt(layout.N))))

        # Generate trees for this configuration    grid_cols = int(np.ceil(layout.box_side / grid_size)) + 1

        trees, side = initialize_trees(n, existing_trees, scale_factor)    grid_rows = int(np.ceil(layout.box_side / grid_size)) + 1

            

        # Store placements for this configuration    # Assign trees to grid cells

        for tree in trees:    grid: Dict[Tuple[int, int], List[int]] = {}

            all_x.append(tree.center_x)    for i in range(layout.N):

            all_y.append(tree.center_y)        x, y = layout.positions[i]

            all_deg.append(tree.angle)        col = int(x / grid_size)

                row = int(y / grid_size)

        # Use these trees as base for next configuration        cell = (row, col)

        existing_trees = trees        if cell not in grid:

                grid[cell] = []

    # Create submission DataFrame        grid[cell].append(i)

    submission = pd.DataFrame({    

        'x': all_x,    # Check collisions only within and between adjacent cells

        'y': all_y,    checked_pairs = set()

        'deg': all_deg    for (row, col), indices in grid.items():

    }, index=index)        # Check within same cell

            for idx_a in range(len(indices)):

    submission.index.name = 'id'            for idx_b in range(idx_a + 1, len(indices)):

                    i = indices[idx_a]

    return submission                j = indices[idx_b]

                if (i, j) not in checked_pairs:

                    checked_pairs.add((i, j))

def validate_submission_no_overlaps(submission: pd.DataFrame, scale_factor: int = 1000) -> None:                    if trees_overlap(layout.positions[i], layout.positions[j], radii[i], radii[j]):

    """                        return True

    Validate that submission has no overlapping trees.        

    Raises AssertionError if overlaps are detected.        # Check with adjacent cells

            for dr in [-1, 0, 1]:

    Args:            for dc in [-1, 0, 1]:

        submission: Submission DataFrame with x, y, deg columns                if dr == 0 and dc == 0:

        scale_factor: Precision scaling factor                    continue

    """                neighbor = (row + dr, col + dc)

    print("Validating submission for overlaps...")                if neighbor in grid:

                        for i in indices:

    # Parse x, y, deg (remove 's' prefix if present)                        for j in grid[neighbor]:

    def parse_value(val):                            if i < j and (i, j) not in checked_pairs:

        if isinstance(val, str) and val.startswith('s'):                                checked_pairs.add((i, j))

            return float(val[1:])                                if trees_overlap(layout.positions[i], layout.positions[j], radii[i], radii[j]):

        return float(val)                                    return True

        return False

    x_values = submission['x'].apply(parse_value).values

    y_values = submission['y'].apply(parse_value).values

    deg_values = submission['deg'].apply(parse_value).valuesdef is_inside_square(pos: np.ndarray, box_side: float, margin: float = 0.0) -> bool:

    ids = submission.index.values    return margin <= float(pos[0]) <= box_side - margin and margin <= float(pos[1]) <= box_side - margin

    

    # Group by configuration (first 3 chars of id)

    configs = {}def layout_respects_bounds(layout: Layout, margin: float = 0.0) -> bool:

    for i, tree_id in enumerate(ids):    for point in layout.positions:

        config_num = tree_id.split('_')[0]        if not is_inside_square(point, layout.box_side, margin):

        if config_num not in configs:            return False

            configs[config_num] = []    return True

        configs[config_num].append((tree_id, x_values[i], y_values[i], deg_values[i]))

    

    # Check each configuration for overlapsdef compute_layout_bounding_box(layout: Layout, tree_specs: TreeSpecs) -> tuple[float, float, float, float]:

    for config_num, trees_data in configs.items():    min_x, max_x = float("inf"), float("-inf")

        # Build trees    min_y, max_y = float("inf"), float("-inf")

        trees = []    for idx, pos in enumerate(layout.positions):

        for tree_id, x, y, deg in trees_data:        radius = compute_tree_radius(tree_specs, layout.tree_ids[idx])

            tree = ChristmasTree(x, y, deg, scale_factor)        min_x = min(min_x, float(pos[0]) - radius)

            trees.append((tree_id, tree))        max_x = max(max_x, float(pos[0]) + radius)

                min_y = min(min_y, float(pos[1]) - radius)

        # Build STRtree        max_y = max(max_y, float(pos[1]) + radius)

        tree_index = STRtree([t[1].polygon for t in trees])    return min_x, max_x, min_y, max_y

        

        # Check all pairs

        for i, (id1, tree1) in enumerate(trees):def compute_box_side(layout: Layout, tree_specs: TreeSpecs) -> float:

            nearby_polygons = list(tree_index.query(tree1.polygon))    min_x, max_x, min_y, max_y = compute_layout_bounding_box(layout, tree_specs)

            for nearby_polygon in nearby_polygons:    span_x = max_x - min_x

                for j, (id2, tree2) in enumerate(trees):    span_y = max_y - min_y

                    if i < j and tree2.polygon == nearby_polygon:    return float(max(span_x, span_y))

                        if tree1.intersects(tree2):

                            raise AssertionError(

                                f"Overlapping trees in group {config_num}: {id1} and {id2}"def is_feasible(layout: Layout, tree_specs: TreeSpecs) -> bool:

                            )    if not layout_respects_bounds(layout):

            return False

    print("✓ No overlaps detected!")    if layout_has_collisions(layout, tree_specs):

        return False

    return True

def format_submission_with_s_prefix(submission: pd.DataFrame) -> pd.DataFrame:

    """

    Format submission DataFrame with 's' prefix as required by Kaggle.def load_smallN_patterns(max_n: int) -> Dict[int, np.ndarray]:

        patterns: Dict[int, np.ndarray] = {}

    Args:    # Patterns are naive placeholders; tune as needed.

        submission: DataFrame with numeric x, y, deg columns    patterns[1] = np.array([[0.5, 0.5, 0.0]])

        patterns[2] = np.array([[0.35, 0.5, 0.0], [0.65, 0.5, 90.0]])

    Returns:    patterns[3] = np.array([[0.5, 0.35, 0.0], [0.35, 0.65, 0.0], [0.65, 0.65, 0.0]])

        DataFrame with s-prefixed string columns    patterns[4] = np.array([[0.3, 0.3, 0.0], [0.7, 0.3, 0.0], [0.3, 0.7, 0.0], [0.7, 0.7, 0.0]])

    """    patterns[5] = np.vstack([patterns[4], np.array([[0.5, 0.5, 0.0]])])

    result = submission.copy()    # TODO: add more refined motifs up to max_n.

        return {n: pat for n, pat in patterns.items() if n <= max_n}

    for col in ['x', 'y', 'deg']:

        # Round to 6 decimals

        result[col] = result[col].astype(float).round(6)def copy_layout(layout: Layout) -> Layout:

        # Convert to string with 's' prefix    return Layout(

        result[col] = 's' + result[col].astype('string')        shipment_id=layout.shipment_id,

            positions=layout.positions.copy(),

    return result        angles=layout.angles.copy(),

        box_side=layout.box_side,

        N=layout.N,

def generate_submission(seed: int = 42, output_path: str | None = None) -> pd.DataFrame:        tree_ids=list(layout.tree_ids),

    """        meta=dict(layout.meta) if layout.meta else None,

    Main entry point: generate collision-free submission.    )

    

    Args:

        seed: Random seed for reproducibilitydef place_using_smallN_pattern(

        output_path: Optional path to save submission CSV    shipment: Shipment, tree_specs: TreeSpecs, pattern: np.ndarray, params: Params

    ) -> Layout:

    Returns:    positions = pattern[:, :2]

        Formatted submission DataFrame    if pattern.shape[1] == 3:

    """        angles = pattern[:, 2]

    print("Generating collision-free tree configurations...")    else:

            angles = np.zeros(len(pattern))

    # Generate all configurations    base_radius = compute_tree_radius(tree_specs, shipment.tree_ids[0])

    submission = generate_all_configurations(seed=seed)    base_side = max(1.0, 2 * base_radius * math.sqrt(shipment.N))

        interior_side = base_side * (1.0 - params.margin_init)

    # Validate no overlaps (using numeric values)    offset = (base_side - interior_side) / 2.0

    validate_submission_no_overlaps(submission)    scaled_positions = positions * interior_side + offset

        layout = Layout(

    # Format with 's' prefix        shipment_id=shipment.shipment_id,

    submission_formatted = format_submission_with_s_prefix(submission)        positions=scaled_positions.astype(float),

            angles=np.mod(angles, 360.0),

    # Save if path provided        box_side=base_side,

    if output_path:        N=shipment.N,

        submission_formatted.to_csv(output_path, index=True)        tree_ids=list(shipment.tree_ids),

        print(f"✓ Submission saved to {output_path}")    )

        layout.box_side = max(layout.box_side, compute_box_side(layout, tree_specs))

    return submission_formatted    return layout





def parse_args() -> argparse.Namespace:def compute_rows_cols_for_N(N: int, dx: float, dy: float) -> tuple[int, int]:

    parser = argparse.ArgumentParser(description="Santa 2025 collision-free solution")    cols = max(1, int(math.ceil(math.sqrt(N))))

    parser.add_argument("--output", type=str, default="submission.csv", help="Output CSV path")    rows = int(math.ceil(N / cols))

    parser.add_argument("--seed", type=int, default=42, help="Random seed")    return rows, cols

    return parser.parse_args()



def generate_hex_grid_positions(N: int, radius: float) -> np.ndarray:

if __name__ == "__main__":    positions: List[Point] = []

    args = parse_args()    dx = 2 * radius

    submission = generate_submission(seed=args.seed, output_path=args.output)    dy = math.sqrt(3) * radius

    print(f"Generated submission with {len(submission)} tree placements")    rows, cols = compute_rows_cols_for_N(N, dx, dy)

    for r in range(rows):
        for c in range(cols):
            if len(positions) >= N:
                break
            x = c * dx + (radius if r % 2 else 0.0)
            y = r * dy
            positions.append((x, y))
        if len(positions) >= N:
            break
    arr = np.array(positions, dtype=float)
    arr -= np.mean(arr, axis=0, keepdims=True)
    return arr


def place_using_hex_tiling(shipment: Shipment, tree_specs: TreeSpecs, params: Params) -> Layout:
    base_radius = compute_tree_radius(tree_specs, shipment.tree_ids[0])
    spacing = 2.0 * base_radius * (1.0 + params.margin_init)
    raw_positions = generate_hex_grid_positions(shipment.N, spacing)
    min_x, max_x = raw_positions[:, 0].min(), raw_positions[:, 0].max()
    min_y, max_y = raw_positions[:, 1].min(), raw_positions[:, 1].max()
    width = max_x - min_x + 2 * spacing
    height = max_y - min_y + 2 * spacing
    side = max(width, height)
    shifted = raw_positions - np.array([min_x, min_y]) + spacing
    if side <= 0:
        side = spacing * max(2, shipment.N)
    layout = Layout(
        shipment_id=shipment.shipment_id,
        positions=shifted,
        angles=np.zeros(shipment.N, dtype=float),
        box_side=side,
        N=shipment.N,
        tree_ids=list(shipment.tree_ids),
    )
    layout.box_side = max(layout.box_side, compute_box_side(layout, tree_specs) * (1 + params.margin_init))
    return layout


def place_using_partitioned_tiling(
    shipment: Shipment, tree_specs: TreeSpecs, params: Params
) -> Layout:
    partitions = max(1, int(math.sqrt(shipment.N / 64.0)))
    base_layout = place_using_hex_tiling(shipment, tree_specs, params)
    if partitions <= 1:
        return base_layout
    positions = base_layout.positions
    side = base_layout.box_side
    partition_size = side / partitions
    for idx, pos in enumerate(positions):
        block = idx % partitions
        offset = block * partition_size
        positions[idx, 0] = max(params.margin_init, min(side - params.margin_init, offset + pos[0] % partition_size))
        positions[idx, 1] = max(params.margin_init, min(side - params.margin_init, pos[1]))
    base_layout.positions = positions
    return base_layout


def place_using_deterministic_tiling(
    shipment: Shipment, tree_specs: TreeSpecs, params: Params
) -> Layout:
    """
    TODO: Deterministic tiling strategy inspired by public insights.
    Implement optimal circle packing patterns for specific N values,
    or lattice-based arrangements with proven optimal/near-optimal density.
    
    For now, falls back to hex tiling.
    """
    # TODO: Add deterministic patterns for specific N values
    # E.g., for N=7, use optimal circle packing configuration
    # For N=19, use hexagonal lattice with specific offsets, etc.
    return place_using_hex_tiling(shipment, tree_specs, params)


def apply_smallN_translation(layout: Layout, tree_specs: TreeSpecs) -> Layout:
    """
    TODO: Small-N translation optimization inspired by public notebooks.
    After initial placement, try systematic translations of the entire
    configuration to find positions that allow tighter packing.
    
    For now, returns layout unchanged.
    """
    # TODO: Implement grid search over small translations
    # Try shifting entire layout by small increments in x and y
    # Keep configuration that minimizes bounding box
    return layout


def initial_placement_for_shipment(
    shipment: Shipment,
    tree_specs: TreeSpecs,
    params: Params,
    patterns_smallN: Dict[int, np.ndarray] | None,
) -> Layout:
    if shipment.N <= params.small_n_threshold and patterns_smallN:
        pattern = patterns_smallN.get(shipment.N)
        if pattern is not None:
            return place_using_smallN_pattern(shipment, tree_specs, pattern, params)
    if params.use_partitioned_tiling and shipment.N > params.medium_n_threshold:
        return place_using_partitioned_tiling(shipment, tree_specs, params)
    return place_using_hex_tiling(shipment, tree_specs, params)


def rescale_layout(layout: Layout, scale: float) -> Layout:
    new_layout = copy_layout(layout)
    center = new_layout.box_side / 2.0
    new_layout.positions = (new_layout.positions - center) * scale + center
    new_layout.box_side *= scale
    return new_layout


def compress_layout_global(layout: Layout, tree_specs: TreeSpecs, params: Params) -> Layout:
    low, high = params.global_scale_min, 1.0
    best_layout = layout
    while high - low > params.binary_search_tol:
        mid = (low + high) / 2.0
        candidate = rescale_layout(layout, mid)
        if is_feasible(candidate, tree_specs):
            best_layout = candidate
            high = mid
        else:
            low = mid
    return best_layout


def num_iterations_for_N(N: int, params: Params) -> int:
    if params.use_adaptive_iters:
        # Adaptive: scale with N
        iters = int(params.adaptive_iters_per_tree * N)
        return max(params.adaptive_iters_min, min(iters, params.adaptive_iters_max))
    else:
        # Fixed thresholds
        if N <= params.small_n_threshold:
            return params.iterations_small
        if N <= params.medium_n_threshold:
            return params.iterations_medium
        return params.iterations_large


def num_iterations_for_shipment(N: int, params: Params) -> int:
    """Alias for num_iterations_for_N for clarity in adaptive iteration context."""
    return num_iterations_for_N(N, params)


def move_std_for_N(N: int, params: Params) -> float:
    if N <= params.small_n_threshold:
        return params.move_std_small
    if N <= params.medium_n_threshold:
        return params.move_std_medium
    return params.move_std_large


def select_tree_index_for_move(layout: Layout, rng: np.random.Generator) -> int:
    return int(rng.integers(0, layout.N))


def propose_move_position(
    layout: Layout, tree_specs: TreeSpecs, params: Params, rng: np.random.Generator
) -> Layout:
    """Standard position move: translate one tree by (dx, dy)."""
    candidate = copy_layout(layout)
    idx = select_tree_index_for_move(candidate, rng)
    std = move_std_for_N(candidate.N, params) * candidate.box_side
    delta = rng.normal(loc=0.0, scale=std, size=2)
    candidate.positions[idx] += delta
    candidate.positions[idx, 0] = float(np.clip(candidate.positions[idx, 0], 0.0, candidate.box_side))
    candidate.positions[idx, 1] = float(np.clip(candidate.positions[idx, 1], 0.0, candidate.box_side))
    d_angle = float(rng.normal(0.0, 5.0))
    candidate.angles[idx] = (candidate.angles[idx] + d_angle) % 360.0
    candidate.box_side = max(candidate.box_side, compute_box_side(candidate, tree_specs))
    return candidate


def propose_move_swap(
    layout: Layout, tree_specs: TreeSpecs, params: Params, rng: np.random.Generator
) -> Layout:
    """Swap move: exchange positions of two randomly selected trees."""
    if layout.N < 2:
        return copy_layout(layout)
    
    candidate = copy_layout(layout)
    idx1 = int(rng.integers(0, candidate.N))
    idx2 = int(rng.integers(0, candidate.N))
    
    # Ensure different indices
    while idx2 == idx1 and candidate.N > 1:
        idx2 = int(rng.integers(0, candidate.N))
    
    # Swap positions
    candidate.positions[idx1], candidate.positions[idx2] = (
        candidate.positions[idx2].copy(),
        candidate.positions[idx1].copy()
    )
    
    # Optionally swap angles too
    candidate.angles[idx1], candidate.angles[idx2] = candidate.angles[idx2], candidate.angles[idx1]
    
    candidate.box_side = max(candidate.box_side, compute_box_side(candidate, tree_specs))
    return candidate


def propose_move_cluster(
    layout: Layout, tree_specs: TreeSpecs, params: Params, rng: np.random.Generator
) -> Layout:
    """Cluster move: move a small group of trees together by (dx, dy)."""
    if layout.N < 2:
        return propose_move_position(layout, tree_specs, params, rng)
    
    candidate = copy_layout(layout)
    
    # Select cluster size (min 2, max cluster_size param or N)
    actual_cluster_size = min(params.cluster_size, candidate.N)
    actual_cluster_size = max(2, actual_cluster_size)
    
    # Select a random seed tree
    seed_idx = int(rng.integers(0, candidate.N))
    
    # Find nearest neighbors (simple: select random trees or distance-based)
    # For simplicity: select random subset including seed
    cluster_indices = [seed_idx]
    remaining = [i for i in range(candidate.N) if i != seed_idx]
    remaining_array = np.array(remaining)
    rng.shuffle(remaining_array)
    cluster_indices.extend(remaining_array[:actual_cluster_size-1].tolist())
    
    # Apply same translation to all in cluster
    std = move_std_for_N(candidate.N, params) * candidate.box_side
    delta = rng.normal(loc=0.0, scale=std, size=2)
    
    for idx in cluster_indices:
        candidate.positions[idx] += delta
        candidate.positions[idx, 0] = float(np.clip(candidate.positions[idx, 0], 0.0, candidate.box_side))
        candidate.positions[idx, 1] = float(np.clip(candidate.positions[idx, 1], 0.0, candidate.box_side))
    
    candidate.box_side = max(candidate.box_side, compute_box_side(candidate, tree_specs))
    return candidate


def propose_random_move(
    layout: Layout, tree_specs: TreeSpecs, params: Params, rng: np.random.Generator
) -> Layout:
    """Select and apply a random move based on configured probabilities."""
    # Normalize probabilities
    total_prob = params.prob_position_move + params.prob_swap_move + params.prob_cluster_move
    if total_prob <= 0:
        total_prob = 1.0
    
    rand_val = rng.random() * total_prob
    
    if rand_val < params.prob_position_move:
        return propose_move_position(layout, tree_specs, params, rng)
    elif rand_val < params.prob_position_move + params.prob_swap_move:
        return propose_move_swap(layout, tree_specs, params, rng)
    else:
        return propose_move_cluster(layout, tree_specs, params, rng)


def local_search_optimize(
    layout: Layout, tree_specs: TreeSpecs, params: Params, rng: np.random.Generator
) -> Layout:
    best_layout = copy_layout(layout)
    best_score = compute_box_side(best_layout, tree_specs)
    current_layout = copy_layout(layout)
    current_score = best_score
    iterations = num_iterations_for_N(layout.N, params)
    
    # Initialize temperature based on schedule
    temperature = params.sa_T0
    
    for iteration in range(iterations):
        candidate = propose_random_move(current_layout, tree_specs, params, rng)
        if not is_feasible(candidate, tree_specs):
            # Update temperature even on infeasible moves
            temperature = _update_temperature(temperature, iteration, iterations, params)
            continue
        
        candidate_score = compute_box_side(candidate, tree_specs)
        delta = candidate_score - current_score
        accept = False
        
        if delta <= 0:
            accept = True
        else:
            # Accept worse moves based on temperature
            if temperature > 0:
                prob = math.exp(-delta / max(temperature, 1e-6))
                if rng.random() < prob:
                    accept = True
            # else: temperature is 0, reject all worse moves (hill climbing)
        
        if accept:
            current_layout = candidate
            current_score = candidate_score
            if candidate_score < best_score:
                best_layout = copy_layout(candidate)
                best_score = candidate_score
        
        # Update temperature
        temperature = _update_temperature(temperature, iteration, iterations, params)
    
    best_layout.box_side = max(best_layout.box_side, best_score)
    return best_layout


def _update_temperature(temperature: float, iteration: int, total_iterations: int, params: Params) -> float:
    """Update temperature according to the configured annealing schedule."""
    schedule = params.annealing_schedule.lower()
    
    if schedule == "none":
        # Pure hill climbing: no annealing
        return 0.0
    
    elif schedule == "exp":
        # Exponential decay
        return temperature * params.sa_alpha
    
    elif schedule == "linear":
        # Linear decay from sa_T0 to 0
        progress = iteration / max(total_iterations - 1, 1)
        return params.sa_T0 * (1.0 - progress)
    
    elif schedule == "two_stage":
        # Two-stage: high temp for first part, low temp for second part
        transition_iter = int(total_iterations * params.two_stage_transition)
        if iteration < transition_iter:
            # Stage 1: coarse search with high temperature
            return params.sa_T0
        else:
            # Stage 2: fine search with exponential decay
            stage2_iter = iteration - transition_iter
            stage2_total = total_iterations - transition_iter
            # Start from sa_T0 and decay
            return params.sa_T0 * (params.sa_alpha ** stage2_iter)
    
    else:
        # Default to exponential if unknown schedule
        return temperature * params.sa_alpha


def recompute_exact_bounding_box(layout: Layout, tree_specs: TreeSpecs) -> Layout:
    updated = copy_layout(layout)
    min_x, max_x, min_y, max_y = compute_layout_bounding_box(updated, tree_specs)
    width = max_x - min_x
    height = max_y - min_y
    side = max(width, height)
    shift_x = -min_x + (side - width) / 2.0
    shift_y = -min_y + (side - height) / 2.0
    updated.positions[:, 0] += shift_x
    updated.positions[:, 1] += shift_y
    updated.box_side = side
    return updated


def micro_compress(layout: Layout, tree_specs: TreeSpecs, params: Params) -> Layout:
    best_layout = copy_layout(layout)
    factors = np.linspace(
        params.micro_compress_min_factor,
        params.micro_compress_max_factor,
        params.micro_compress_steps,
    )
    for factor in factors:
        candidate = rescale_layout(best_layout, factor)
        if is_feasible(candidate, tree_specs):
            best_layout = candidate
    return best_layout


def micro_jitter(layout: Layout, tree_specs: TreeSpecs, params: Params, rng: np.random.Generator) -> Layout:
    best_layout = copy_layout(layout)
    best_score = compute_box_side(best_layout, tree_specs)
    attempts = min(10 * layout.N, 200)
    for _ in range(attempts):
        candidate = copy_layout(best_layout)
        idx = select_tree_index_for_move(candidate, rng)
        jitter = rng.normal(scale=params.micro_jitter_std * candidate.box_side, size=2)
        candidate.positions[idx] += jitter
        candidate.positions[idx] = np.clip(candidate.positions[idx], 0.0, candidate.box_side)
        if not is_feasible(candidate, tree_specs):
            continue
        score = compute_box_side(candidate, tree_specs)
        if score + 1e-6 < best_score:
            best_layout = candidate
            best_score = score
    return best_layout


def postprocess_layout(
    layout: Layout, tree_specs: TreeSpecs, params: Params, rng: np.random.Generator
) -> Layout:
    updated = recompute_exact_bounding_box(layout, tree_specs)
    updated = micro_compress(updated, tree_specs, params)
    updated = micro_jitter(updated, tree_specs, params, rng)
    updated.box_side = compute_box_side(updated, tree_specs)
    return updated


def compute_normalized_area_for_shipment(layout: Layout, tree_specs: TreeSpecs) -> float:
    # TODO: replace with official normalization from competition host.
    return float(layout.box_side ** 2)


def evaluate_shipment(layout: Layout, tree_specs: TreeSpecs) -> float:
    if not is_feasible(layout, tree_specs):
        return compute_normalized_area_for_shipment(layout, tree_specs) + 1e6
    return compute_normalized_area_for_shipment(layout, tree_specs)


def evaluate_solution(layouts: Dict[str, Layout], tree_specs: TreeSpecs) -> float:
    score = 0.0
    for layout in layouts.values():
        score += evaluate_shipment(layout, tree_specs)
    return score


def solve_shipment(
    shipment: Shipment,
    tree_specs: TreeSpecs,
    params: Params,
    patterns_smallN: Dict[int, np.ndarray],
    rng: np.random.Generator,
) -> Layout:
    layout = initial_placement_for_shipment(shipment, tree_specs, params, patterns_smallN)
    layout = compress_layout_global(layout, tree_specs, params)
    layout = local_search_optimize(layout, tree_specs, params, rng)
    layout = postprocess_layout(layout, tree_specs, params, rng)
    return layout


def build_submission_df(layouts: Dict[str, Layout], submission_template: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, float | str | int]] = []
    for shipment_id, layout in layouts.items():
        for idx, tree_id in enumerate(layout.tree_ids):
            x, y = layout.positions[idx]
            angle = layout.angles[idx]
            rows.append(
                {
                    "id": f"{shipment_id}_{tree_id}",
                    "shipment_id": shipment_id,
                    "tree_id": tree_id,
                    "x": f"s{float(x)}",    # Format required by Kaggle: 's' prefix
                    "y": f"s{float(y)}",    # Format required by Kaggle: 's' prefix
                    "deg": f"s{float(angle)}",  # Format required by Kaggle: 's' prefix
                }
            )
    result = pd.DataFrame(rows)
    missing_cols = [col for col in submission_template.columns if col not in result.columns]
    for col in missing_cols:
        if col in submission_template.columns and not submission_template.empty:
            result[col] = submission_template[col].iloc[0]
        else:
            result[col] = np.nan
    ordered_cols = [col for col in submission_template.columns if col in result.columns]
    if ordered_cols:
        result = result[ordered_cols]
    return result


def detect_input_dir() -> str:
    candidates = [
        "/kaggle/input/santa-2025-christmas-tree-packing-challenge",
        "/kaggle/input/santa-2025-christmas-tree-packing-challenge/train",
        os.getcwd(),
        str(Path(__file__).resolve().parent),
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return os.getcwd()


def run_full_inference(input_dir: str, output_path: str, params: Params) -> float:
    set_global_seed(params.seed)
    trees_df, submission_template = load_data(input_dir)
    tree_specs = build_tree_specs(trees_df)
    shipments = group_trees_into_shipments(trees_df)
    patterns = load_smallN_patterns(params.max_smallN_pattern)
    rng = np.random.default_rng(params.seed)
    layouts: Dict[str, Layout] = {}
    for shipment in shipments:
        layout = solve_shipment(shipment, tree_specs, params, patterns, rng)
        layouts[shipment.shipment_id] = layout
    submission_df = build_submission_df(layouts, submission_template)
    submission_df.to_csv(output_path, index=False)
    score = evaluate_solution(layouts, tree_specs)
    return score


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Santa 2025 baseline solution")
    parser.add_argument("--input-dir", type=str, default=None, help="Input directory with competition data")
    parser.add_argument("--output-path", type=str, default="submission.csv", help="Output CSV path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed override")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    params = init_default_params()
    if args.seed is not None:
        params.seed = args.seed
    input_dir = args.input_dir or detect_input_dir()
    score = run_full_inference(input_dir=input_dir, output_path=args.output_path, params=params)
    print(f"Local score estimate: {score:.4f}")
