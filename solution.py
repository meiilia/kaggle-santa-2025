"""Santa 2025 – Christmas Tree Packing Challenge baseline solution."""
from __future__ import annotations

import argparse
import math
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

Point = Tuple[float, float]
MetaValue = float | int | str | List[float] | List[int] | Dict[str, float]
MetaDict = Dict[str, MetaValue]


@dataclass
class Params:
    seed: int = 42
    small_n_threshold: int = 12
    medium_n_threshold: int = 80
    margin_init: float = 0.15
    global_scale_min: float = 0.4
    binary_search_tol: float = 1e-3
    iterations_small: int = 300
    iterations_medium: int = 500
    iterations_large: int = 800
    sa_T0: float = 0.1
    sa_alpha: float = 0.995
    move_std_small: float = 0.02
    move_std_medium: float = 0.03
    move_std_large: float = 0.04
    micro_compress_min_factor: float = 0.96
    micro_compress_max_factor: float = 1.0
    micro_compress_steps: int = 8
    micro_jitter_std: float = 0.005
    max_smallN_pattern: int = 12
    use_partitioned_tiling: bool = False
    max_runtime_per_shipment: float | None = None
    
    # Advanced move sets (probabilities must sum to <= 1.0)
    prob_position_move: float = 0.85  # Standard position translation
    prob_swap_move: float = 0.10      # Swap two trees
    prob_cluster_move: float = 0.05   # Move a cluster of trees together
    cluster_size: int = 3              # Size of cluster for cluster moves
    
    # Annealing schedules: "none", "exp", "linear", "two_stage"
    annealing_schedule: str = "exp"
    two_stage_transition: float = 0.5  # Fraction of iterations before stage 2
    
    # Adaptive iteration counts
    use_adaptive_iters: bool = False
    adaptive_iters_min: int = 200
    adaptive_iters_max: int = 1000
    adaptive_iters_per_tree: float = 5.0  # Base iterations per tree


@dataclass
class TreeSpecs:
    footprint_radius: float | None = None
    half_width: float | None = None
    half_height: float | None = None
    per_tree_radius: Dict[int, float] | None = None
    safety_margin: float = 0.0


@dataclass
class Shipment:
    shipment_id: str
    tree_ids: List[int]
    N: int
    meta: Dict[str, float] | None = None


@dataclass
class Layout:
    shipment_id: str
    positions: np.ndarray
    angles: np.ndarray
    box_side: float
    N: int
    tree_ids: List[int]
    meta: MetaDict | None = None


def init_default_params() -> Params:
    return Params()


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def _derive_trees_from_submission(submission_df: pd.DataFrame) -> pd.DataFrame:
    ids = submission_df.get("id")
    if ids is None:
        raise FileNotFoundError("No trees CSV found and submission template lacks 'id' column for fallback")
    parts = ids.astype(str).str.split("_", expand=True)
    if parts.shape[1] >= 2:
        shipment_ids = parts[0]
        tree_tokens = parts[1]
    else:
        shipment_ids = ids.astype(str)
        tree_tokens = pd.Series(range(len(ids)), index=ids.index)
    shipment_ids = shipment_ids.astype(str)
    tree_ids = pd.factorize(tree_tokens.astype(str))[0]
    placeholder = pd.DataFrame(
        {
            "shipment_id": shipment_ids,
            "tree_id": tree_ids,
        }
    )
    placeholder.sort_values(["shipment_id", "tree_id"], inplace=True)
    placeholder.reset_index(drop=True, inplace=True)
    return placeholder


def load_data(input_dir: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    input_path = Path(input_dir)
    submission_candidates = ["sample_submission.csv", "submission_sample.csv"]
    submission_df = None
    for name in submission_candidates:
        file_path = input_path / name
        if file_path.exists():
            submission_df = pd.read_csv(file_path)
            break
    if submission_df is None:
        submission_df = pd.DataFrame(columns=["id", "x", "y", "deg"])  # TODO: replace with actual template

    trees_candidates = ["trees.csv", "train.csv", "train_trees.csv"]
    trees_df = None
    for name in trees_candidates:
        file_path = input_path / name
        if file_path.exists():
            trees_df = pd.read_csv(file_path)
            break
    if trees_df is None:
        if submission_df is not None and not submission_df.empty:
            trees_df = _derive_trees_from_submission(submission_df)
        else:
            raise FileNotFoundError("Could not locate trees data CSV in input directory")

    return trees_df, submission_df


def build_tree_specs(trees_df: pd.DataFrame) -> TreeSpecs:
    radius_cols = ["radius", "canopy_radius", "footprint_radius"]
    radius_series = None
    for col in radius_cols:
        if col in trees_df.columns:
            radius_series = trees_df[col].astype(float)
            break

    per_tree_radius: Dict[int, float] | None = None
    footprint_radius: float | None = None

    if radius_series is not None:
        footprint_radius = float(radius_series.max())
        if "tree_id" in trees_df.columns:
            per_tree_radius = dict(zip(trees_df["tree_id"], radius_series))
    else:
        width_col = next((c for c in ["width", "tree_width"] if c in trees_df.columns), None)
        height_col = next((c for c in ["height", "tree_height"] if c in trees_df.columns), None)
        if width_col and height_col:
            half_width = float(trees_df[width_col].astype(float).max() / 2)
            half_height = float(trees_df[height_col].astype(float).max() / 2)
            return TreeSpecs(
                footprint_radius=None,
                half_width=half_width,
                half_height=half_height,
                per_tree_radius=None,
                safety_margin=0.02,
            )
        # Fallback radius estimate
        footprint_radius = 0.5

    return TreeSpecs(
        footprint_radius=footprint_radius,
        per_tree_radius=per_tree_radius,
        safety_margin=0.02,
    )


def group_trees_into_shipments(trees_df: pd.DataFrame) -> List[Shipment]:
    if "shipment_id" not in trees_df.columns:
        raise KeyError("trees_df must contain a shipment_id column")
    if "tree_id" not in trees_df.columns:
        raise KeyError("trees_df must contain a tree_id column")
    shipments: List[Shipment] = []
    for shipment_id, group in trees_df.groupby("shipment_id"):
        tree_ids = group["tree_id"].tolist()
        shipments.append(Shipment(shipment_id=str(shipment_id), tree_ids=tree_ids, N=len(tree_ids)))
    shipments.sort(key=lambda s: s.N)
    return shipments


def compute_tree_radius(tree_specs: TreeSpecs, tree_id: int | None = None) -> float:
    if tree_id is not None and tree_specs.per_tree_radius is not None:
        radius = tree_specs.per_tree_radius.get(tree_id)
        if radius is not None:
            return float(radius + tree_specs.safety_margin)
    if tree_specs.footprint_radius is not None:
        return float(tree_specs.footprint_radius + tree_specs.safety_margin)
    if tree_specs.half_width is not None and tree_specs.half_height is not None:
        return float(max(tree_specs.half_width, tree_specs.half_height) + tree_specs.safety_margin)
    return 0.5 + tree_specs.safety_margin


def vector_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    # Optimized distance calculation avoiding sqrt when possible
    dx = float(p1[0] - p2[0])
    dy = float(p1[1] - p2[1])
    return float(np.sqrt(dx * dx + dy * dy))


def trees_overlap(pos1: np.ndarray, pos2: np.ndarray, r1: float, r2: float) -> bool:
    # Optimized: compute squared distance to avoid sqrt
    dx = float(pos1[0] - pos2[0])
    dy = float(pos1[1] - pos2[1])
    dist_squared = dx * dx + dy * dy
    threshold = (r1 + r2) ** 2
    return dist_squared < threshold


def layout_has_collisions(layout: Layout, tree_specs: TreeSpecs) -> bool:
    # Optimized collision detection using vectorized operations and spatial grid
    if layout.N < 2:
        return False
    
    # Pre-compute all radii once (caching optimization)
    radii = np.array([compute_tree_radius(tree_specs, tid) for tid in layout.tree_ids])
    
    # For small N, use the original algorithm with pre-computed radii
    if layout.N < 50:
        for i in range(layout.N):
            for j in range(i + 1, layout.N):
                if trees_overlap(layout.positions[i], layout.positions[j], radii[i], radii[j]):
                    return True
        return False
    
    # For larger N, use a spatial grid approach
    max_radius = radii.max()
    
    # Create spatial grid
    grid_size = max(2.0 * max_radius, layout.box_side / max(10, int(np.sqrt(layout.N))))
    grid_cols = int(np.ceil(layout.box_side / grid_size)) + 1
    grid_rows = int(np.ceil(layout.box_side / grid_size)) + 1
    
    # Assign trees to grid cells
    grid: Dict[Tuple[int, int], List[int]] = {}
    for i in range(layout.N):
        x, y = layout.positions[i]
        col = int(x / grid_size)
        row = int(y / grid_size)
        cell = (row, col)
        if cell not in grid:
            grid[cell] = []
        grid[cell].append(i)
    
    # Check collisions only within and between adjacent cells
    checked_pairs = set()
    for (row, col), indices in grid.items():
        # Check within same cell
        for idx_a in range(len(indices)):
            for idx_b in range(idx_a + 1, len(indices)):
                i = indices[idx_a]
                j = indices[idx_b]
                if (i, j) not in checked_pairs:
                    checked_pairs.add((i, j))
                    if trees_overlap(layout.positions[i], layout.positions[j], radii[i], radii[j]):
                        return True
        
        # Check with adjacent cells
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                neighbor = (row + dr, col + dc)
                if neighbor in grid:
                    for i in indices:
                        for j in grid[neighbor]:
                            if i < j and (i, j) not in checked_pairs:
                                checked_pairs.add((i, j))
                                if trees_overlap(layout.positions[i], layout.positions[j], radii[i], radii[j]):
                                    return True
    return False


def is_inside_square(pos: np.ndarray, box_side: float, margin: float = 0.0) -> bool:
    return margin <= float(pos[0]) <= box_side - margin and margin <= float(pos[1]) <= box_side - margin


def layout_respects_bounds(layout: Layout, margin: float = 0.0) -> bool:
    for point in layout.positions:
        if not is_inside_square(point, layout.box_side, margin):
            return False
    return True


def compute_layout_bounding_box(layout: Layout, tree_specs: TreeSpecs) -> tuple[float, float, float, float]:
    min_x, max_x = float("inf"), float("-inf")
    min_y, max_y = float("inf"), float("-inf")
    for idx, pos in enumerate(layout.positions):
        radius = compute_tree_radius(tree_specs, layout.tree_ids[idx])
        min_x = min(min_x, float(pos[0]) - radius)
        max_x = max(max_x, float(pos[0]) + radius)
        min_y = min(min_y, float(pos[1]) - radius)
        max_y = max(max_y, float(pos[1]) + radius)
    return min_x, max_x, min_y, max_y


def compute_box_side(layout: Layout, tree_specs: TreeSpecs) -> float:
    min_x, max_x, min_y, max_y = compute_layout_bounding_box(layout, tree_specs)
    span_x = max_x - min_x
    span_y = max_y - min_y
    return float(max(span_x, span_y))


def is_feasible(layout: Layout, tree_specs: TreeSpecs) -> bool:
    if not layout_respects_bounds(layout):
        return False
    if layout_has_collisions(layout, tree_specs):
        return False
    return True


def load_smallN_patterns(max_n: int) -> Dict[int, np.ndarray]:
    patterns: Dict[int, np.ndarray] = {}
    # Patterns with proper spacing for circles that don't overlap
    # Using normalized coordinates (0-1), will be scaled appropriately
    patterns[1] = np.array([[0.5, 0.5, 0.0]])
    # N=2: horizontal line with spacing
    patterns[2] = np.array([[0.3, 0.5, 0.0], [0.7, 0.5, 90.0]])
    # N=3: triangular arrangement
    patterns[3] = np.array([[0.5, 0.3, 0.0], [0.25, 0.7, 0.0], [0.75, 0.7, 0.0]])
    # N=4: square arrangement with wider spacing
    patterns[4] = np.array([[0.25, 0.25, 0.0], [0.75, 0.25, 90.0], [0.25, 0.75, 180.0], [0.75, 0.75, 270.0]])
    # N=5: 4-corners + center, with proper clearance
    patterns[5] = np.array([[0.2, 0.2, 0.0], [0.8, 0.2, 90.0], [0.2, 0.8, 180.0], [0.8, 0.8, 270.0], [0.5, 0.5, 0.0]])
    # TODO: add more refined motifs up to max_n.
    return {n: pat for n, pat in patterns.items() if n <= max_n}


def copy_layout(layout: Layout) -> Layout:
    return Layout(
        shipment_id=layout.shipment_id,
        positions=layout.positions.copy(),
        angles=layout.angles.copy(),
        box_side=layout.box_side,
        N=layout.N,
        tree_ids=list(layout.tree_ids),
        meta=dict(layout.meta) if layout.meta else None,
    )


def place_using_smallN_pattern(
    shipment: Shipment, tree_specs: TreeSpecs, pattern: np.ndarray, params: Params
) -> Layout:
    positions = pattern[:, :2]
    if pattern.shape[1] == 3:
        angles = pattern[:, 2]
    else:
        angles = np.zeros(len(pattern))
    base_radius = compute_tree_radius(tree_specs, shipment.tree_ids[0])
    
    # Calculate minimum distance between any two points in the pattern
    min_pattern_dist = float('inf')
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dist = np.linalg.norm(positions[i] - positions[j])
            min_pattern_dist = min(min_pattern_dist, dist)
    
    if min_pattern_dist == float('inf'):
        min_pattern_dist = 1.0  # Single tree
    
    # Scale so that minimum distance in pattern = 2 * radius * (1 + margin)
    # Add extra safety factor for Kaggle's numerical precision
    safety_factor = 1.02  # 2% extra spacing for safety
    required_min_dist = 2 * base_radius * (1.0 + params.margin_init) * safety_factor
    scale_factor = required_min_dist / min_pattern_dist if min_pattern_dist > 0 else required_min_dist
    
    # Scale positions
    scaled_positions = positions * scale_factor
    
    # Compute box side to contain all positions with padding
    max_coord = np.max(scaled_positions)
    min_coord = np.min(scaled_positions)
    base_side = max_coord - min_coord + 2 * required_min_dist
    
    # Center the positions
    offset = (base_side - (max_coord - min_coord)) / 2.0 - min_coord
    scaled_positions = scaled_positions + offset
    layout = Layout(
        shipment_id=shipment.shipment_id,
        positions=scaled_positions.astype(float),
        angles=np.mod(angles, 360.0),
        box_side=base_side,
        N=shipment.N,
        tree_ids=list(shipment.tree_ids),
    )
    # Don't call compute_box_side here - it might compress too much
    # The box_side is already correctly calculated above
    return layout


def compute_rows_cols_for_N(N: int, dx: float, dy: float) -> tuple[int, int]:
    cols = max(1, int(math.ceil(math.sqrt(N))))
    rows = int(math.ceil(N / cols))
    return rows, cols


def generate_hex_grid_positions(N: int, radius: float) -> np.ndarray:
    positions: List[Point] = []
    dx = 2 * radius
    dy = math.sqrt(3) * radius
    rows, cols = compute_rows_cols_for_N(N, dx, dy)
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
    # Generate hex grid with proper spacing: radius with margin added
    effective_radius = base_radius * (1.0 + params.margin_init)
    raw_positions = generate_hex_grid_positions(shipment.N, effective_radius)
    min_x, max_x = raw_positions[:, 0].min(), raw_positions[:, 0].max()
    min_y, max_y = raw_positions[:, 1].min(), raw_positions[:, 1].max()
    padding = 2 * effective_radius
    width = max_x - min_x + padding
    height = max_y - min_y + padding
    side = max(width, height)
    shifted = raw_positions - np.array([min_x, min_y]) + effective_radius
    if side <= 0:
        side = effective_radius * 2 * max(2, shipment.N)
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
    
    # For very small shipments using precalculated patterns, skip compression/optimization
    # to preserve the guaranteed safe spacing
    if shipment.N <= params.small_n_threshold and patterns_smallN and shipment.N in patterns_smallN:
        # Only do a light post-processing, skip aggressive compression
        return layout
    
    # For larger shipments, do full optimization
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
