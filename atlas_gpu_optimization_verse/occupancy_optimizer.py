#!/usr/bin/env python3
"""OccupancyOptimizer - Maximisation utilisation SM Fermi"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class FermiSpecs:
    sm_count: int = 2  # GT 440 typical
    cores_per_sm: int = 32
    max_threads_per_sm: int = 1536
    max_blocks_per_sm: int = 8
    warp_size: int = 32
    shared_mem_per_sm: int = 49152  # 48KB


class OccupancyOptimizer:
    """Optimiseur occupancy pour GPU Fermi CC 2.0"""

    def __init__(self, specs: FermiSpecs = None):
        self.specs = specs or FermiSpecs()

    def calculate_occupancy(self, 
                          threads_per_block: int,
                          shared_mem_per_block: int = 0,
                          registers_per_thread: int = 32) -> dict:
        """Calculer occupancy détaillé Fermi"""
        
        # Limite par threads
        active_threads = min(
            self.specs.max_threads_per_sm,
            threads_per_block * self.specs.max_blocks_per_sm
        )
        
        # Limite par registres (max 32768 registers per SM)
        registers_per_sm = 32768
        blocks_by_regs = registers_per_sm // (registers_per_thread * threads_per_block)
        
        # Limite par shared mem
        blocks_by_shared = self.specs.shared_mem_per_sm // max(shared_mem_per_block, 1)
        
        # Blocks finaux
        blocks_per_sm = min(
            self.specs.max_blocks_per_sm,
            active_threads // threads_per_block,
            blocks_by_regs,
            blocks_by_shared
        )
        
        occupancy = (blocks_per_sm * threads_per_block) / self.specs.max_threads_per_sm
        
        return {
            "occupancy": min(occupancy, 1.0),
            "active_threads": blocks_per_sm * threads_per_block,
            "blocks_per_sm": blocks_per_sm,
            "limiting_factor": self._get_limiting_factor(blocks_by_regs, blocks_by_shared)
        }

    def _get_limiting_factor(self, blocks_by_regs: int, blocks_by_shared: int) -> str:
        limits = []
        if blocks_by_regs < self.specs.max_blocks_per_sm:
            limits.append("registers")
        if blocks_by_shared < self.specs.max_blocks_per_sm:
            limits.append("shared_mem")
        return limits[0] if limits else "threads"

    def find_optimal_config(self, 
                           problem_size: int,
                           min_occupancy: float = 0.8,
                           target_occupancy: float = 0.85) -> dict:
        """Trouver configuration optimale occupancy"""
        
        best_config = None
        best_occupancy = 0
        
        for tpb in [128, 192, 256, 384, 512]:
            if tpb > problem_size and tpb > 512:
                continue
                
            for shared_mem in [0, 1024, 2048, 4096, 8192, 16384]:
                result = self.calculate_occupancy(tpb, shared_mem)
                
                if result["occupancy"] >= min_occupancy and result["occupancy"] > best_occupancy:
                    best_occupancy = result["occupancy"]
                    best_config = {
                        "threads_per_block": tpb,
                        "shared_memory": shared_mem,
                        "occupancy": result["occupancy"],
                        "grid_size": (problem_size + tpb - 1) // tpb
                    }
                    
                    if result["occupancy"] >= target_occupancy:
                        return best_config
        
        return best_config or {"threads_per_block": 256, "occupancy": 0}

    def estimate_performance(self, 
                           operations_per_element: float,
                           total_elements: int,
                           occupancy: float,
                           clock_ghz: float = 1.4) -> dict:
        """Estimer performance Fermi"""
        cores_total = self.specs.sm_count * self.specs.cores_per_sm
        effective_cores = cores_total * occupancy
        
        # FLOPS théoriques Fermi CC 2.0
        theoretical_flops = cores_total * clock_ghz * 2  # 2 ops/cycle FMA
        effective_flops = theoretical_flops * occupancy
        
        time_seconds = (operations_per_element * total_elements) / effective_flops
        
        return {
            "theoretical_gflops": theoretical_flops,
            "effective_gflops": effective_flops,
            "estimated_time_ms": time_seconds * 1000
        }


if __name__ == "__main__":
    opt = OccupancyOptimizer()
    config = opt.find_optimal_config(100000)
    print(f"Optimal config: {config}")