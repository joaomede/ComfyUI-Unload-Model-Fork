import objgraph
import gc
import sys
import requests

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
any = AnyType("*")

# Tipos-alvo típicos usados por ComfyUI
TARGET_MODEL_TYPES = (
    "CLIP",
    "UNet",
    "VAE",
    "GGUFModelPatcher",
    "TextEncoder",
    "ConditioningEncoder",
    "ControlNet",
    "HierarchicalCache",
)

class DebugMemoryCleanerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"value": (any,)},
            "optional": {"object": (any,)},
        }

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = (any,)
    FUNCTION = "route"
    CATEGORY = "Debug/Memory"

    def route(self, **kwargs):
        value = kwargs.get("value")
        obj = kwargs.get("object")

        # Proteção contra listas vazias causadas por execuções múltiplas
        if isinstance(value, list) and len(value) == 0:
            print("[DEBUG CLEAN] Valor de entrada vazio. Encerrando execução.")
            return (None,)

        print("=" * 60)
        print("[DEBUG CLEAN] Coletando garbage...")
        gc.collect()

        print("[DEBUG CLEAN] Tipos mais comuns vivos:")
        self.log_top_types()

        if obj is not None:
            print("-" * 50)
            print(f"[DEBUG CLEAN] Inspecionando objeto: {type(obj)} | id: {id(obj)}")
            try:
                objgraph.show_backrefs([obj], max_depth=5, too_many=10, output=sys.stdout, shortnames=True)
            except Exception as e:
                print(f"[DEBUG CLEAN] Erro ao mostrar backrefs: {e}")

            print("-" * 50)
            self.nuke_references(obj)
            print("-" * 50)
            print("[DEBUG CLEAN] Tentando desalocar objeto...")
            try:
                del obj
                gc.collect()
            except Exception as e:
                print(f"[DEBUG CLEAN] Erro ao desalocar: {e}")
        else:
            print("[DEBUG CLEAN] Nenhum objeto fornecido. Buscando objetos vivos de tipos conhecidos...")
            matches = []
            for o in gc.get_objects():
                if type(o).__name__ in TARGET_MODEL_TYPES:
                    matches.append(o)

            print(f" - {len(matches)} objeto(s) de tipo(s) alvo encontrados.")
            for i, m in enumerate(matches):
                print(f"   {i+1}) {type(m)} @ {hex(id(m))}")
                self.nuke_references(m)
                del m
            gc.collect()

        print("=" * 60)

        url = "http://127.0.0.1:8188/api/free"
        payload = {
            "free_memory": True,
            "unload_models": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=2)
            print(f"[MEMORY RESET] /free chamado com sucesso (status {response.status_code})")
        except Exception as e:
            print(f"[MEMORY RESET] Falha ao chamar {url}: {e}")

        return (value,)

    def log_top_types(self, limit=10):
        counts = {}
        for obj in gc.get_objects():
            t = type(obj).__name__
            counts[t] = counts.get(t, 0) + 1
        top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        for name, count in top:
            print(f"{name:<30} {count}")

    def nuke_references(self, obj):
        refs = gc.get_referrers(obj)
        print(f"[DEBUG CLEAN] {len(refs)} referências encontradas para {repr(obj)}")
        for ref in refs:
            try:
                if isinstance(ref, dict):
                    for k, v in list(ref.items()):
                        if v is obj:
                            del ref[k]
                elif isinstance(ref, list):
                    while obj in ref:
                        ref.remove(obj)
                elif hasattr(ref, '__dict__'):
                    for attr, val in list(ref.__dict__.items()):
                        if val is obj:
                            setattr(ref, attr, None)
            except Exception as e:
                print(f"[DEBUG CLEAN] Erro ao quebrar referência: {e}")

NODE_CLASS_MAPPINGS = {
    "DebugMemoryCleaner": DebugMemoryCleanerNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DebugMemoryCleaner": "Debug Memory Cleaner",
}
