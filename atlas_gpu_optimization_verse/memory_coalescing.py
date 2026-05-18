#!/usr/bin/env python3
"""MemoryCoalescing - Patterns accès mémoire optimisés Fermi"""

import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class CoalescingConfig:
    alignment: int = 128  # bytes, optimal for Fermi
    warp_size: int = 32
    max_threads_per_block: int = 512


class MemoryCoalescing:
    """Optimiseur accès mémoire coalesced pour GPU Fermi"""

    def __init__(self, config: CoalescingConfig = None):
        self.config = config or CoalescingConfig()

    def pad_to_alignment(self, array: np.ndarray, alignment: int = None) -> np.ndarray:
        """Pad array pour alignement optimal"""
        alignment = alignment or self.config.alignment
        current_bytes = array.nbytes
        padded_bytes = ((current_bytes // alignment) + 1) * alignment
        new_shape = (padded_bytes // array.itemsize,)
        
        padded = np.zeros(new_shape, dtype=array.dtype)
        padded[:array.size] = array.flatten()
        return padded

    def coalesce_access(self, data: np.ndarray, stride: int = 1) -> np.ndarray:
        """Réorganiser données pour accès coalescé"""
        if stride == 1:
            return data
        
        # Pour Fermi, coalescer par WARP de 32 threads
        shape = data.shape
        elements_per_thread = np.prod(shape) // self.config.warp_size
        
        # Reorganiser en blocs continus
        coalesced = np.ascontiguousarray(data.reshape(-1))
        return coalesced

    def calculate_occupancy(self, threads_per_block: int, shared_mem_per_block: int) -> float:
        """Calculer occupancy SM Fermi (max 1536 threads par SM)"""
        max_threads_per_sm = 1536
        max_blocks_per_sm = 8
        
        blocks_per_sm = min(
            max_blocks_per_sm,
            max_threads_per_sm // threads_per_block
        )
        occupancy = (blocks_per_sm * threads_per_block) / max_threads_per_sm
        return min(occupancy, 1.0)

    def optimize_kernel_config(self, data_size: int) -> dict:
        """Configuration kernel optimale pour Fermi"""
        # Fermi: 32 CUDA cores par SM, optimal 192-256 threads par bloc
        threads_per_block = min(256, 2 ** int(np.log2(data_size / 4)))
        threads_per_block = max(128, threads_per_block)
        
        blocks = (data_size + threads_per_block - 1) // threads_per_block
        
        return {
            "threads_per_block": threads_per_block,
            "blocks": blocks,
            "shared_memory": 0,
            "occupancy": self.calculate_occupancy(threads_per_block, 0)
        }


if __name__ == "__main__":
    opt = MemoryCoalescing()
    config = opt.optimize_kernel_config(10000)
    print(f"Optimal config: {config}")