import objgraph
import tempfile

# Padrão ComfyUI de tipo wildcard
class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False
any = AnyType("*")

class DebugReferencesNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"value": (any,)},  # passthrough
            "optional": {"object": (any,)},  # objeto a ser inspecionado
        }

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    RETURN_TYPES = (any,)
    FUNCTION = "route"
    CATEGORY = "Debug/Memory"

    def route(self, **kwargs):
        obj = kwargs.get("object")
        if obj is None:
            print("[DEBUG REFERENCES] Nenhum objeto fornecido.")
            return (kwargs.get("value"),)

        print("="*40)
        print(f"[DEBUG REFERENCES] Tipo: {type(obj)}")
        try:
            tmpfile = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            objgraph.show_backrefs([obj], max_depth=5, filename=tmpfile.name)
            print(f"[DEBUG REFERENCES] Grafo salvo em: {tmpfile.name}")
        except Exception as e:
            print(f"[DEBUG REFERENCES] Erro ao gerar objgraph: {e}")
        print("="*40)

        return (kwargs.get("value"),)

NODE_CLASS_MAPPINGS = {
    "DebugReferences": DebugReferencesNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DebugReferences": "Debug References (ObjGraph)",
}
