from .unloadModel import DebugMemoryCleanerNode
# from .memory_reset import MemoryResetNode

# Mapeamento estático
NODE_CLASS_MAPPINGS = {
    "DebugMemoryCleaner": DebugMemoryCleanerNode,
    # "MemoryReset": MemoryResetNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DebugMemoryCleaner": "🧹 Debug Memory Cleaner",
    # "MemoryReset": "🚨 Memory Reset (Comfy Flags)",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]
